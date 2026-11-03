# Sporty-Bara — Contract de date

Ce există în Firestore și ce funcții are serverul. **Ce e scris aici e înțelegerea dintre Erin și Sami**: fiecare construiește pe el fără să aștepte partea celuilalt. Orice schimbare de aici se face prin PR, cu review de la celălalt.

## Reguli generale
- **Monedele sunt numere întregi** (Bara Coins), niciodată zecimale.
- **Cotele sunt zecimale** cu 2 zecimale (`1.85`).
- Timpul: `Timestamp` Firestore (UTC). Afișarea în app se face în ora României.
- Clientul **doar citește**. Soldul, biletele, tranzacțiile, rotirile se scriu **numai** din Cloud Functions.
- Toate funcțiile cer utilizator logat (`request.auth`), în regiunea `europe-west1`.
- Erorile sunt `HttpsError` Firebase, cu codurile de mai jos; în app se citesc din `FirebaseFunctionsException.getCode()`.

## Valori de pornire (propuse, de confirmat)
| Ce | Valoare |
|---|---|
| Sold la înregistrare | 1000 |
| Bonus zilnic | 100 |
| Miză minimă / maximă | 10 / 500 |
| Selecții maxime pe bilet | 10 |
| Rotiri gratuite | 1 / zi + 1 la fiecare 5 bilete |

## Colecții

### `users/{uid}` — privat (doar proprietarul citește)
| Câmp | Tip | Note |
|---|---|---|
| `displayName` | string | |
| `photoUrl` | string \| null | |
| `balance` | int | sold Bara Coins |
| `spinsAvailable` | int | rotiri la roată |
| `ticketsSinceBonusSpin` | int | 0–4, la 5 → +1 rotire |
| `lastDailyClaim` | Timestamp \| null | |
| `cardId` | string \| null | ID Sporty-Bara Card |
| `createdAt` | Timestamp | |

### `profiles/{uid}` — public (orice utilizator logat citește)
| Câmp | Tip | Note |
|---|---|---|
| `displayName`, `photoUrl` | | copie din `users` |
| `rank` | string | `pui`, `balta`, `rau`, `alpha`, `legenda` |
| `badges` | string[] | ID-uri insigne |
| `stats` | map | `{tickets, won, profit}` (int) |

### `matches/{matchId}`
| Câmp | Tip | Note |
|---|---|---|
| `league` | string | `laliga` \| `superliga` |
| `home`, `away` | string | numele echipelor |
| `kickoff` | Timestamp | |
| `status` | string | `scheduled` \| `live` \| `finished` \| `cancelled` |
| `score` | map \| null | `{home: int, away: int}` |
| `bestOdds` | map | `{home: {odd, bookmaker}, draw: {...}, away: {...}}` |
| `fairOdds` | map \| null | cota Sporty-Bara `{home, draw, away}` |
| `verdict` | map \| null | `{home: "fair"\|"low"\|"high", ...}` — „low” = casa o dă prea mică |
| `externalIds` | map | `{oddsApi, apiFootball}` |
| `updatedAt` | Timestamp | |

#### `matches/{matchId}/odds/{bookmaker}`
`{home, draw, away}` (float) + `updatedAt`. Piața: doar 1X2 deocamdată.

#### `matches/{matchId}/factors/{factorId}`
| Câmp | Tip | Note |
|---|---|---|
| `type` | string | `injury`, `suspension`, `lineup`, `referee`, `weather`, `news`, ... |
| `team` | string | `home` \| `away` |
| `player` | string \| null | |
| `playProbability` | float \| null | 0–1 |
| `effect` | map | efectul asupra probabilităților, ex. `{home: -0.03}` |
| `source`, `url` | string | sursa citată de AI |
| `date` | Timestamp | |

### `tickets/{ticketId}`
| Câmp | Tip | Note |
|---|---|---|
| `uid` | string | |
| `selections` | array | `[{matchId, pick: "home"\|"draw"\|"away", odd, bookmaker, result: null\|"won"\|"lost"\|"void"}]` |
| `stake` | int | |
| `totalOdd` | float | produsul cotelor |
| `potentialWin` | int | `floor(stake * totalOdd)` |
| `status` | string | `open` \| `won` \| `lost` \| `void` |
| `createdAt`, `settledAt` | Timestamp | |

Cota folosită la plasare = `bestOdds` din momentul plasării; se salvează pe bilet și nu se mai schimbă.

### `transactions/{txId}` — doar adăugare, niciodată modificare
| Câmp | Tip | Note |
|---|---|---|
| `uid` | string | |
| `amount` | int | + intrare, − ieșire |
| `type` | string | `signup`, `daily`, `stake`, `win`, `refund`, `wheel`, `nfc_out`, `nfc_in` |
| `ref` | string \| null | ID bilet / rotire / token |
| `balanceAfter` | int | |
| `createdAt` | Timestamp | |

### `leagues/{leagueId}` — „bălți”
| Câmp | Tip | Note |
|---|---|---|
| `name` | string | |
| `ownerUid` | string | |
| `inviteCode` | string | 6 caractere |
| `members` | string[] | uid-uri |
| `paillierPublicKey` | string \| null | `n` în zecimal (Sami, #22) |
| `createdAt` | Timestamp | |

`leagues/{leagueId}/keys/{uid}`: `{encryptedPrivateKey}` — cheia ligii criptată pentru fiecare membru (#22).
`league_stats/{leagueId}_{uid}`: `{leagueId, uid, encProfit, encWon, encTotal}` — ciphertext Paillier (string) (#22). `leagueId` și `uid` sunt necesare ca regulile Firestore să verifice că cititorul e membru al ligii.

### `follows/{uid}/following/{otherUid}`
`{createdAt}`

### `wheel_config/current`
`{prizes: [{id, label, type: "coins"|"free_ticket"|"multiplier"|"ai_questions", value, weight}]}` — probabilitatea unui premiu = `weight / suma weight-urilor`.

### `wheel_spins/{spinId}`
`{uid, prizeId, createdAt}`

### `cards/{cardId}`
`{uid, walletObjectId, createdAt}` — același ID folosit în Google Wallet (Erin, #13) și la NFC (Sami, #24).

### `nfc_tokens/{token}` — doar server
`{cardId, uid, expiresAt, used}`

### `pending_factors/{id}` — doar admin
Ca `factors`, plus `matchId`, `status: "pending"|"approved"|"rejected"`.

## Funcții apelabile din app (`callable`)

| Funcție | Cine | Parametri | Răspuns | Erori |
|---|---|---|---|---|
| `ping` | Sami | — | `{ok, uid}` | — |
| `claim_daily` | Erin | — | `{balance, nextClaimAt}` | `failed-precondition` (deja luat azi) |
| `place_ticket` | Erin | `{selections: [{matchId, pick}], stake}` | `{ticketId, totalOdd, potentialWin, balance}` | `invalid-argument`, `failed-precondition` (meci început / sold insuficient) |
| `edit_ticket` | Erin | `{ticketId, selections, stake}` | ca `place_ticket` | ca mai sus + `not-found`, `permission-denied` |
| `delete_ticket` | Erin | `{ticketId}` | `{balance}` | `not-found`, `permission-denied`, `failed-precondition` |
| `spin_wheel` | Erin | — | `{prize, balance, spinsAvailable}` | `failed-precondition` (fără rotiri) |
| `create_league` | Erin | `{name}` | `{leagueId, inviteCode}` | `invalid-argument` |
| `join_league` | Erin | `{inviteCode}` | `{leagueId}` | `not-found` |
| `follow` / `unfollow` | Erin | `{uid}` | `{ok}` | `not-found` |
| `create_wallet_pass` | Erin | — | `{saveUrl}` | `internal` |
| `ai_explain` | Sami | `{matchId, question}` | `{answer, sources: [{title, url}]}` | `resource-exhausted` (limită întrebări) |
| `nfc_token` | Sami | — | `{token, expiresAt}` | — |
| `nfc_charge` | Sami | `{token, amount}` | `{txId, balance}` | `not-found`, `deadline-exceeded` (token expirat), `failed-precondition` |

## Funcții automate (server)

| Funcție | Cine | Când | Ce face |
|---|---|---|---|
| `init_user` | Erin | la creare cont (Auth) | `users` + `profiles` + sold inițial + tranzacție `signup` |
| `fetch_odds` | Sami | programat (~6 h) | cote → `matches` + `odds` + `bestOdds` |
| `fetch_results` | Sami | programat în zilele cu meciuri | `status` + `score` |
| `settle_tickets` | Erin | când un meci devine `finished` | decontare bilete + `win` + rotire bonus |
| `compute_fair_odds` | Sami | după `fetch_odds` / factori noi | `fairOdds` + `verdict` |
| `scout` | Sami | programat | factori → `pending_factors` |
| `update_wallet_pass` | Erin | la schimbarea soldului | soldul de pe pass |
| `notify` | Sami | bilet decontat, invitație | FCM |

## Date de test
Până sunt gata `fetch_odds` și `fetch_results`, Erin pune în emulator meciuri de test cu forma de mai sus (`matches` cu `bestOdds`), ca să poată lucra la bilete.

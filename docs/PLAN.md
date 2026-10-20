# Sporty-Bara — Plan proiect

**Autori:** Savu Mihai-Samuel · Ludoșan Erin-Andreea
**Ultima actualizare:** 20-10-2026

## Ce este
Aplicație Android pentru urmărirea pariurilor sportive **fără bani reali**:
- compară cotele mai multor case de pariuri pentru același meci și evidențiază cea mai bună cotă;
- calculează o **cotă proprie** (date echipe + cote din piață + modele matematice + AI) și arată dacă o casă dă o cotă prea mică / prea mare;
- joc cu **monedă virtuală** (Bara Coins): bilete, rezultate, clasament, ligi private, social;
- **asistent AI** care explică pe înțeles de ce o cotă merită sau nu;
- **Roata de premii**: rotiri gratuite (zilnic + bonus la bilete plasate), premii doar virtuale;
- **Sporty-Bara Card**: card virtual în Google Wallet + plată prin NFC între telefoane, doar cu monedă virtuală.

## Reguli de bază
- Monedele **nu se cumpără și nu se retrag** — se obțin doar din joc (bonus înregistrare, bonus zilnic, pariuri câștigate, roata de premii). Fără valoare bănească.
- Rotirile la roată **nu se cumpără**; rezultatul e tras pe server (RNG sigur).
- Cheile API (cote, AI) stau **doar pe server**, niciodată în aplicație.
- Toate operațiile cu monede sunt validate pe server (clientul nu modifică soldul direct).
- Cardul NFC folosește un **AID propriu Sporty-Bara**, nu emulează Visa/Mastercard. La un POS bancar real nu e recunoscut → plata e respinsă.

## Tehnologii
| Zonă | Tehnologie |
|---|---|
| App | Android nativ, **Java + XML Views**, Material 3, minSdk 26 |
| Login | Firebase Auth (email + Google) |
| Bază de date | Cloud Firestore |
| Backend | Cloud Functions for Firebase (2nd gen) în **Python** — plan **Blaze** necesar pentru apeluri externe |
| Cote + date | **The Odds API** (cote) + **API-Football** (rezultate, accidentări, echipe) — ambele free |
| Statistici | Understat (xG), ClubElo, football-data.co.uk, `soccerdata`; vreme Open-Meteo |
| Scout | Python + Playwright (adaptat din motorul de leads), RSS știri |
| AI | **Claude Haiku 5.5** (SDK `anthropic`), apelat doar din Cloud Functions |
| Notificări | Firebase Cloud Messaging |
| Wallet | Google Wallet API (Generic / Loyalty pass) |
| NFC | Android HCE (Host Card Emulation) cu AID propriu + mod „terminal” în aplicație |
| Criptare omomorfă | Paillier — `phe` (Python, server) + `javallier` (Java, app), compatibile |

## Design
Totul e **capybara-themed** (mascota Bara, Profesorul Bara, Bara Coins, ranguri capibara, ligi = „bălți”).
Planul complet de design — culori, fonturi, componente, ecrane, asset-uri — e în **[DESIGN.md](DESIGN.md)** (îl întreține Erin).

## Etape

### 0. Fundație
- [x] Repo GitHub + schelet Android Java
- [ ] Proiect Firebase (Auth, Firestore, Functions, FCM) + `google-services.json` (necomis)
- [ ] Structura Firestore: `users`, `matches`, `odds`, `tickets`, `leagues`, `follows`, `transactions`
- [ ] Reguli de securitate Firestore

### 1. Conturi
- [ ] Înregistrare / login (email + Google)
- [ ] Profil (nume, avatar)
- [ ] Sold inițial de monede + bonus zilnic (Cloud Function)

### 2. Cote
- [ ] Funcție Python programată: aduce cotele din API → Firestore
- [ ] Ecran listă meciuri (pe ligi / zile)
- [ ] Ecran meci: cotele caselor una lângă alta, cea mai bună evidențiată

### 3. Bilete
- [ ] Creare bilet (selecții + miză în monede)
- [ ] Modificare / ștergere bilet (înainte de start meci)
- [ ] Decontare automată după rezultat (Cloud Function)
- [ ] Istoric + statistici personale

### 4. Cota proprie
**Principiu:** cota o calculează un **model matematic** în Python; AI-ul doar transformă știrile în date structurate și explică rezultatul — nu inventează cote.

- [ ] Probabilități „corecte” din piață (eliminarea marjei caselor)
- [ ] Model de bază: Poisson / Dixon-Coles pe goluri + xG (Understat) + Elo (ClubElo)
- [ ] Date istorice pentru antrenare/testare: football-data.co.uk (rezultate + cote istorice), biblioteca `soccerdata`
- [ ] Ajustări din factori (vezi tabelul de mai jos) → **cota Sporty-Bara**
- [ ] Indicator în UI: corectă / prea mică / prea mare
- [ ] **Backtest**: modelul vs. cotele caselor pe sezoanele trecute
- [ ] **Testăm statistic ipotezele** (inclusiv cele „mit”, ex. ziua de naștere) — păstrăm doar factorii cu efect dovedit pe date

#### Factori care pot modifica o cotă
| Nivel | Factori |
|---|---|
| **Mare (dovedit)** | accidentări/suspendări jucători cheie (pondere în xG+xA), portar titular lipsă, executant penalty/faze fixe lipsă, rotație înaintea unui meci mai important, meci fără public / sancțiuni stadion, mișcarea cotelor în piață |
| **Mediu (real)** | arbitru (cartonașe, penalty-uri), vreme (ploaie, vânt, căldură, zăpadă), altitudine, distanță deplasare + fus orar, gazon sintetic, oboseală (zile odihnă, minute jucate, pauza echipelor naționale), motivație (retrogradare, titlu, meci fără miză), derby, antrenor nou, jucători la limita suspendării |
| **Mic / de testat** | ziua de naștere a jucătorului, evenimente personale, Ramadan, probleme financiare la club, ora de start |

#### Scout — motor de căutare factori (adaptat din motorul de leads)
- [ ] Căutări automate per meci (accidentări, echipe probabile, arbitru, știri) în Google News, RSS (Marca, AS, Mundo Deportivo, BBC Sport, GSP), Transfermarkt, FotMob
- [ ] Surse structurate: API-Football `/injuries`, `/fixtures/lineups`; vreme din Open-Meteo
- [ ] Deduplicare după URL / hash text
- [ ] AI extrage factorii în JSON: `{jucator, echipa, status, probabilitate_joaca, sursa, data}`
- [ ] Pas de revizuire umană: `pending_factors.json` → verificat → aplicat în model
- [ ] Cereri rare + cache (fără încărcarea site-urilor)

### 5. Social
- [ ] Clasament general
- [ ] Ligi private (cod de invitație)
- [ ] **Clasament omomorf în ligi private (Paillier)** — vezi mai jos
- [ ] Follow jucători + vezi biletele lor
- [ ] Bilete în grup

#### Clasament omomorf (ligi private)
Scop: statisticile de clasament ale unei ligi (profit, rata de câștig, număr bilete) sunt **stocate și agregate criptat** — serverul le calculează fără să le cunoască valorile.
- [ ] La crearea ligii, aplicația creatorului generează perechea de chei Paillier a ligii
- [ ] Cheia publică → Firestore (`leagues/{id}`); cheia privată → trimisă fiecărui membru criptată cu cheia lui (RSA din Android Keystore)
- [ ] `settle_tickets`: rezultatul biletului se criptează cu cheia publică a ligii, plaintext-ul nu se salvează în statisticile ligii
- [ ] Serverul adună omomorf: profit total, nr. bilete câștigate / totale per membru (doar ciphertext în `league_stats`)
- [ ] App-ul membrilor decriptează (javallier) și **ordonează local** clasamentul
- [ ] Limitare asumată: serverul cunoaște soldul și biletele (necesar pentru decontare); ce e protejat sunt statisticile agregate ale ligii. Ordonarea criptată pe server (FHE) — doar ca extindere viitoare.
- [ ] Clasamentul general rămâne necriptat

### 5b. Roata de premii
- [ ] 1 rotire gratuită / zi + 1 rotire bonus la fiecare 5 bilete plasate
- [ ] Premii: monede, bilet gratuit, multiplicator câștig, întrebări extra la AI
- [ ] `spin_wheel` pe server (RNG sigur, probabilități configurabile în Firestore)
- [ ] Animație roată în app (rezultatul vine de la server)
- [ ] Istoric rotiri

### 6. Consultant AI (chat)
- [ ] Ecran meci: cota casei vs. cota Sporty-Bara + verdict (ex. „casa o dă prea mică”)
- [ ] Chat „de ce?”: AI-ul primește **doar** datele calculate de noi (factori + surse, xG, Elo, efectul fiecărui factor) și explică pe înțeles
- [ ] AI-ul citează sursele; dacă nu are informația, spune asta — nu inventează factori
- [ ] Prin Cloud Function (cheia doar pe server) + limită de cereri pe utilizator

### 7. Sporty-Bara Card (Wallet + NFC)
- [ ] Generare card virtual per utilizator (ID card, legat de cont)
- [ ] Buton „Adaugă în Google Wallet” (pass cu nume, sold, QR) + actualizare sold de pe server
- [ ] Ecran **„Plătește”** în aplicație: afișează **același card** ca în Wallet (design, ID, sold) și pornește tap-ul NFC
- [ ] Notă: Google Wallet face NFC doar pentru carduri bancare reale → tap-ul pornește din aplicația Sporty-Bara; din Wallet se plătește prin QR
- [ ] HCE: telefonul se comportă ca un card Sporty-Bara (AID propriu)
- [ ] Mod „terminal” în aplicație: alt telefon citește cardul la tap și cere plata în monede
- [ ] Validare + transfer pe server, tranzacție semnată, protecție la replay
- [ ] Rezervă: plată prin scanarea QR-ului din Wallet
- [ ] Test: la un POS bancar real cardul nu e recunoscut → respins

### 8. Notificări + finisare
- [ ] Notificări: bilet câștigat/pierdut, meci început, invitație în ligă
- [ ] Polish UI, testare, pregătire prezentare

## Mod demo (pentru prezentare)
La prezentare s-ar putea să nu fie meciuri live → avem nevoie de date controlate.
- [ ] **Seed data**: un weekend de meciuri salvat (cote, factori, rezultate) încărcat în Firestore
- [ ] **Replay**: „derulăm” timpul — meciurile încep / se termină la comandă, biletele se decontează pe loc
- [ ] Conturi demo cu sold, bilete, ligă, insigne deja făcute
- [ ] Scenariu Yamal: arătăm cum cota se schimbă când apare o accidentare

## Infrastructură & calitate
- [ ] **Git**: `main` stabil, lucrăm pe `feature/...`, Pull Request + review între noi
- [ ] **CI GitHub Actions**: build + teste la fiecare PR (`./gradlew assembleDebug test`) + teste Python (`pytest`)
- [ ] **Firebase Emulator Suite** pentru dezvoltare locală (Auth, Firestore, Functions) — fără costuri, fără date reale
- [ ] **Teste**: unit pe model (Python), pe decontare bilete, pe roată (distribuția premiilor), pe NFC (token, replay)
- [ ] **Firebase App Check** (doar aplicația noastră poate apela funcțiile)
- [ ] Reguli Firestore testate cu emulatorul
- [ ] Limită de cheltuieli în Anthropic Console + alerte de buget în Google Cloud
- [ ] Crashlytics pentru erori din aplicație

## Siguranță, legal, confidențialitate
- [ ] Mesaj clar în app: **„Fără bani reali. Monedele nu au valoare și nu se pot retrage.”**
- [ ] Secțiune „Joc responsabil” cu linkuri de ajutor (aplicația e despre pariuri, chiar dacă virtuale)
- [ ] Politică de confidențialitate minimă (ce date stocăm: email, nume, bilete) + ștergere cont
- [ ] Scraping: cereri rare, cache, respectăm `robots.txt`; doar pentru proiectul de facultate

## Ce ne trebuie fizic / conturi
- [ ] **2 telefoane Android cu NFC** — emulatorul **nu** suportă HCE, testarea plăților cere telefoane reale
- [ ] Cont Firebase / Google Cloud (plan Blaze, card)
- [ ] Cont **Google Pay & Wallet Console** (emitent de pass-uri) — în modul demo, pass-urile merg pe conturile de test adăugate de noi
- [ ] Cheie The Odds API, cheie API-Football, cont Anthropic (~$5 credit)

## Documentație (pentru facultate)
- [ ] Diagrama arhitecturii + fluxuri (bilet, plată NFC, clasament omomorf)
- [ ] Descrierea modelului de cotă + rezultatele backtest-ului
- [ ] Rezultatele testării ipotezelor (ce factori contează cu adevărat)
- [ ] Manual de utilizare + capturi de ecran

## De decis
- [x] API cote: **The Odds API** (free, ~500 credite/lună) + **API-Football** (free, 100 cereri/zi) pentru rezultate, accidentări, echipe
- [x] Ligi: **La Liga (Spania)** + **Superliga României** (maxim 2, ca să rămânem în creditele gratuite: ~8 credite/zi ≈ 240/lună)
  - [ ] De verificat cu `/v4/sports` (0 credite) dacă The Odds API acoperă Superliga; dacă nu → cote RO din API-Football
  - Superliga nu are xG în Understat → modelul RO merge pe goluri reale + Elo
- [x] API AI: **Claude Haiku 5.5** (`claude-haiku-5-5`) — structured outputs pt. Scout, Batch API (-50%) pt. extragere; ~$5 credit acoperă proiectul; spend limit în Console
- [ ] Împărțirea muncii (cine pe ce etapă)
- [ ] Termene / data predării
- [ ] Cine desenează mascota Bara / asset-urile
- [ ] Limba aplicației: doar RO sau RO + EN

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
| Cote | API extern (de ales, ex. The Odds API) |
| AI | API LLM extern, apelat doar din Cloud Functions |
| Notificări | Firebase Cloud Messaging |
| Wallet | Google Wallet API (Generic / Loyalty pass) |
| NFC | Android HCE (Host Card Emulation) cu AID propriu + mod „terminal” în aplicație |
| Criptare omomorfă | Paillier — `phe` (Python, server) + `javallier` (Java, app), compatibile |

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
- [ ] Eliminarea marjei caselor (probabilități „corecte” din piață)
- [ ] Model statistic pe echipe (ex. Poisson pe goluri / Elo)
- [ ] Combinare cu AI → cotă Sporty-Bara
- [ ] Indicator în UI: corectă / prea mică / prea mare

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

### 6. Asistent AI
- [ ] Chat „de ce merită / nu merită cota asta” (prin Cloud Function)
- [ ] Limită de cereri pe utilizator

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

## De decis
- [ ] API-ul de cote (ce ligi / case de pariuri acoperă, limite gratuite)
- [ ] API-ul de AI
- [ ] Împărțirea muncii (cine pe ce etapă)
- [ ] Termene / data predării

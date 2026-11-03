# Plan Erin

Partea ta: **design + conturi + bilete + roata + clasament/bălți + Google Wallet + mod demo**, fiecare **cap la coadă** (ecran Java/XML + funcția Python + teste).

Începi cu **#1 (Firebase)** — de el depinde și Sami. În paralel poți face design-ul (#2–#4).
Pentru bilete nu trebuie să aștepți cotele lui Sami: pui meciuri de test în emulator (vezi `docs/API.md` → Date de test).

**Legături cu Sami:** biletele folosesc `bestOdds` din `matches` (#18); clasamentul din bălți primește criptarea Paillier (#22); cardul din Wallet are același `cardId` ca plata NFC (#24).

Ordinea de lucru (bifează în issue, se închide automat la merge-ul PR-ului cu `Closes #N`):


### 0. Fundație
- [ ] [#1 Creare proiect Firebase](https://github.com/Sami111-Afk/Sporty-Bara/issues/1)

### Design
- [ ] [#2 Design: finalizare DESIGN.md](https://github.com/Sami111-Afk/Sporty-Bara/issues/2)
- [ ] [#3 Mascota Bara + iconița aplicației](https://github.com/Sami111-Afk/Sporty-Bara/issues/3)
- [ ] [#4 Tema Android: culori, font, componente de bază](https://github.com/Sami111-Afk/Sporty-Bara/issues/4)

### 1. Conturi
- [ ] [#5 Onboarding + Login / Înregistrare](https://github.com/Sami111-Afk/Sporty-Bara/issues/5)
- [ ] [#6 Profil + sold inițial + bonus zilnic](https://github.com/Sami111-Afk/Sporty-Bara/issues/6)

### 3. Bilete
- [ ] [#7 Bilete: slip + plasare bilet](https://github.com/Sami111-Afk/Sporty-Bara/issues/7)
- [ ] [#8 Bilete: modificare, ștergere, istoric](https://github.com/Sami111-Afk/Sporty-Bara/issues/8)
- [ ] [#9 Decontare automată bilete](https://github.com/Sami111-Afk/Sporty-Bara/issues/9)

### 5. Social + Roata
- [ ] [#10 Roata de premii](https://github.com/Sami111-Afk/Sporty-Bara/issues/10)
- [ ] [#11 Clasament general + ranguri](https://github.com/Sami111-Afk/Sporty-Bara/issues/11)
- [ ] [#12 Bălți (ligi private) + follow](https://github.com/Sami111-Afk/Sporty-Bara/issues/12)

### 7. Card
- [ ] [#13 Card: design + Google Wallet](https://github.com/Sami111-Afk/Sporty-Bara/issues/13)

### 8. Final
- [ ] [#14 Mod demo + manual de utilizare](https://github.com/Sami111-Afk/Sporty-Bara/issues/14)

Vezi și: [PLAN.md](PLAN.md) · [API.md](API.md) · [DESIGN.md](DESIGN.md) · [CONTRIBUTING.md](../CONTRIBUTING.md)

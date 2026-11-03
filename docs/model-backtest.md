# Model cotă proprie — raport backtest

Parte din issue #20 (modelul de bază; factorii de știri nu sunt incluși). Toate cifrele de mai jos provin din rularea reală a
`functions/tools/backtest.py` pe datele descărcate pe 03-11-2026.

## Date

Sursă: [football-data.co.uk](https://www.football-data.co.uk) (CSV-uri descărcate în cache-ul local `functions/.data/`, necomis).

| Ligă | Fișier | Perioadă încărcată | Perioadă evaluată (test) |
|---|---|---|---|
| La Liga | `mmz4281/{SSSS}/SP1.csv`, sezoanele 2021/22 – 2026/27 | 2021/22 – 2026/27 (parțial) | 12-08-2022 – 02-11-2026 (sezoanele 2022/23, 2023/24, 2024/25, 2025/26 complete + 2026/27 parțial), **1629 meciuri** |
| Superliga României | `new/ROU.csv` (toate sezoanele, coloana `Season`) | 2012/13 – 2026/27 (parțial) | 15-07-2022 – 02-11-2026 (idem), **1390 meciuri** |

Formatele diferă: SP1 are `HomeTeam, AwayTeam, FTHG, FTAG` + cote `AvgH/MaxH` (deschidere) și `AvgCH/MaxCH` (închidere); ROU are
`Home, Away, HG, AG, Season` + doar cote de închidere (`AvgCH/MaxCH`, `PSCH`...). Datele sunt `dd/mm/yyyy`. Parserul
(`sportybara/model/data.py`) normalizează ambele formate și folosește **cotele de închidere** când există (pentru comparație corectă între ligi).

**Piața** = cotele medii (`AvgC*`) fără marjă (metoda proporțională din `odds.fair_probabilities`).
Toate metricile sunt calculate pe același set de meciuri (cele care au cote medii; în testul final toate meciurile le aveau).

## Modele

- **Poisson (Dixon–Coles simplificat)**: atac/apărare pe echipă + avantaj teren propriu, maximum likelihood cu ponderare în timp
  `exp(-xi · vechime)`, `xi = ln2/365` (timp de înjumătățire 1 sezon), doar ultimii 4 ani, penalizare L2 mică (`reg = 1`).
  Corecția `rho` pentru scoruri mici se estimează într-un pas separat, după ratele Poisson (simplificare față de varianta completă).
  Echipele fără istoric (promovate) primesc media ligii. Matrice de scor până la 10 goluri → 1X2.
- **Elo**: K = 20, avantaj teren 75 puncte, start 1500, multiplicator `1 + ln(diferență de goluri)` la diferențe > 1.
  Probabilități 1X2 printr-un model „ordered logit” pe diferența de rating, ai cărui doi parametri (scară, prag de egal) se recalibrează
  la fiecare etapă pe meciurile deja văzute.
- **Poisson+Elo**: medie ponderată 0.65 / 0.35. **Combinat (cu piață)**: Poisson 0.35, Elo 0.15, piață 0.50.
  Ponderile au fost fixate dinainte, **nu** optimizate pe datele de test.
- Piața: cotele medii de închidere fără marjă.

## Metodologie: walk-forward

Meciurile din perioada de test se grupează în etape (blocuri de maxim 7 zile de la primul meci al blocului). Pentru fiecare bloc,
Poisson se re-antrenează și Elo se actualizează **doar cu meciuri cu data strict mai mică decât începutul blocului**; apoi se prezic
meciurile blocului. Nu există scurgere de informație din viitor (există test automat care schimbă rezultatele viitoare și verifică
că predicțiile anterioare rămân identice). Perioada dinaintea testului (de la 2021/22 la La Liga, de la 2012/13 la România) servește doar ca istoric.

Metrici: **log loss** (mai mic = mai bine; un model care dă 1/3 oricărui rezultat are ln 3 ≈ 1.0986), **Brier** (suma pătratelor erorilor pe cele 3 rezultate, mai mic = mai bine), **acuratețea** rezultatului cel mai probabil.

## Rezultate — La Liga (1629 meciuri)

| Model | Log loss | Brier | Acuratețe |
|---|---|---|---|
| Poisson | 0.9781 | 0.5813 | 53.3% |
| Elo | 0.9771 | 0.5807 | 54.0% |
| Poisson+Elo | 0.9753 | 0.5795 | 53.5% |
| Combinat (cu piață) | 0.9627 | 0.5713 | 54.1% |
| **Piață (cote medii, fără marjă)** | **0.9562** | **0.5672** | **55.1%** |

Log loss pe sezon:

| Sezon | Meciuri | Poisson | Elo | Poisson+Elo | Combinat | Piață |
|---|---|---|---|---|---|---|
| 2022/2023 | 380 | 1.0098 | 1.0045 | 1.0057 | 0.9880 | 0.9778 |
| 2023/2024 | 380 | 0.9634 | 0.9605 | 0.9603 | 0.9519 | 0.9498 |
| 2024/2025 | 380 | 0.9728 | 0.9735 | 0.9712 | 0.9560 | 0.9462 |
| 2025/2026 | 380 | 0.9788 | 0.9807 | 0.9759 | 0.9678 | 0.9650 |
| 2026/2027 (parțial) | 109 | 0.9346 | 0.9394 | 0.9336 | 0.9177 | 0.9072 |

## Rezultate — Superliga României (1390 meciuri)

| Model | Log loss | Brier | Acuratețe |
|---|---|---|---|
| Poisson | 1.0336 | 0.6206 | 47.1% |
| Elo | 1.0327 | 0.6199 | 47.3% |
| Poisson+Elo | 1.0313 | 0.6190 | 46.8% |
| Combinat (cu piață) | 1.0175 | 0.6097 | 48.8% |
| **Piață (cote medii, fără marjă)** | **1.0112** | **0.6057** | **49.9%** |

| Sezon | Meciuri | Poisson | Elo | Poisson+Elo | Combinat | Piață |
|---|---|---|---|---|---|---|
| 2022/2023 | 321 | 1.0166 | 1.0207 | 1.0156 | 1.0045 | 1.0008 |
| 2023/2024 | 321 | 1.0530 | 1.0520 | 1.0513 | 1.0343 | 1.0255 |
| 2024/2025 | 315 | 1.0595 | 1.0478 | 1.0543 | 1.0384 | 1.0279 |
| 2025/2026 | 321 | 1.0374 | 1.0323 | 1.0332 | 1.0235 | 1.0223 |
| 2026/2027 (parțial) | 112 | 0.9426 | 0.9708 | 0.9488 | 0.9304 | 0.9204 |

## Simulare de pariere „value”

Regulă: pariu fix de 1 unitate pe un rezultat când **cota MAX** din piață (cea mai bună cotă dintre case) este mai mare decât
cota noastră × (1 + prag). Se pot face mai multe pariuri pe același meci. Referință: pariind pe toate cele 3 rezultate la cota max,
ROI = **−4.1%** (La Liga, 4887 pariuri) și **−3.1%** (România, 4170 pariuri) — marja cotelor max.

**La Liga**

| Prag | Cota noastră din | Pariuri | Câștigate | Profit | ROI |
|---|---|---|---|---|---|
| 0% | Poisson+Elo | 2220 | 667 | -150.3 | -6.8% |
| 5% | Poisson+Elo | 1656 | 460 | -104.9 | -6.3% |
| 10% | Poisson+Elo | 1227 | 308 | -109.0 | -8.9% |
| 20% | Poisson+Elo | 664 | 130 | -121.3 | -18.3% |
| 0% | Combinat (cu piață) | 2220 | 629 | -155.8 | -7.0% |
| 5% | Combinat (cu piață) | 1271 | 298 | -139.5 | -11.0% |
| 10% | Combinat (cu piață) | 760 | 137 | -156.6 | -20.6% |
| 20% | Combinat (cu piață) | 262 | 44 | -13.0 | -5.0% |

**Superliga României**

| Prag | Cota noastră din | Pariuri | Câștigate | Profit | ROI |
|---|---|---|---|---|---|
| 0% | Poisson+Elo | 1714 | 508 | -89.1 | -5.2% |
| 5% | Poisson+Elo | 1251 | 347 | -91.0 | -7.3% |
| 10% | Poisson+Elo | 946 | 239 | -105.7 | -11.2% |
| 20% | Poisson+Elo | 532 | 127 | -26.7 | -5.0% |
| 0% | Combinat (cu piață) | 1573 | 444 | -70.7 | -4.5% |
| 5% | Combinat (cu piață) | 927 | 225 | -82.4 | -8.9% |
| 10% | Combinat (cu piață) | 567 | 123 | -43.2 | -7.6% |
| 20% | Combinat (cu piață) | 200 | 38 | -5.9 | -3.0% |

## Concluzii

1. **Piața bate modelul, în ambele ligi și în fiecare sezon testat.** Log loss-ul pieței este cel mai mic peste tot (La Liga 0.9562 vs 0.9753 pentru Poisson+Elo; România 1.0112 vs 1.0313), la fel Brier și acuratețea. Era de așteptat: cotele de închidere încorporează informație pe care modelul nu o are (formă recentă, accidentări, loturi, mișcări de bani).
2. **Poisson și Elo sunt la același nivel** (diferențe de ordinul 0.001 în log loss); combinația lor e puțin mai bună decât fiecare separat. Modelul e totuși mai bun decât a ghici (ln 3 ≈ 1.0986), deci prinde semnal real din rezultate.
3. **Combinarea cu piața nu bate piața** (0.9627 vs 0.9562 la La Liga; 1.0175 vs 1.0112 în România): amestecul cu un model mai slab nu adaugă informație utilă în această formă.
4. **Nu există „value” exploatabil.** Toate simulările de pariere au ROI negativ, de la −3.0% până la −20.6%; nicio configurație nu iese pozitiv. ROI-ul nu se îmbunătățește monoton cu pragul (zgomot statistic: la praguri mari sunt puține pariuri, 200–260), deci diferențele dintre praguri nu sunt interpretabile. Datele nu arată că dezacordul modelului cu piața ar indica o cotă greșită a casei.
5. **Concluzie pentru produs:** în Sporty-Bara, cota proprie nu trebuie prezentată ca „mai bună decât piața”. Ca verdict (`fair`/`low`/`high`), cota noastră în forma actuală arată mai degrabă cât de mult se abate piața de la un model simplu bazat pe rezultate; varianta mai sigură este să ancorăm cota proprie pe piața fără marjă și să o ajustăm doar cu factori verificați statistic.

## Limitări

- Doar rezultate și goluri; fără xG, accidentări, loturi, vreme, motivație.
- Echipele promovate / necunoscute pornesc de la media ligii (în realitate sunt de regulă sub medie); Elo pornește de la 1500 pentru echipe noi.
- Superliga României și-a schimbat formatul în perioada încărcată (play-off/play-out, număr diferit de echipe); modelul nu ține cont de asta.
- Cotele max sunt cele de închidere, culese ulterior: o parte din ele nu ar fi putut fi obținute efectiv la momentul pariului; ROI-ul real ar fi, probabil, și mai slab.
- Ponderile combinării, K-ul Elo, `xi` și `reg` sunt valori alese a priori, neoptimizate (evită supra-ajustarea pe test, dar pot fi suboptime).
- 2026/27 este sezon parțial (aprox. 110 meciuri pe ligă); numerele lui au varianță mare.

## Ce ar putea îmbunătăți modelul

- **xG** (Understat/FBref) în locul golurilor brute: semnal mult mai puțin zgomotos pentru forța echipei.
- **Factorii de știri** (accidentări, suspendări, portar titular, rotații) — separat, în continuarea issue-ului #20; singurul tip de informație care poate aduce ceva față de piață, dar trebuie validat cu același backtest.
- Estimarea comună a `rho` în verosimilitate, optimizarea (pe sezoane anterioare, nu pe test) a lui `xi`, `reg` și a ponderilor.
- Prior pentru echipele promovate, tratarea separată a fazelor play-off/play-out în România.

## Cum se rulează

```
cd functions
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt pytest
.venv/bin/python tools/backtest.py --league all      # descarcă CSV-urile în functions/.data/ la prima rulare
.venv/bin/python -m pytest -q tests
```

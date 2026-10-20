# Sporty-Bara — Plan de design 🦫

> **Status: propunere / ciornă.** Erin modifică liber orice de aici — culori, mascota, ecrane, nume.
> Ce se schimbă aici se reflectă apoi în `app/src/main/res/values/colors.xml`, `themes.xml` și layout-uri.

## 1. Idee și ton
- Totul e **capybara-themed** (Sporty-**Bara**).
- Capibara e calmă și prietenoasă cu toată lumea → tonul aplicației: **pariuri fără stres, fără bani reali**, totul e un joc.
- Texte scurte, cu umor ușor („Bara zice: cota asta e cam mică 🍊”), niciodată agresive („PARIAZĂ ACUM!”).
- Nimic din aplicație nu trebuie să arate a cazino real: fără roșu-auriu strident, fără „jackpot”.

## 2. Mascota: Bara
Capibara cu o **portocală (yuzu) pe cap**.

| Poză / stare | Unde apare |
|---|---|
| Bara zâmbește, salută | onboarding, ecran de login |
| Bara sărbătorește, portocala sare | bilet câștigat, insignă nouă, rang nou |
| Bara stă în apă, liniștită | bilet pierdut („se mai întâmplă”) |
| Bara înoată | încărcare (animație) |
| Bara doarme pe iarbă | ecran gol (fără bilete, fără ligi) |
| Bara confuză, cu semn de întrebare | eroare / fără internet |
| Bara învârte roata | roata de premii |
| **Profesorul Bara** — ochelari, carte | consultantul AI (chat) |
| Bara cu cardul în lăbuțe | ecran Card / Plătește |

**De decis (Erin):** stilul desenului (flat / 3D / desenat de mână), cine îl desenează, câte poze facem în prima versiune.

## 3. Culori
Valori propuse, **contrastul verificat** (WCAG: ≥ 4.5 pentru text normal).

### Light
| Rol | Culoare | Folosire | Contrast |
|---|---|---|---|
| Fundal | `#F5E6D3` crem | fundalul ecranelor | — |
| Text principal | `#3E2A1E` maro închis | tot textul | 11.0 pe crem ✅ |
| Primar | `#8B5E3C` maro capibara | bară de sus, butoane principale | 4.55 pe crem ✅, text alb pe el 5.58 ✅ |
| Accent | `#F39C12` portocaliu yuzu | monede, butoane secundare, roata | **doar ca fundal**, cu text maro închis (6.16 ✅) |
| Câștig | `#1E6B2A` verde | text „câștigat”, cota cea mai bună | 5.37 ✅ |
| Pierdere | `#A93226` roșu cărămidă | text „pierdut” | 5.41 ✅ |

⚠️ **Portocaliul nu se folosește ca text** (1.79 pe crem ❌) și **nu pui text alb pe portocaliu** (2.19 ❌).

### Dark — „onsen noaptea”
| Rol | Culoare | Contrast |
|---|---|---|
| Fundal | `#2B1D14` maro foarte închis | — |
| Text | `#F5E6D3` crem | 13.3 ✅ |
| Primar | `#D7B899` maro deschis | 8.7 ✅ |
| Accent | `#F39C12` portocaliu | 7.43 ✅ |
| Câștig | `#81C784` | 8.1 ✅ |
| Pierdere | `#EF9A9A` | 7.57 ✅ |

## 4. Fonturi
- Font rotunjit, prietenos: **Nunito** sau **Baloo 2** (Google Fonts, gratuite) — de ales.
- Cifrele (cote, monede) cu cifre de lățime egală (`tnum`), ca să nu „sară” când se schimbă cota.
- Mărimi: titlu 24sp, subtitlu 18sp, text 16sp, mic 13sp. Respectăm mărirea fontului din setările telefonului.

## 5. Componente
| Componentă | Descriere |
|---|---|
| **Card meci** | echipele + ora, cota casei vs. cota Sporty-Bara, insignă „casa o dă prea mică / mare” |
| **Comparator cote** | rânduri cu fiecare casă, cea mai bună cotă evidențiată cu verde + 🍊 |
| **Bilet (slip)** | panou care urcă de jos cu selecțiile, miza în Bara Coins, câștig posibil |
| **Bara Coin** | monedă portocalie cu fața capibarei, lângă orice sumă |
| **Roata** | felii de portocală, fiecare cu un premiu |
| **Sporty-Bara Card** | card cu Bara, numele jucătorului, sold, ID — același design în app și în Google Wallet |
| **Rang** | insignă cu nivelul de capibara |
| **Insigne** | cerculețe colecționabile pe profil |
| **Chat Profesorul Bara** | bule de chat, Bara cu ochelari ca avatar, surse citate sub răspuns |

## 6. Ranguri și insigne
**Ranguri:** Pui de capibara → Capibara de baltă → Capibara de râu → Capibara Alpha → Capibara Legendă

**Insigne (exemple):**
- „Prima baie” — primul bilet
- „Yuzu de aur” — bilet câștigat cu cotă > 10
- „Zen” — 7 zile la rând în aplicație
- „Profesor” — 10 întrebări puse Profesorului Bara
- „Bălăceală” — ai creat o ligă

**Ligi private** = „bălți” 🫧

## 7. Ecrane
Navigare jos cu 5 tab-uri: **Acasă · Bilete · Roata · Clasament · Profil**

| Ecran | Conținut | Bara |
|---|---|---|
| Onboarding (3 pași) | ce sunt cotele, monede virtuale, „fără bani reali” | salută |
| Login | email + Google | zâmbește |
| Acasă | meciurile zilei, bonus zilnic, filtre ligă | — |
| Meci | comparator cote, factori (accidentări etc.), „Întreabă-l pe Profesorul Bara” | — |
| Bilete | bilet curent, active, istoric | doarme dacă e gol |
| Roata | roata + rotiri disponibile | învârte |
| Clasament | general + bălți | — |
| Profil | rang, insigne, statistici, follow | — |
| Card / Plătește | cardul, tap NFC, mod terminal, Google Wallet | cu cardul |
| Chat AI | Profesorul Bara | ochelari |
| Rezultat bilet | animație câștig / pierdere | sărbătorește / în apă |

**De făcut (Erin):** schițe pentru fiecare ecran (Figma sau pe hârtie), apoi le transformăm în layout-uri XML.

## 8. Iconițe
- Tab-uri custom: Acasă = vizuina, Bilete = frunză, Roata = felie de portocală, Clasament = trofeu cu urechi, Profil = capibara.
- Restul iconițelor: Material Symbols (rotunjite), ca să se potrivească cu fontul.

## 9. Animații
- Lottie (`com.airbnb.android:lottie`, merge din Java): Bara înoată, Bara sărbătorește, învârtirea roții, monede care cad.
- Animații scurte (< 1.5 s), cu opțiune de reducere a animațiilor (respectăm setarea din telefon).

## 10. Accesibilitate
- Contrast verificat (secțiunea 3).
- Câștig / pierdere nu doar prin culoare: și cu text + iconiță (✓ / ✗).
- Butoane de minim 48dp.
- Descrieri pentru imagini (pentru TalkBack).

## 11. Asset-uri
Desenate sau generate de noi, ori cu licență liberă — **fără** meme-uri sau imagini cu copyright.

| Asset | Status | Cine |
|---|---|---|
| Mascota Bara (toate pozele) | ⬜ de făcut | ? |
| Iconiță aplicație | ⬜ (acum e un cerc placeholder) | ? |
| Bara Coin | ⬜ | ? |
| Design card | ⬜ | ? |
| Roata | ⬜ | ? |
| Insigne | ⬜ | ? |
| Animații Lottie | ⬜ | ? |

## 12. De decis (Erin)
- [ ] Stilul mascotei și cine o desenează
- [ ] Fontul: Nunito sau Baloo 2
- [ ] Culorile finale (pornim de la cele de mai sus)
- [ ] Figma sau schițe pe hârtie
- [ ] Limba: doar RO sau RO + EN
- [ ] Numele finale pentru ranguri / insigne

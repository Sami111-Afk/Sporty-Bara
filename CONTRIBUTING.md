# Cum lucrăm

## Pe scurt
1. Iei un task din [Issues](https://github.com/Sami111-Afk/Sporty-Bara/issues) (asignat ție).
2. Faci un branch din `main`: `feature/<numar>-<nume-scurt>` (ex. `feature/7-slip-bilet`).
3. Commit-uri mici, mesaje clare.
4. Deschizi un **Pull Request** către `main`, cu `Closes #<numar>` în descriere.
5. Celălalt face review. Se face merge doar când CI e verde ✅ și review-ul e aprobat.

```bash
git checkout main && git pull
git checkout -b feature/7-slip-bilet
# ... lucrezi ...
git add -A && git commit -m "Slip bilet: selecții + miză"
git push -u origin feature/7-slip-bilet
gh pr create --fill        # sau din pagina repo-ului pe GitHub
```

## Reguli
- **Nu se face push direct pe `main`.** Totul prin PR.
- **Nu se urcă** `google-services.json`, chei API, keystore-uri (sunt în `.gitignore`).
- Orice schimbare la structura datelor sau la funcții se face în [`docs/API.md`](docs/API.md) în același PR.
- Logica din funcțiile Python care se poate testa fără Firebase stă în `functions/sportybara/` și are teste în `functions/tests/`.

## Rulare locală
```bash
# app
JAVA_HOME=/opt/android-studio/jbr ./gradlew assembleDebug test

# teste Python
cd functions && python3 -m pytest -q tests

# teste reguli Firestore (cer Java și Firebase CLI; prima dată: npm ci --prefix firestore-tests)
firebase emulators:exec --only firestore --project demo-sporty-bara "npm --prefix firestore-tests test"

# emulator Firebase (Auth, Firestore, Functions) — UI pe http://localhost:4000
firebase emulators:start
```

## Documente
- [Plan proiect](docs/PLAN.md) · [Plan Erin](docs/PLAN-ERIN.md) · [Plan Sami](docs/PLAN-SAMI.md)
- [Plan de design](docs/DESIGN.md) · [Contract de date](docs/API.md)

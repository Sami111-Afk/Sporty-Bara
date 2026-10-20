# Sporty-Bara

Aplicație Android — Java + XML Views (Material 3).

## Cerințe
- Android Studio (ultima versiune stabilă)
- JDK 17+ (vine cu Android Studio)
- minSdk 26 (Android 8.0), targetSdk 36

## Pornire
```bash
git clone https://github.com/Sami111-Afk/Sporty-Bara.git
```
Android Studio → **File → Open** → folderul `Sporty-Bara` → așteaptă Gradle Sync → **Run ▶**.

Din terminal:
```bash
./gradlew assembleDebug   # APK în app/build/outputs/apk/debug/
./gradlew test            # teste unitare
```

## Documente
- [Plan proiect](docs/PLAN.md)
- [Plan de design](docs/DESIGN.md)

## Workflow
- `main` = stabil; lucrăm pe branch-uri (`feature/...`) și facem Pull Request.
- Nu se comit `local.properties`, keystore-uri sau `google-services.json`.

## Echipă
- [@Sami111-Afk](https://github.com/Sami111-Afk)
- [@erinlud](https://github.com/erinlud)

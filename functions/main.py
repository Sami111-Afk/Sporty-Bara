"""Cloud Functions Sporty-Bara (Python).

Fiecare funcție nouă se adaugă aici; logica pură (fără Firebase) stă în pachetul
`sportybara/` ca să poată fi testată cu pytest fără emulator.
Contractul (parametri, răspunsuri, erori) e în docs/API.md.
"""
from firebase_admin import initialize_app
from firebase_functions import https_fn, options

options.set_global_options(region="europe-west1", max_instances=5)
initialize_app()


@https_fn.on_call()
def ping(req: https_fn.CallableRequest) -> dict:
    """Verificare că app-ul ajunge la funcții (folosit la legarea app ↔ Firebase)."""
    return {"ok": True, "uid": req.auth.uid if req.auth else None}

#!/usr/bin/env python3
"""Buduje podpisany custom.txt dla ID Desk (odpowiednik generatora custom clienta z RustDesk Pro).

Plik custom.txt kładzie się obok IDDesk.exe / rustdesk.exe (portable: w pakowanym katalogu).
Format: base64( ed25519_signature(64B) || JSON ), zgodny z `read_custom_client` w src/common.rs.

Użycie:
  ID_DESK_CUSTOM_SIGN_KEY=<base64 klucza prywatnego> python make_custom.py config.json > custom.txt

Przykładowy config.json (klucze z libs/hbb_common/src/config.rs::keys, '_' lub '-'):
{
  "app-name": "IDDesk",
  "default-settings": { "api-server": "https://infradesk.pl" },
  "override-settings": { "custom-rendezvous-server": "infradesk.pl", "key": "84RlZpwgH+jM8JnfPP40GVx6HtOC+7IsauZQQFdLb54=" },
  "disable-settings": "Y",
  "disable-account": "Y",
  "disable-ab": "Y"
}
Pozostałe klucze najwyższego poziomu (stringi) trafiają do HARD_SETTINGS (np. password/salt presetu).
"""
import base64, json, os, sys
from nacl.signing import SigningKey

if len(sys.argv) != 2:
    sys.exit(__doc__)
priv = os.environ.get("ID_DESK_CUSTOM_SIGN_KEY")
if not priv:
    sys.exit("Brak ID_DESK_CUSTOM_SIGN_KEY w env")
with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
payload = json.dumps(data, separators=(",", ":")).encode()
sk = SigningKey(base64.b64decode(priv))
signed = sk.sign(payload)  # signature || message
sys.stdout.write(base64.b64encode(bytes(signed)).decode())

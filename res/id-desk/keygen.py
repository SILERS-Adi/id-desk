#!/usr/bin/env python3
"""Generuje parę kluczy ed25519 do podpisywania custom.txt ID Desk.

Klucz PUBLICZNY wklej do `ID_DESK_CUSTOM_SIGN_PUB_KEY` w src/common.rs.
Klucz PRYWATNY trzymaj poza repo (sekret GitHub Actions `ID_DESK_CUSTOM_SIGN_KEY`
lub plik na serwerze z chmod 600). Nigdy nie commituj.

Użycie: python keygen.py
"""
import base64
from nacl.signing import SigningKey

sk = SigningKey.generate()
print("PUBLIC (do src/common.rs):", base64.b64encode(bytes(sk.verify_key)).decode())
print("PRIVATE (sekret, NIE do repo):", base64.b64encode(bytes(sk)).decode())

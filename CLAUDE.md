# ID Desk — brandowany klient zdalnego pulpitu InfraDesk (fork RustDesk)

**Co to jest:** fork `rustdesk/rustdesk` (AGPL-3.0) z tożsamością „ID Desk” (nazwa techniczna `IDDesk`),
zaszytym serwerem rendezvous/relay na vps1 i API InfraDesk. Silnik zdalnego dostępu dla agenta
InfraDesk (`ADRIA/infradesk/agent`) — agent instaluje go cicho przez MSI tak, jak dziś klienta „SILERS”
z RustDesk Server Pro, a od strony klienta całość wygląda jak jedna apka InfraDesk.

**Status (2026-08-19):** POC — pierwszy build w CI, nie wdrożony u klientów. Decyzja właściciela: nazwa
„ID Desk”, repo publiczne, cel = własny brand + zero paczek urządzeń RustDesk Pro.

Upstreamowe instrukcje dla agentów AI: `AGENTS.md` (układ repo, konwencje). Ten plik = to, co odróżnia fork.

## Co różni fork od upstreamu (trzymaj diff minimalny!)

| Gdzie | Co |
|---|---|
| `src/common.rs` | `ID_DESK_*` stałe + `apply_id_desk_branding()` (APP_NAME, serwer, klucz, api-server jako DEFAULT_SETTINGS), własny klucz podpisu `custom.txt` w `read_custom_client` |
| `res/`, `flutter/assets/icon.png`, `logo_light/dark.png`, `flutter/windows/runner/resources/app_icon.ico`, Android `mipmap-*` | ikony z `infradesk/LOGO/ID_icon_1024.png` |
| `flutter/windows/runner/Runner.rc`, `Cargo.toml` (description), `flutter/lib/desktop/widgets/tabbar_widget.dart` | metadane/nazwa „ID Desk” |
| `res/id-desk/` | `keygen.py`, `make_custom.py`, `custom.release.json` (konfiguracja custom clienta) |
| `.github/workflows/id-desk-windows.yml` | build Windows x64: portable exe + MSI, Release przy tagu `id-desk-v*` |

Wszystko „InfraDeskowe” (billing, CMDB, logika agenta) żyje w `infradesk/backend-v2`, **nie w tym repo** —
klient i tak wysyła `POST /api/audit/conn`, `/api/audit/file`, `/api/heartbeat`, `/api/sysinfo` na `api-server`.
Submoduł `libs/hbb_common` = upstream bez zmian (celowo; stałe nadpisujemy w runtime z `src/`).

## Twarde reguły

- **AGPL-3.0**: kod każdej wersji rozdawanej klientom musi być publiczny w tym repo (tag = wydanie).
  Zachowaj `LICENCE` i copyright RustDesk/Purslane. Backend InfraDesk jest osobnym programem (HTTP), nie linkujemy go.
- **Klucz prywatny podpisu `custom.txt`** = sekret GitHub Actions `ID_DESK_CUSTOM_SIGN_KEY`. Nie do repo, nie do notatek.
  Zgubiony → `python res/id-desk/keygen.py`, nowy klucz publiczny do `src/common.rs`, nowy build.
- **Zmiana serwera/klucza hbbs** (`ID_DESK_RENDEZVOUS_SERVER`, `ID_DESK_RS_PUB_KEY`) = nowy build u wszystkich klientów.
  Przy migracji Pro → OSS hbbs zachowaj parę kluczy `/home/adrian/rustdesk/id_ed25519*` — wtedy klienci działają bez zmian.
- Nazwa techniczna `IDDesk` bez spacji (URI `iddesk://`, usługa Windows `IDDesk`, `IDDesk.exe`, `C:\Program Files\IDDesk`).
  Agent InfraDesk szuka dziś `C:\Program Files\SILERS\SILERS.exe` i `RustDesk.toml` — przy wdrożeniu dodać ścieżki `IDDesk`.
- Nie zaczynamy funkcji „agentowych” w Flutterze, dopóki istnieje agent Python — ID Desk to silnik zdalny.
- **`custom.txt` NIE jest używany w buildzie** (obecność pliku obok exe wywołuje abort klienta, kod 3 —
  do zbadania). Branding, serwer, klucz, api-server i `disable-account/ab` są zaszyte w
  `src/common.rs::apply_id_desk_branding`. Presetowe hasło → agent przez `IDDesk.exe --password`.
  Mechanizm `res/id-desk/make_custom.py` zostaje do czasu naprawy crashu.

## Synchronizacja z upstreamem

```
git fetch upstream && git merge upstream/master     # konflikty tylko w plikach z tabeli wyżej
# porównaj .github/workflows/flutter-build.yml (job build-for-windows-flutter) z id-desk-windows.yml:
# wersje FLUTTER_VERSION / LLVM_VERSION / VCPKG_COMMIT_ID / SCITER_RUST_VERSION i nowe kroki
```
Upstreamowe workflowy (`ci.yml`, `flutter-ci.yml`, `flutter-nightly.yml`, `flutter-tag.yml`, `fdroid.yml`, `playground.yml`,
`update-webpki-roots.yml`) są **wyłączone po stronie GitHuba** (Actions → workflow → Disable), nie usunięte — żeby merge nie konfliktował.

## Build / wydanie

- CI: Actions → „ID Desk – Windows” → Run workflow (artefakty `id-desk-windows-x86_64-installers`), lub
  `git tag id-desk-v1.4.9-1 && git push origin id-desk-v1.4.9-1` → GitHub Release (pre-release) z `IDDesk-<ver>-x86_64.{exe,msi}`.
- Lokalnie (Windows): wymaga VS 2022, LLVM 15, vcpkg (commit z workflowu), Flutter 3.24.5 z silnikiem rustdesk/engine —
  patrz `docs/` upstreamu. W praktyce buduj w CI.
- Własny `custom.txt` poza CI: `ID_DESK_CUSTOM_SIGN_KEY=... python res/id-desk/make_custom.py cfg.json > custom.txt`
  obok `IDDesk.exe` (klucze ustawień: `libs/hbb_common/src/config.rs` → `mod keys`).

## Wdrożenie u klienta (docelowo)

1. MSI z Release → `https://infradesk.pl/downloads/IDDesk.msi` (dziś agent pobiera `silers.msi`).
2. Agent InfraDesk: `install_rustdesk()` → `IDDesk.msi`, ścieżki exe/toml `IDDesk`, `--password` jak dziś.
3. backend-v2: endpointy `/api/audit/conn`, `/api/heartbeat`, `/api/sysinfo` (zastępują cron `sync-rustdesk-sessions.ts`).
4. Serwer: OSS `rustdesk-server` (hbbs/hbbr) zamiast Pro → brak limitu urządzeń; Pro opłacony do 2027-02-27, migracja stopniowa.

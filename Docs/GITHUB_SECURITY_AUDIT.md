# GitHub Security and Privacy Publication Audit

**Audit date:** 2026-07-13  
**Repository:** Aetheraeon AI System  
**Audited branch/commit:** `main` at `035831c`  
**Remote state at audit time:** local `main` and `origin/main` were identical (`0` ahead, `0` behind)  
**Overall publication readiness:** **42/100 — NOT READY for privacy-safe publication**

## Executive summary

The current Git-visible tree contains **84 tracked files**. The complete local Git history contains **8 commits, 85 unique historical paths, and 88 unique blobs**. The one history-only path is an empty batch file, `core/PY_Files_Names.bat`. The audit found no committed live API key, OAuth credential, database password, bearer token, private key, certificate, cookie, access token, database dump, Chroma store, user profile, session file, log, screenshot, or binary installer in the current tree or available Git history.

Publication is nevertheless **not ready** because:

1. A predictable Flask session-signing fallback is compiled into the application. If `SECRET_KEY` is absent, an attacker who knows the public source can forge Flask session cookies.
2. The repository publishes the owner's full legal name in source, documentation, and the license, and publishes a personal-looking Gmail address in all eight commits' author metadata.
3. `.gitignore` has high-risk gaps around active `Data/Memory` settings, MariaDB dump names, cookies, sessions, models, and SQLite sidecar/backup files.
4. Documentation and executable sample playbooks expose detailed legacy drive layouts, project names, a user first name, and nonportable `H:` targets.
5. Existing release documentation states that Google/n8n credentials were previously exposed and removed. No such credentials exist in the available eight-commit history, but external copies, releases, forks, logs, or older history cannot be cleared by this audit alone.

The score reflects the absence of committed live credentials or private data stores, but publication remains blocked by one critical session-security defect and multiple high privacy/ignore-rule risks.

## Scope and method

- Audited the exact current tracked set from `git ls-files`, not arbitrary ignored runtime data.
- Audited all reachable commits and blobs from all local refs, including deleted/historical paths.
- Searched for provider-specific key formats, JWTs, bearer tokens, PEM/private-key markers, credential assignments, connection strings, high-entropy token candidates, email addresses, phone numbers, coordinates, private IPs, paths, user identifiers, and privacy-sensitive filenames/content.
- Compared required ignore targets with `.gitignore`, including a case-sensitive simulation because GitHub contributors may use case-sensitive systems even though this checkout has `core.ignorecase=true`.
- Checked tracked and historical blob sizes, file signatures/null bytes, extensions, Git LFS state, generated dependency metadata, archives, models, installers, binaries, database files, logs, and screenshots.
- Reviewed documentation separately for credentials, network details, paths, private URLs, and images.

This is a static publication audit, not a runtime penetration test. Credential validity was not tested. GitHub-side Actions logs, releases, caches, issues, pull requests, forks, repository secrets, and unreachable/pruned Git objects are outside the local repository and require separate review.

At the beginning of the audit, a local `.env` file was present and correctly ignored. It was no longer present when an exact value-to-tracked-content comparison was attempted. Its values are not included in this report. The current tracked tree and all reachable history were independently scanned for credentials and secret formats, and `.env` itself was never tracked in the available history.

## Risk scale

| Level | Meaning |
|---|---|
| Critical | Directly exploitable security exposure or publication blocker |
| High | Likely sensitive disclosure or strong chance of future secret/private-data publication |
| Medium | Meaningful privacy, portability, or operational exposure requiring review |
| Low | Limited exposure, hygiene issue, or intentional example that should be confirmed |
| Informational | Safe or expected content recorded for completeness |

## Critical findings

### C-01 — Predictable Flask session-signing fallback

**Risk: Critical**

`core/api_gateway.py:1681` sets `app.secret_key` to the public literal `aetheraeon_fallback_dev_key` whenever the environment-provided `SECRET_KEY` is absent. Flask's default client-side session integrity depends on this key. A deployment that omits `.env` or `SECRET_KEY` can therefore accept attacker-forged session cookies.

Related locations:

- `.env.example:8-10` correctly instructs the operator to generate a random key.
- `core/config_loader.py:170` reads `SECRET_KEY` without a fallback.
- `Docs/CONFIGURATION.md:14` explicitly calls the code fallback insecure.

**Recommended action:** remove the fixed fallback, fail startup when a strong production key is missing, rotate any key used by an exposed deployment, and invalidate existing sessions after rotation. Do not publish or deploy until this is resolved.

## High-risk findings

### H-01 — Full legal identity and commit email are public

**Risk: High if publication is not explicitly consented to; Informational if intentional**

The owner's full legal name appears in three variants. Every current occurrence is listed below without repeating the name in this report:

- `Docs/ai_identity_specification.md:31`
- `LICENSE:3,14,93,112,165`
- `README.md:155`
- `core/agent_identity.py:2,19,235`
- `core/api_gateway.py:1386`

Additional first-name/user-context occurrences:

- `Docs/PATH_AUDIT.md:43`
- `Docs/PROJECT_USAGE_AUDIT.md:107,223-226,342`
- `WebUI/index.html:139` (generic-looking registration placeholder)
- `core/ai_orchestrator.py:1598` (preference/memory example)
- `core/api_gateway.py:1387` (initials example)
- `core/help_system.py:191` (memory command example)

All eight commits use the same Git author identity and personal-looking Gmail address (`XxNeroMortexX@…`). The address is visible in commit metadata even if it is removed from current files. The GitHub handle is also visible through repository/commit identity.

Some name use is clearly intended as copyright attribution and system authorship, so removal may have licensing implications. The privacy issue is lack of separation between public attribution and a full personal identity/email.

**Recommended action:** explicitly decide whether public legal-name attribution is intended. If not, obtain licensing advice before changing attribution, use a public pseudonym/organization where legally appropriate, configure a GitHub noreply commit address, and consider history rewriting only after assessing forks/tags and coordinating the force-push. Treat the current email as already public.

### H-02 — Active private settings are not reliably ignored on case-sensitive systems

**Risk: High**

Active runtime files are `Data/Memory/settings.json` and `Data/Memory/personality.json` (`core/system_paths.py:168-169`). `core/config_manager.py:179,327-328` can persist `google_cse_api_key` and the full settings object; `core/personality_engine.py:333-345` persists the personality profile.

The ignore file contains lowercase `memory/` plus selected `Data/Memory` children, but no complete `Data/Memory/` rule. In this Windows checkout, `core.ignorecase=true` makes lowercase `memory/` appear to protect the uppercase directory. A case-sensitive check shows:

- `Data/Memory/settings.json` — **not ignored**
- `Data/Memory/personality.json` — **not ignored**
- `Data/Memory/memory.json` — ignored explicitly
- `Data/Memory/Chroma/`, `Embeddings/`, and `Cache/` — ignored explicitly

This can allow API credentials, personal preferences, and runtime state to be committed by a Linux/macOS contributor or CI process.

**Recommended action:** add an exact `Data/Memory/` policy, with narrow allow-list exceptions only for deliberately public templates or README files. Verify with case-sensitive `git check-ignore` tests.

### H-03 — Database backup ignore coverage is unsafe

**Risk: High**

`.gitignore:33-36` ignores `*.sql` and then unignores the entire `database/` directory and every direct `database/*.sql` file. As a result, a real dump named `database/backup.sql` is not ignored. The following common dump forms are also not ignored:

- `database/backup.sql.gz`
- `database/backup.dump`
- `*.dmp`, compressed SQL archives, and timestamped database export folders

The tracked `database/aetheraeon_schema.sql` is a schema-only source file: no `INSERT`, `COPY`, `CREATE USER`, `IDENTIFIED BY`, password assignment, or data rows were found. It is appropriate source content, but the broad exception creates future risk.

**Recommended action:** ignore database exports broadly and allow-list only the exact schema filename, such as `!database/aetheraeon_schema.sql`.

### H-04 — Repository documentation reports an earlier credential incident

**Risk: High / requires external verification**

`Docs/RELEASE_READINESS.md:48` states that plaintext Google/n8n credentials were found and removed, must be treated as compromised, and should be purged from history, forks, logs, and releases.

No Google key format, n8n credential, secret assignment with a live value, or sensitive deleted file was found in the available eight-commit history. That does not prove the credentials were never published in an older repository, force-pushed history, release artifact, fork, CI log, or another remote.

**Recommended action:** confirm the referenced credentials were revoked/rotated; review GitHub releases, Actions logs/artifacts/caches, forks, pull requests, and secret-scanning alerts; and verify whether older remote history exists outside the current local object database.

## Medium- and low-risk findings

### M-01 — Legacy/personal machine paths and project context are public

**Risk: Medium**

The most privacy-relevant values are the legacy `H:\Sentimina\AI`, `H:\MQ2_Project`, `Users\James\…`, and related registry-backup/user-session descriptions. They disclose drive layout, prior project names, a user first name, and the existence/names of former private artifacts. Executable playbooks still target `H:\MQ2_Project`.

Every current source line containing the requested drive/user path classes or closely related machine-specific Windows locations is inventoried below. Multiple values on one line are represented by that line once.

| File | Lines | Context | Risk |
|---|---:|---|---|
| `.gitignore` | 96-97 | `Users` ignore rule and exception | Low |
| `Docs/CONFIGURATION.md` | 52,55-56,60,62,69,71 | `Users`, `%USERPROFILE%`, private n8n/Chroma locations | Low-Medium |
| `Docs/INSTALL.md` | 190,192 | Hard-coded `H:/AISystem/WebUI` Apache example | Medium |
| `Docs/PATH_AUDIT.md` | 9-19,21,25,34-36,42-45,51-55 | Consolidated legacy `H:`, `C:`, `D:`, `E:`, user, temp, and registry paths | Medium |
| `Docs/PROJECT_USAGE_AUDIT.md` | 4,49,92,107,222-226,236-237,239,256,275,313,328,330,342,356 | Old root, `Users/James`, model/backup trees, legacy scripts | Medium |
| `Docs/RELEASE_READINESS.md` | 52,62 | Personal playbook and `Users` warnings | Medium |
| `core/system_security.py` | 381,536,559 | Generic `C:\Temp`/drive parser examples | Low |
| `core/system_utils.py` | 443-447,473-475 | Generic `C:`, `D:`, and `E:` parser examples | Low |
| `core/tool_executor.py` | 1162,1170,1187 | `H:\AISystem` command examples | Medium |
| `playbooks/open_mq2.json` | 11,19 | Executable `H:\MQ2_Project` targets | Medium |
| `playbooks/test_sentimina.json` | 11,19,23 | Executable `H:\MQ2_Project`/`E3` targets | Medium |
| `scripts/Install_AI_Command.bat` | 25,67 | Generic per-user `HKCU` registry location | Low |
| `scripts/Remove_AI_Command.bat` | 13,49,52,71 | Generic `HKCU` and `%TEMP%` locations | Low |

No real `C:\Users\<local-username>`, desktop, documents, downloads, UNC share, `/home/<username>`, `/Users/<username>`, or GPS path/location was found. `Docs/PATH_AUDIT.md:21` contains only literal redacted examples of those POSIX/user path forms. Loopback URLs (`127.0.0.1`, `localhost`) are development endpoints, not private network topology. No RFC1918 LAN address was committed.

**Recommended action:** replace active playbook targets and installation examples with portable placeholders; remove or generalize the historical path inventory if preserving those private details is not intentional; retain generic parser examples only where they materially document behavior.

### M-02 — Partial ignore coverage for sessions, cookies, users, models, and SQLite variants

| Target | Audit result | Risk |
|---|---|---|
| `Sessions/` | Only lowercase `sessions/` is specified; it fails on case-sensitive systems | Medium |
| `Cookies/` | No rule | High |
| `Users/` | `Users/*` is ignored, but `!Users/__init__.py` intentionally re-allows one file | Low now; Medium if more exceptions appear |
| `Models/` | Only `blobs/`, `manifests/`, and one named model directory are ignored | Medium (size/licensing risk) |
| `*.sqlite*` | Only `*.sqlite` and `*.sqlite3` are ignored; `*.sqlite-wal`, `*.sqlite-shm`, and other suffixes are not | High if runtime data is produced |

No file in these classes is currently tracked. The risk is preventive: these gaps make future accidental publication plausible.

**Recommended action:** add exact case variants or canonical directory rules, ignore all cookie/session/runtime model content, and use `*.sqlite*` where appropriate.

### M-03 — Personal examples and legacy product name remain in executable/content files

**Risk: Medium**

- `playbooks/test_sentimina.json:27` publishes the former/alternate name “Sentimina.”
- `core/ai_orchestrator.py:1598` uses a named person's photography preference as a memory example.
- `core/help_system.py:191` uses a named person's identity as a memory-write example.
- `Docs/PATH_AUDIT.md:11,43,45,55` and `Docs/PROJECT_USAGE_AUDIT.md:107,223-226,256,258,330,342` connect the same identifiers with private paths, user profiles, registry state, or legacy files.

These are not credentials, but together they reveal personal/project history and can seed personal content into demonstrations.

**Recommended action:** replace personal examples with neutral synthetic names and paths if this history is not intentionally public.

### L-01 — Package lock is generated and slightly over 1 MiB

**Risk: Low**

`package-lock.json` is 1,184,315 bytes (approximately 1.13 MiB). It is generated dependency-resolution metadata for the direct `n8n` dependency, not bundled `node_modules` vendor code. Its registry URLs and integrity hashes are expected public package metadata, not credentials. Committing a lock file is normally appropriate for reproducible installs, although this lock is unusually large because n8n has a broad dependency graph.

**Recommended action:** keep it if npm/n8n installation is supported; otherwise reassess whether the Node package manifest belongs in this repository. Do not remove it merely for size if reproducible npm installs are required.

### L-02 — Local `.env` changed during the audit

**Risk: Low / audit limitation**

A local ignored `.env` existed at the first inventory but was absent later. Git status showed it as ignored, it does not appear in any reachable commit, and no current tracked secret matched known credential formats. Because it disappeared, an exact comparison of each live `.env` secret value against tracked text could not be completed.

**Recommended action:** before the next publication or credential rotation, run an exact-value comparison locally without printing values, then run a dedicated history scanner such as Gitleaks or TruffleHog.

## Secret and credential audit results

| Check | Result | Risk |
|---|---|---|
| OpenAI keys | PASS — none found | Informational |
| Anthropic keys | PASS — none found | Informational |
| Google API keys/OAuth values | PASS — optional variables are blank/placeholders only | Informational |
| AWS/GitHub/Slack/provider token formats | PASS — none found | Informational |
| API keys, access/refresh tokens, bearer tokens, JWTs | PASS — none found | Informational |
| MariaDB password/connection URI | PASS — only a replacement placeholder is present | Informational |
| Database usernames | PASS with note — public example account `aetheraeon_app` only | Informational |
| Flask `SECRET_KEY` | **FAIL — predictable fallback; see C-01** | Critical |
| SSH keys, PEM/private keys, key stores | PASS — none found | Informational |
| Private/public certificates | PASS — none tracked | Informational |
| Encryption/session/cookie secrets | PASS except Flask fallback; no live values found | Critical via C-01 |
| Cookies/session/access-token files | PASS in current tree; ignore gaps remain | Medium-High future risk |
| Connection strings with embedded credentials | PASS — none found | Informational |
| `.env` tracked now or historically | PASS — never tracked in available history | Informational |
| `.env.example` | PASS — password/key placeholders and blank Google fields only | Informational |

The strings at `.env.example:6,10` and `Docs/INSTALL.md:75` are explicit replacement placeholders, not live secrets. Package-lock integrity hashes and package names containing words such as `credential`, `oauth`, `cookie`, or `1password` are third-party dependency metadata, not credentials.

## Personal information and private-data audit results

| Data class | Result | Risk |
|---|---|---|
| Full name | Found; see H-01 | High unless intentional |
| Email addresses | Personal-looking commit author email in all 8 commits; HTML example and upstream package deprecation emails are nonpersonal examples/third-party metadata | High |
| Home address | None found | Informational |
| Phone numbers | None found | Informational |
| GPS coordinates | None found | Informational |
| Local OS username path | None found | Informational |
| Personal notes/documents | No files found; personal examples/history remain, see M-03 | Medium |
| Registry exports | None tracked or in history; documentation names a former private registry backup | Medium contextual disclosure |
| Browser data/history | None found | Informational |
| Session files/cookies | None found | Informational current state |
| Conversation history/user profiles | None found; documentation names former `Users/James` content | Medium contextual disclosure |
| Memory/Chroma data | No runtime data found; only source/docs | Informational current state |
| MariaDB dumps | None found; schema only | Informational current state |
| Logs/debug dumps/stack-trace files | None found | Informational |
| Machine/device IDs | None found; `node-machine-id` is only a dependency name in the lock file | Informational |

## `.gitignore` verification matrix

| Required target | Status | Evidence / caveat | Risk |
|---|---|---|---|
| `.env` | PASS | `.gitignore:4` | Informational |
| `.env.*` | PASS | `.gitignore:5`; `.env.example` intentionally allowed | Informational |
| `venv`, `env`, `.venv` | PASS | `.gitignore:16-19` | Informational |
| `__pycache__` | PASS | `.gitignore:11` | Informational |
| `node_modules` | PASS | `.gitignore:102-103` | Informational |
| `chroma_memory` | PASS | `.gitignore:41-49` | Informational |
| `Data/Memory` | **PARTIAL/FAIL** | only selected children/files; active settings/personality unsafe case-sensitively | High |
| `Data/Logs` | PASS | `.gitignore:57` | Informational |
| `Data/Backups` | PASS | `.gitignore:84` | Informational |
| `Users` | PARTIAL | contents ignored, `Users/__init__.py` explicitly allowed | Low |
| `Sessions` | **FAIL case-sensitively** | only lowercase `sessions/` | Medium |
| `Cookies` | **FAIL** | no rule | High |
| `Models` | PARTIAL | only known subtrees | Medium |
| `Services/Ollama` | PASS | `.gitignore:104` | Informational |
| Database backups | **FAIL** | broad `database/*.sql` exception and missing dump/archive forms | High |
| `*.db` | PASS | `.gitignore:28` | Informational |
| `*.sqlite*` | PARTIAL | `.sqlite` and `.sqlite3` only | High |
| `*.log` | PASS | `.gitignore:54` | Informational |
| `*.zip` | PASS | `.gitignore:82` | Informational |
| `*.bak` | PASS | `.gitignore:79` | Informational |
| `*.tmp` | PASS | `.gitignore:80` | Informational |

Additional recommended ignore coverage:

| Suggested class | Reason | Risk if omitted |
|---|---|---|
| Exact `Data/Memory/`, with narrow public exceptions | Settings may hold Google API keys and personal preferences | High |
| `Cookies/`, `cookies/`, `*.cookie`, `*.cookies` | Browser/session authentication material | High |
| `Sessions/`, `*.session` | Cross-platform session state | High |
| `*.sqlite*` | WAL/SHM/backup files can contain full records | High |
| `*.dump`, `*.dmp`, `*.sql.gz`, `*.sql.bz2`, `*.sql.xz` | Common database backup forms | High |
| `*.7z`, `*.rar`, `*.tar`, `*.tar.gz`, `*.tgz` | Backups/models/private exports can bypass `*.zip` | Medium-High |
| `.npmrc`, `.pypirc`, `credentials.json`, `service-account*.json` | Common plaintext token/service-account locations | High |
| `instance/` | Common Flask location for private config/databases | High |
| `Data/Exports/`, `exports/`, `*.jsonl` where runtime-generated | Conversation/memory exports | Medium-High |
| General downloaded model patterns (`*.gguf`, `*.safetensors`, `*.onnx`, `*.ckpt`, `*.pth`) | Size and third-party license risk | Medium |
| `*.der`, `*.keystore`, `*.ovpn` | May contain private keys or access configuration | High |

## Large-file audit

Thresholds use binary MiB (`1 MiB = 1,048,576 bytes`).

| Threshold | Files | GitHub suitability | Risk |
|---|---|---|---|
| Greater than 1 MiB | `package-lock.json` — 1,184,315 bytes | Appropriate if npm/n8n support is intentional; generated lock metadata | Low |
| Greater than 10 MiB | None | PASS | Informational |
| Greater than 50 MiB | None | PASS | Informational |
| Greater than 100 MiB | None | PASS | Informational |

The same lock-file blob is the only historical blob above 1 MiB. Git LFS tracks no files and is not needed for the current tree.

## Third-party, binary, and generated-content audit

| Class | Result | Risk |
|---|---|---|
| Downloaded models | None tracked | Informational |
| Bundled installers | None tracked | Informational |
| EXE/DLL/MSI/native binaries | None tracked; all files are text and contain no null bytes | Informational |
| ZIP/archives | None tracked | Informational |
| `node_modules`/vendor trees | None tracked | Informational |
| Generated dependency files | `package-lock.json` only; appropriate lock metadata | Low |
| Database content | Schema-only `database/aetheraeon_schema.sql`; appropriate source artifact | Informational |
| Generated runtime data | None tracked | Informational |
| Upstream model/training content | Mentioned only in historical audit documentation; not present in current/history files | Informational |

## Documentation security review

| Check | Result | Risk |
|---|---|---|
| Passwords/secrets | No live values; placeholders and warnings only | Informational |
| Internal IP addresses | None; loopback only | Informational |
| Private URLs/hostnames | None; localhost and public vendor/API URLs only | Informational |
| Local network information | No real LAN IP/hostname; source prints runtime-discovered LAN/public IPs but no captured value is committed | Low runtime consideration |
| Sensitive screenshots | None; no image/PDF files or embedded data-image content | Informational |
| Machine paths | Multiple legacy and hard-coded paths; see M-01 | Medium |
| Personal identity/history | Full name, user/project identifiers, and former private artifact descriptions; see H-01/M-03 | High-Medium |
| Prior credential incident statement | Present; see H-04 | High |

## PASS items

- No committed live provider API key, OAuth secret, token, JWT, bearer token, password, SSH/private key, certificate, connection string, or cookie was detected.
- `.env` is ignored and was never tracked in the available history.
- `.env.example` contains only safe placeholders/blank optional credential fields.
- No database dump, Chroma/vector store, user profile, conversation archive, browser data, session file, cookie file, log, stack trace, debug dump, registry export, or device identifier is tracked.
- No phone number, home address, GPS coordinate, real private-network address, UNC share, or local OS username path was detected.
- No screenshots or other image assets are present.
- No downloaded model, bundled installer, executable, DLL, archive, vendor directory, or native binary is present.
- No file exceeds 10 MiB; none approaches GitHub's 100 MiB per-file limit.
- The SQL file is schema-only and contains no data rows or database credentials.
- Current tracked files are not themselves ignored, and the working tree was clean before this report was created.

## Required actions before publication

1. **Critical:** eliminate the public Flask fallback key, require a strong configured key, rotate deployed keys, and invalidate prior sessions.
2. **High:** decide whether publishing the legal name and personal-looking commit email is intentional; address commit identity/history and licensing consequences accordingly.
3. **High:** protect the entire active `Data/Memory` runtime area on case-sensitive systems, with only deliberate public-template exceptions.
4. **High:** narrow the SQL allow-list to the exact schema file and ignore all database dump/compressed backup formats.
5. **High:** confirm revocation/rotation and external cleanup of the Google/n8n credentials referenced by `Docs/RELEASE_READINESS.md`.
6. **High/Medium:** add cross-platform rules for cookies, sessions, all SQLite variants, runtime models, and additional archive/export formats.
7. **Medium:** sanitize or replace the two `H:\MQ2_Project` playbooks, the `H:/AISystem` installation example, personal memory examples, and the historical path/user/registry narrative.
8. **Process:** enable GitHub secret scanning/push protection where available and run a dedicated full-history scanner before the next release.

## Final assessment

**Readiness score: 42/100.** The repository is comparatively clean of live secret material and private runtime artifacts, but it is not safe to treat as publication-ready while a known predictable session key can activate and while high-risk privacy/ignore-rule issues remain. Because `main` matched `origin/main` at audit time, current GitHub readers should be assumed to have access to all present identity, path, and fallback-key disclosures.

This report is advisory only. No source, configuration, history, ignore rule, credential, or project artifact was modified or removed as part of the audit.

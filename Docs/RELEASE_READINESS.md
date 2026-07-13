# Release readiness report

Audit date: 2026-07-13

Overall status: **Conditionally ready after the remaining repository/history and live-MariaDB checks below.** Runtime dependency installation and active-code imports pass from a clean Python environment.

## Completed checks

| Check | Result | Evidence |
|---|---|---|
| Runtime dependencies verified | Pass | Active imports mapped to ten direct packages; isolated Python 3.12 install and `pip check` passed |
| Development dependencies verified | Pass | `regex` is the only extra package used by a developer helper; isolated install passed |
| `requirements.txt` generated | Pass | Direct runtime packages only, exact tested versions |
| `requirements-dev.txt` generated | Pass | Development/helper package only |
| `.env.example` generated | Pass | Exact match to the nine environment names read by active core code; placeholders only |
| Database schema created | Static pass | All seven tables referenced by core SQL are defined in `database\aetheraeon_schema.sql` |
| Database seed assessed | Not required | Existing registration logic creates the first user and promotes user ID 1 to admin |
| Installation guide | Pass | `Docs\INSTALL.md` covers the complete Windows flow |
| Dependency documentation | Pass | `Docs\DEPENDENCIES.md` covers Python, system, optional, model, Node, port, and service dependencies |
| Configuration documentation | Pass | `Docs\CONFIGURATION.md` documents variables, files, runtime/data/cache locations, and user storage |
| Hardcoded paths | Pass with legacy findings | Active root/editor/validator paths made portable; all remaining literal families classified in `Docs\PATH_AUDIT.md` |
| Secrets scan | Pass with rotation action | No high-confidence key/token/private-key signature remains in non-vendor text; plaintext values were removed from two setup scripts |
| `.gitignore` | Pass for future additions | Covers secrets, environments, dependencies, binaries, models, runtime DBs, users, backups, logs, caches, and key files; explicitly allows release SQL and `.env.example` |
| Active Python compilation | Pass | `core`, validator, MemoryEditor, and Emoji Finder compile under Python 3.12 |
| Runtime import smoke test | Pass | All direct dependencies plus `core.api_gateway` import in the isolated environment |
| Node dependency | Pass | Root npm tree resolves `n8n@2.22.6`; `npx n8n --version` reports 2.22.6 |
| Frontend dependency audit | Pass | Three separated browser-native HTML/CSS/JS files; no build, CDN, or external frontend package |

## Clean-install verification performed

1. Created a new Python 3.12 virtual environment.
2. Installed `requirements.txt` from the package index successfully.
3. Installed `requirements-dev.txt` successfully.
4. Ran `pip check`: no broken requirements.
5. Imported every direct runtime package and `core.api_gateway` successfully.
6. Compiled all active Python sources successfully.
7. Verified the root npm dependency tree and n8n executable version.
8. Compared `.env.example` keys programmatically with every environment read in active core code: no missing or extra names.
9. Compared the schema table set with tables referenced by core SQL: all real application tables are present.

The backend was not launched end-to-end because this audit machine has no MariaDB client/server installed. Ollama and n8n executables are present, but full AI/workflow calls were not used because they would operate on the developer's existing services and data.

## Remaining issues before a public GitHub release

1. **Run a live MariaDB import test.** On a clean MariaDB 10.6+ or 11.4 LTS instance, import `database\aetheraeon_schema.sql`, start `python -m core.api_gateway`, register the first account, create a conversation, and save one message. Static SQL/table coverage passes, but a live server import was not available here.
2. **Repair or remove from the release the incomplete legacy `Scripts\API_Server.py`.** It fails parsing at line 8 with `unexpected indent`. It is not the active entry point; `core.api_gateway` passes. Altering/removing it was outside this non-refactor audit.
3. **Restore/inspect real Git metadata before publishing.** The workspace contains an empty/nonfunctional `.git` directory, and `git status` reports that this is not a repository. Consequently, the audit cannot prove which existing files were previously tracked.
4. **Rotate the exposed Google/n8n credentials.** Plaintext credentials were found and removed from setup-script copies. Treat them as compromised and purge them from any real Git history, forks, logs, and releases.
5. **Untrack generated/private artifacts if they exist in real history.** `.gitignore` prevents new additions but does not remove already tracked content.
6. **Address release UX placeholders.** `readme.md` and `start.bat` are empty. The install guide is complete, but GitHub visitors will not see it unless the README links to it.
7. **Review duplicate n8n manifests.** The active root lock resolves 2.22.6; `Services\N8N` separately resolves 2.20.9. The install guide intentionally uses the active root manifest.
8. **Sanitize or replace personal playbooks.** `playbooks\open_mq2.json` and `playbooks\test_sentimina.json` reference `H:\MQ2_Project` and are not portable.

## Do not commit or publish

- `.env` or any machine-specific `.env.*` file other than `.env.example`
- `env\`, `.venv\`, `.release-venv\`, `__pycache__\`, or test/tool caches
- root or service `node_modules\`
- `Services\Ollama\` and the 736 MB `Scripts\OllamaSetup.exe`
- `Models\blobs\`, `Models\manifests\`, downloaded Hugging Face model trees, or Ollama model data
- `chroma_memory\`, Chroma indexes/SQLite files, or `Data\Memory\memory.json`
- `Users\*`, session state, private profiles, registry backups, or legacy `memory\` state
- MariaDB data dumps, n8n user state/credentials, logs, backups, temporary files, or archive ZIPs
- certificates, private keys, SSH keys, signing files, or session cookies

If any of these were already committed, remove them from the index and purge sensitive/binary history before creating a release. Do not rely on `.gitignore` to erase history.

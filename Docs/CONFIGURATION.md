# Configuration and storage

## Environment variables

Copy `.env.example` to `.env`. `core\config_loader.py` loads this file from the repository root regardless of the shell's current directory.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DB_HOST` | Yes | None | MariaDB host; clean-install guide uses `127.0.0.1` |
| `DB_PORT` | Yes | None | MariaDB TCP port; normally `3306` |
| `DB_NAME` | Yes | None | Database containing the Aetheraeon schema |
| `DB_USER` | Yes | None | MariaDB application account |
| `DB_PASS` | Yes | None | MariaDB application account password |
| `SECRET_KEY` | Yes | Insecure development fallback in code | Signs Flask session cookies; use a unique random value |
| `N8N_URL` | No | `http://localhost:5678` | n8n health and webhook base URL |
| `GOOGLE_CSE_API_KEY` | No | Empty | Google Custom Search API key |
| `GOOGLE_CSE_CX` | No | Empty | Google Programmable Search engine ID |

The web-search variables are read directly from the process environment and can also be stored in the settings JSON. Environment values take precedence. Never commit `.env` or real settings credentials.

Values previously present in `.env.example`—`AGENT_NAME`, `CHROMA_PATH`, and `LOG_LEVEL`—were removed because active code never reads them. `OLLAMA_HOST` is not exposed as supported configuration because multiple health/model endpoints currently assume local port `11434`.

## Configuration files

| Path | Purpose | Commit? |
|---|---|---|
| `.env` | Machine credentials and service endpoints | No |
| `.env.example` | Placeholder-only configuration template | Yes |
| `Data\Memory\settings.json` | Created when runtime model/search/UI/personality settings are saved | Template/default only; do not commit private API keys |
| `Data\Memory\personality.json` | Created when personality settings are saved | No if it contains user preferences |
| `playbooks\*.json` | File-based automation playbooks | Only sanitized, portable examples |
| `package.json` / `package-lock.json` | Optional root n8n installation | Yes |
| `database\aetheraeon_schema.sql` | Empty MariaDB schema | Yes |

The lowercase root `memory\` folder is a legacy duplicate. Active code uses `Data\Memory`, not `memory\settings.json` or `memory\memory.json`.

## Project and runtime folders

The project root is computed from `core\system_paths.py`; the repository can be cloned to any drive or folder.

| Folder | Contents | Lifecycle |
|---|---|---|
| `core\` | Active Python application | Source |
| `WebUI\` | Static frontend | Source |
| `database\` | Clean schema | Source |
| `playbooks\` | File playbook definitions | Source or user-authored |
| `Data\Memory\` | Settings, personality, memory-related runtime files | Persistent user data |
| `Data\Logs\` | Installer/file logs when produced | Runtime |
| `Data\Backups\` | Local backups | Runtime/private |
| `Data\Temp\` | Temporary application data | Runtime/disposable |
| `chroma_memory\` | ChromaDB SQLite/index/vector files | Persistent user data |
| `Users\` | Legacy/local user profiles and session state | Persistent/private; MariaDB is the active web-account store |
| `.venv\` | Local Python environment | Re-creatable cache |
| `node_modules\` | Optional n8n/npm installation | Re-creatable cache |
| `%USERPROFILE%\.ollama\models` | Ollama models (default Windows location) | External persistent model data |
| `%USERPROFILE%\.n8n` | n8n configuration, credentials, and default SQLite DB | External persistent/private data |

## User data and backups

User account data, conversation history, relational playbooks, and logs are stored in the MariaDB database named by `DB_NAME`. Semantic memories are stored separately in `chroma_memory\`. A complete backup therefore needs both a MariaDB dump and the Chroma directory while the application is stopped. If n8n is used, back up `%USERPROFILE%\.n8n` separately.

Do not publish `.env`, MariaDB dumps, Chroma data, `Users\*`, n8n state, logs, sessions, or backup archives.

## Cache locations

- Python bytecode: `__pycache__\` beside Python modules.
- Python environment/download cache: `.venv\` and pip's user cache outside the repository.
- Chroma embedding/index cache: `chroma_memory\` and `Data\Memory\Cache`/`Embeddings` if created.
- Ollama model cache: `%USERPROFILE%\.ollama\models` unless `OLLAMA_MODELS` is set at the Windows user level.
- npm dependencies: `node_modules\`.
- n8n application state: `%USERPROFILE%\.n8n`.

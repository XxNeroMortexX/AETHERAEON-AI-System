# Dependency audit

This inventory is derived from active imports, service commands, package manifests/locks, SQL calls, frontend asset references, and startup behavior. Historical files under `Scripts\Extras` are not runtime entry points.

## Python runtime packages

| Package | Pinned version | Used by |
|---|---:|---|
| `bcrypt` | 5.0.0 | Password hashing and verification |
| `chromadb` | 1.5.9 | Embedded persistent vector memory |
| `colorama` | 0.4.6 | Windows service-status terminal output |
| `Flask` | 3.1.3 | API gateway, sessions, and static web UI |
| `mysql-connector-python` | 9.7.0 | MariaDB connections and persistence |
| `ollama` | 0.6.2 | Local LLM calls |
| `psutil` | 7.2.2 | Service/process discovery and shutdown |
| `python-dotenv` | 1.2.1 | Root `.env` loading |
| `requests` | 2.32.5 | Ollama/n8n health, web search, public-IP lookup |
| `waitress` | 3.0.2 | Production WSGI server on Windows |

Transitive packages are resolved by pip and are intentionally not duplicated in `requirements.txt`. ChromaDB is embedded in-process; no Chroma server is required.

## Development/helper packages

| Package | Pinned version | Used by |
|---|---:|---|
| `regex` | 2026.1.15 | `Scripts\Emojii_Finder.py` developer helper |

The repository has no pytest-based suite, formatter configuration, or linter configuration, so no unreferenced test/lint/format package was added.

## System software

| Software | Minimum | Recommended / verified | Required? | Download |
|---|---:|---:|---|---|
| Windows | Windows 10 22H2 | Current Windows 11 | Required | Microsoft Windows |
| Python x64 | 3.10 | 3.12.x (verified on 3.12.3; 3.12.10 is the final 3.12 Windows bugfix installer) | Required | <https://www.python.org/downloads/windows/> |
| MariaDB Community Server | 10.6 | 11.4 LTS | Required | <https://mariadb.org/download/> |
| Ollama for Windows | 0.31.2 (verified server) | Current installer release | Required for AI responses | <https://ollama.com/download/windows> |
| Git for Windows | 2.x | Current maintained release | Required to clone; optional after download | <https://git-scm.com/install/windows> |
| Node.js | 22.16 | Current Node 22 LTS | Optional, required for n8n | <https://nodejs.org/en/download> |
| npm | Bundled with Node 22 | Bundled current npm 10.x | Optional, required for n8n | Included with Node.js |
| n8n | 2.22.6 (root lockfile) | 2.22.6 for reproducibility | Optional automation feature | Installed by `npm ci` |
| Aider | 0.86.2 verified | 0.86.2 for current integration | Optional code-agent feature | Installed with pip separately |
| Microsoft Visual C++ Redistributable x64 | No direct application requirement | Latest v14 if a native wheel/Ollama reports a missing runtime DLL | Optional troubleshooting prerequisite | <https://aka.ms/vc14/vc_redist.x64.exe> |

FFmpeg, FastAPI, Uvicorn, OpenAI, LiteLLM, PyMySQL, NumPy, SciPy, Pillow, OpenCV, Matplotlib, and office-document libraries are not imported by the active application and are not runtime requirements. The checked-in `all-MiniLM-L6-v2` directory is also not referenced; ChromaDB manages its own embedding implementation/cache.

## Node packages and frontend libraries

The root `package-lock.json` resolves one direct package: `n8n==2.22.6`. Its transitive packages are managed by npm. `Services\N8N\package.json` is a redundant legacy installation manifest pinned by its lock to n8n 2.20.9; active service startup runs `npx n8n` from the repository root.

`WebUI\index.html`, `WebUI\css\aetheraeon.css`, and `WebUI\js\aetheraeon.js` use browser-native HTML, CSS, and JavaScript. They have no external script, stylesheet, CDN, bundler, or npm dependency. Flask serves the files directly.

## AI models

Current defaults in `core\config_manager.py` are:

| Role | Default Ollama model | Required for default configuration? |
|---|---|---|
| Router | `qwen2.5-coder:14b` | Yes |
| Chat | `gpt-oss:20b` | Yes |
| Code | `qwen2.5-coder:32b` | Yes for code routing |

The optional Aider integration also defaults to `ollama/qwen2.5-coder:14b`. `Models\Pull_Models.txt` contains an older, different model list and is not read by the application.

## Databases and services

- MariaDB stores accounts, settings, personality traits, conversations, messages, relational playbooks, and logs.
- Embedded ChromaDB stores semantic vector memory under `chroma_memory\`.
- Ollama supplies local LLM inference.
- n8n accepts optional workflow webhooks.
- DuckDuckGo HTML search is the credential-free web-search provider.
- Google Custom Search is optional and requires `GOOGLE_CSE_API_KEY` plus `GOOGLE_CSE_CX`.
- `api.ipify.org` and `icanhazip.com` are queried at startup only to display a public IP; failure is non-fatal.

## Ports

| Port | Service | Required? | Configuration |
|---:|---|---|---|
| 8080/TCP | Flask/Waitress API and web UI | Required | Hardcoded in `core\api_gateway.py` |
| 3306/TCP | MariaDB | Required | `DB_PORT` |
| 11434/TCP | Ollama API | Required for AI | Local endpoint currently hardcoded in health/model calls |
| 5678/TCP | n8n UI/webhooks | Optional | URL via `N8N_URL`; health/start logic assumes local port 5678 |

No Redis, PostgreSQL, MongoDB, external Chroma server, cloud LLM API, FFmpeg process, or frontend development server is required by active code.

# Aetheraeon AI Project Usage Audit

Audit date: 2026-07-13  
Repository root audited: `H:\AISystem`  
Mode: static, read-only usage audit; no application files were changed, deleted, or moved.

## Scope and decision rules

The active application entry point is the documented command:

```text
python -m core.api_gateway
```

The audit traced imports from that entry point, Flask route registration, static tool and service registration, file/path operations, `os.path`/`pathlib` use, playbook discovery, frontend `fetch()` calls, HTML assets, batch launch/install commands, and database access. It also searched for `importlib`, `__import__`, plugin loaders, globbing, and filename/folder references throughout the non-excluded project.

Statuses mean:

- **REQUIRED**: needed to start the current application or complete its documented clean installation.
- **REFERENCED**: named or discovered by active code, but may be generated at runtime or belong to an optional feature.
- **OPTIONAL**: useful documentation, development, administration, or optional-service content; not required for the base application path.
- **UNUSED**: no active import, startup reference, runtime path, frontend reference, or package-manager role was found.
- **UNKNOWN**: static evidence is insufficient to determine provenance or whether the owner still wants the item.
- **LEGACY**: an unused older implementation, obsolete installer, backup, migration artifact, or abandoned experiment.

“Unused” in this report means unused by the current repository code and documented startup path. It does not prove that a person never runs the file manually. Cleanup remains a manual decision.

## Explicit exclusions

As requested, the following generated/vendor data was skipped completely and is not classified file-by-file:

- `env/`, `venv/`, `.venv/`, `ENV/`, and any Python virtual environment
- root `node_modules/` and `Services/N8N/node_modules/`
- `__pycache__/`
- `chroma_memory/`
- `Data/Memory/Cache/`, `Data/Memory/Chroma/`, and `Data/Memory/Embeddings/`
- `Models/blobs/` and `Models/manifests/` (Ollama model storage)
- `Services/Ollama/` (installed/bundled Ollama files)

These exclusions do not imply that generated runtime data should be committed.

## Executive findings

- The active runtime is `core/api_gateway.py` plus 27 imported `core` modules, `WebUI/index.html`, `.env` configuration, MariaDB, and the local Chroma directory created by the application.
- `core/system_debug.py` is the only orphan module in `core/`: no active module imports it.
- There is no general plugin loader or filesystem-based tool loader. Tools and services are registered through normal Python imports and static registry calls.
- `playbooks/` is dynamically enumerated by `core/automation_playbooks.py`; both JSON files are visible to the running application, although their contents are old machine-specific examples.
- `Scripts/API_Server.py` is not the entry point, has no caller, and fails Python parsing with `IndentationError: unexpected indent` at line 8.
- `Shared/`, `System/`, `Users/`, `Users_Templates/`, `Tools/`, and `TestShell/` are not read by current application code. Current accounts, sessions, settings, personality, and conversations use MariaDB and `Data/Memory`, not the `Users/` tree.
- The lowercase `memory/` folder is a legacy persistence layout. Active settings and personality paths are under `Data/Memory`.
- The active n8n command runs `npx n8n start` with the repository root as its working directory. Therefore the root `package.json`/`package-lock.json` supply optional n8n; `Services/N8N/package*.json` are a second, inactive installation layout.
- `WebUI/index.html` references local `css/aetheraeon.css` and `js/aetheraeon.js`. The frontend has no remote asset includes or external browser dependencies.
- Exact duplicate hashing found `Scripts/Extras/FixHTML1Line.py` duplicated under `Scripts/Extras/New Current backup/static/`, and the same duplication for `index_formatted.html`.
- `Scripts/New_Backups/core_Backup.zip` is a complete `core/` snapshot including `__pycache__`; `WebUI.zip` contains a copy of `index.html`. Neither archive is referenced.

# 1. Required folders

| Folder | Status | Reason |
|---|---|---|
| `core/` | **REQUIRED** | `python -m core.api_gateway` loads this package. Every active backend subsystem is here. All modules except `system_debug.py` are reachable from the entry point; `__init__.py` is the package marker. |
| `database/` | **REQUIRED** | `aetheraeon_schema.sql` defines the MariaDB tables used by active SQL. It is required for a documented clean install, although Python does not import the SQL file at runtime. |
| `WebUI/` | **REQUIRED** | `core/api_gateway.py` constructs Flask with `static_folder=WEBUI_PATH`; it serves `WebUI/index.html` from `/` and the separated CSS/JavaScript from root-relative static paths. |

# 2. Referenced folders

| Folder | Status | Reason |
|---|---|---|
| `Data/` | **REFERENCED** | `system_paths.py` defines this runtime tree. `config_manager.py` reads/writes `Data/Memory/settings.json`; `personality_engine.py` reads/writes `Data/Memory/personality.json`. Missing runtime directories are created by code. Existing installer logs and placeholder files are not consumed. |
| `playbooks/` | **REFERENCED** | `automation_playbooks.py` creates the folder if missing, calls `os.listdir()`, opens matching JSON, and exposes it through `/api/playbooks`. Files are data-discovered rather than imported. |
| `Services/` | **REFERENCED** (weak) | `system_paths.py` defines `SERVICES_PATH` and `OLLAMA_PATH`, and `system_health_check.py` imports `OLLAMA_PATH`; however, the imported path is not used to launch Ollama. Active service launch uses commands on `PATH`. Existing `Services/N8N` content is not the active n8n package location. |

# 3. Optional folders

| Folder | Status | Reason |
|---|---|---|
| `Docs/` | **OPTIONAL** | Documentation and one unreferenced filename-normalization utility. Not read at runtime. Important for distribution, but not application execution. |
| `Scripts/` | **OPTIONAL** | Contains two useful standalone developer/admin utilities (`Emojii_Finder.py`, `MemoryEditor.py`), but no script in this folder starts the current application. Most contents are legacy installers, backups, or experiments. |
| `.git/` | **OPTIONAL / UNKNOWN** | Git metadata, not application content and never committed as project content. The visible directory did not present a usable repository to `git`, so its local state requires manual review. |

# 4. Unused folders

| Folder | Status | Reason |
|---|---|---|
| `.agents/` | **UNUSED** | Empty; no project code or launcher reference found. It may be local tooling metadata, so confirm before local removal. |
| `Backups/` | **UNUSED** | Empty and unreferenced. Active `BACKUPS_PATH` points to `Data/Backups`, not this root folder. |
| `memory/` | **LEGACY / UNUSED** | Contains old `memory.json` and `settings.json`. Active code uses `Data/Memory/settings.json`, `Data/Memory/personality.json`, MariaDB, and `chroma_memory/`. References to this lowercase layout occur only in old backup code and documentation. |
| `Models/` (non-excluded content) | **UNUSED** | `Pull_Models.txt` and `all-MiniLM-L6-v2/` are not referenced by active Python or HTML. Ollama is queried by model name/API; Chroma manages its own embedding function. The bundled model's TPU training script is an upstream artifact, not runtime code. |
| `Shared/` | **UNUSED** | `README.txt` and `SystemPrompts/SystemPrompt.txt` have no active reader. Identity/prompt text is embedded in `core/agent_identity.py` and other core modules. |
| `System/` | **UNUSED** | Contains an empty structure and `Settings/README.txt`; no active code reads it. It is created only by the old layout batch file. |
| `TestShell/` | **UNUSED** | Empty and unreferenced. |
| `Tools/` | **UNUSED** | Empty. Active tools come from Python modules and `tool_registry.py`; no filesystem tool discovery exists. |
| `Users/` | **UNUSED** | No active import or path reference. Account/session/conversation data is in MariaDB, UI session data is browser-side, and active configuration is under `Data/Memory`. The folder contains personal/profile/session JSON and must be manually reviewed as private data before publication. |
| `Users_Templates/` | **UNUSED** | Empty and unreferenced. |

Top-level excluded folders `env/`, `node_modules/`, `chroma_memory/`, and `__pycache__/` were intentionally not analyzed or assigned usage status.

## Nested folder and content findings

| Path | Status | Evidence |
|---|---|---|
| `Data/Memory/` | **REFERENCED** | Active target for generated `settings.json` and `personality.json`. The current `README.txt` is only a placeholder. Excluded cache/vector subfolders were skipped. |
| `Data/Logs/` | **UNUSED EXISTING DATA** | Six `install_2026-05-15_*.log` files are outputs from the old installer. Runtime `system_logger.py` writes to MariaDB, not these files. |
| `Data/Backups/`, `Data/Temp/` | **REFERENCED CONSTANT / UNUSED EXISTING FOLDER** | Defined in `system_paths.py`, but no active consumer was found; both are empty. |
| `Services/N8N/` excluding `node_modules` | **LEGACY / UNUSED** | Has its own `package.json` and lock for n8n `^2.20.9`. Active startup uses the root working directory, whose package declares n8n `^2.22.6`. Only the old installer changes into this directory. |
| `Scripts/Extras/` | **LEGACY** | Named backup/old/stable trees, tests against obsolete endpoints/names, registry migration artifacts, and HTML formatting experiments. No active imports or launch references. |
| `Scripts/New_Backups/` | **BACKUP / UNUSED** | `core_Backup.zip` snapshots all of `core` plus bytecode; `WebUI.zip` snapshots `index.html`. Neither is referenced. |
| `Users/James/` | **UNUSED / PRIVATE DATA REVIEW** | No active reader. Contains profile, session, UI, and agent JSON/text plus empty scaffold folders. Do not treat absence of code references as permission to publish personal data. |
| `Models/all-MiniLM-L6-v2/` | **UNUSED** | Complete local Hugging Face model/training bundle with no code reference. `train_script.py` imports PyTorch/XLA/Transformers only for training and is not part of runtime reachability. |

# 5. Required root files

| File | Status | Reason |
|---|---|---|
| `.env` | **REQUIRED LOCALLY / DO NOT COMMIT** | Loaded explicitly by `core/config_loader.py`. Contains machine-specific runtime configuration and may contain secrets. It is correctly ignored. |
| `.env.example` | **REQUIRED FOR DISTRIBUTION** | Referenced by installation/configuration documentation and provides the safe configuration template. Not read by runtime. |
| `.gitignore` | **REQUIRED FOR GITHUB SAFETY** | Prevents local secrets, environments, caches, user data, models, logs, backups, installed software, and keys from being committed. |
| `requirements.txt` | **REQUIRED** | Runtime Python installation manifest used by the clean-install path. |

# 6. Optional root files

| File | Status | Reason |
|---|---|---|
| `requirements-dev.txt` | **OPTIONAL** | Developer-only dependency manifest; not needed to run the app. |
| `package.json` | **OPTIONAL / REFERENCED BY PACKAGE MANAGER** | Declares root n8n. Needed only if the optional n8n integration is installed locally. `npx n8n start` executes from the repository root. |
| `package-lock.json` | **OPTIONAL / REFERENCED BY PACKAGE MANAGER** | Reproducible npm lock for the optional root n8n installation. It is not a JavaScript source reference but is consumed by `npm install`/`npm ci`. |
| `dependency_validator.py` | **OPTIONAL** | Standalone developer audit tool; not imported or launched by the application. |
| `AISystem_DIRECTORY_GUIDE.md` | **OPTIONAL / PARTLY STALE** | Human documentation only. It describes old structural folders and lists empty `start.bat`; no runtime reader. |

# 7. Unused root files

| File | Status | Reason |
|---|---|---|
| `readme.md` | **UNUSED PLACEHOLDER** | Zero bytes and never referenced. It does not help GitHub users in its current state; replacing its content is preferable to assuming the filename itself is unnecessary. |
| `start.bat` | **UNUSED PLACEHOLDER** | Zero bytes, never called by another script, and does not launch the application. |

## Root directory cleanup report

### Root files currently required

- `.env` — required only on the local machine; must remain uncommitted.
- `.env.example`
- `.gitignore`
- `requirements.txt`

### Root files currently referenced

- `package.json` and `package-lock.json` — implicit npm inputs for optional n8n and consistent with the active root working directory.
- `requirements-dev.txt` — referenced by developer setup documentation, not runtime.

### Root files safe to review for removal or replacement

- `start.bat` — empty and nonfunctional.
- `readme.md` — empty; review for replacement with a useful GitHub README rather than simple removal.
- `AISystem_DIRECTORY_GUIDE.md` — documentation only and contains obsolete structure descriptions.
- `dependency_validator.py` — optional local development tool; keep only if desired in the public developer workflow.
- `package.json` and `package-lock.json` — review only if n8n is intentionally removed as an optional feature; otherwise keep both.

### Root files never referenced by application code

- `.env.example`
- `.gitignore`
- `AISystem_DIRECTORY_GUIDE.md`
- `dependency_validator.py`
- `package.json`
- `package-lock.json`
- `readme.md`
- `requirements.txt`
- `requirements-dev.txt`
- `start.bat`

This last list is literal **application-code reference** status, not a deletion recommendation. Package managers, Git, installers, developers, and GitHub consume several of these files without Python/JavaScript source referring to their names.

# 8. Required scripts

Every Python file below is reachable from `core.api_gateway` through direct imports, except the package marker which participates in package loading.

| Script | Status | Why |
|---|---|---|
| `core/__init__.py` | **REQUIRED** | Package marker for the active `core` package. |
| `core/agent_identity.py` | **REQUIRED** | Imported by orchestrator, gateway, cognition, memory context, personality, and router layers. |
| `core/ai_orchestrator.py` | **REQUIRED** | Imported by gateway and playbook execution. |
| `core/api_gateway.py` | **REQUIRED** | Active Flask application and documented startup module. |
| `core/automation_playbooks.py` | **REQUIRED** | Imported by gateway; provides registered playbook routes and dynamic JSON discovery. |
| `core/config_loader.py` | **REQUIRED** | Loads `.env` and database/service configuration for multiple active modules. |
| `core/config_manager.py` | **REQUIRED** | Active settings API and `Data/Memory/settings.json` persistence. |
| `core/conversation_title_engine.py` | **REQUIRED** | Imported by gateway for conversation title generation. |
| `core/core_cognition.py` | **REQUIRED** | Imported by orchestrator. |
| `core/external_toolkit.py` | **REQUIRED** | Imported by orchestrator and tool executor. |
| `core/help_system.py` | **REQUIRED** | Imported by orchestrator, gateway, and router. |
| `core/json_helpers.py` | **REQUIRED** | Imported by core cognition. |
| `core/llm_interface.py` | **REQUIRED** | Imported by orchestrator, title engine, cognition, and router. |
| `core/memory_context_builder.py` | **REQUIRED** | Imported by orchestrator, gateway, and personality. |
| `core/memory_database.py` | **REQUIRED** | Active MariaDB and Chroma persistence implementation. |
| `core/memory_interface.py` | **REQUIRED** | Imported by multiple active memory/orchestration modules. |
| `core/model_registry.py` | **REQUIRED** | Active model lookup/selection used by core modules. |
| `core/personality_engine.py` | **REQUIRED** | Active personality generation and persistence. |
| `core/request_router.py` | **REQUIRED** | Imported by orchestrator and gateway. |
| `core/service_manager.py` | **REQUIRED** | Active service status/start/stop integration. |
| `core/service_registry.py` | **REQUIRED** | Imported by service manager and health check. |
| `core/system_health_check.py` | **REQUIRED** | Imported by gateway and playbook layer; service checks/start logic. |
| `core/system_logger.py` | **REQUIRED** | Imported by LLM, model registry, and tool executor. |
| `core/system_paths.py` | **REQUIRED** | Central clone-relative path definitions used across active modules. |
| `core/system_security.py` | **REQUIRED** | Imported by playbook and tool execution layers. |
| `core/system_utils.py` | **REQUIRED** | Shared helpers imported by multiple active modules. |
| `core/tool_executor.py` | **REQUIRED** | Active registered tool execution layer. |
| `core/tool_registry.py` | **REQUIRED** | Active static tool registry imported by orchestrator/gateway/executor. |

# 9. Optional scripts

| Script | Status | Why |
|---|---|---|
| `dependency_validator.py` | **OPTIONAL** | Standalone AST/dependency development audit. No runtime caller. It conditionally bootstraps `colorama` only inside the expected environment. |
| `Scripts/Emojii_Finder.py` | **OPTIONAL** | Standalone source-scanning developer utility. Its `regex` dependency is correctly development-only. No caller. |
| `Scripts/MemoryEditor.py` | **OPTIONAL** | Standalone interactive Chroma administrator. It uses the same clone-relative Chroma path and `aetheraeon` collection as active code, but nothing calls it. |
| `core/PY_Files_Names.bat` | **OPTIONAL** | Manual convenience utility that lists Python filenames and copies them to the clipboard. No caller. |

# 10. Unused scripts

| Script | Status | Why |
|---|---|---|
| `core/system_debug.py` | **UNUSED / ORPHAN MODULE** | Valid Python, but no active module imports it and no dynamic loader exists. Its `dbg_memory()` function is also uncalled. |
| `Users/__init__.py` | **UNUSED** | Empty package marker; no `Users` package import exists. |
| `Users/James/__init__.py` | **UNUSED** | Empty and no package import exists. |
| `Users/James/Agents/__init__.py` | **UNUSED** | Empty and no package import exists. |
| `Users/James/Agents/Aetheraeon/__init__.py` | **UNUSED** | Empty and no package import exists. |
| `Users/James/Agents/Aetheraeon/Identity/__init__.py` | **UNUSED** | Empty and no package import exists. |
| `Models/all-MiniLM-L6-v2/train_script.py` | **UNUSED / UPSTREAM TRAINING ARTIFACT** | No import or launcher reference. It targets TPU/PyTorch-XLA model training and is unrelated to runtime inference. |
| `start.bat` | **UNUSED** | Empty and never called. |

No project-owned `.cmd` or `.ps1` scripts were found outside excluded `node_modules` and installed/vendor software.

# 11. Legacy files and scripts

| Path | Status | Why |
|---|---|---|
| `Scripts/0.AI_Project_Layout.bat` | **LEGACY** | Hardcodes `H:\AISystem` and creates the old `Shared`, `System`, `Users`, `Services`, and related scaffold. No caller; many created folders have no active reader. |
| `Scripts/1.Ollama_Install.bat` | **LEGACY** | Hardcodes `H:\AISystem`, launches bundled `OllamaSetup.exe`, and installs into `Services/Ollama`; current installation docs use normal Ollama installation and active code uses CLI/API discovery. |
| `Scripts/2.Install_Aetheraeon_ENV.bat` | **LEGACY** | Hardcoded, administrator-elevating installer for the old `Services/N8N` layout. It duplicates the current documented installation path and is not called. |
| `Scripts/First_Setup_AI.bat` | **LEGACY** | Uses obsolete root `H:\Aetheraeon\AI`, installs an incomplete/old package set including FastAPI/Uvicorn, and does not match the Flask entry point. |
| `Scripts/API_Server.py` | **LEGACY / BROKEN** | Incomplete route fragment, no imports/startup reference, and the only non-excluded Python file that fails AST parsing (`IndentationError` at line 8). The live implementation is `core/api_gateway.py`. |
| `Docs/lowercase_files.bat` | **LEGACY / UNUSED** | Manual bulk-renaming utility in the docs directory. No caller; running it would rename documentation files. |
| `Scripts/Extras/Current_Stable/brain.py` | **LEGACY** | Older monolithic cognition implementation superseded by modular `core` code. No caller. |
| `Scripts/Extras/Current_Stable/executor.py` | **LEGACY** | Older executor superseded by `core/tool_executor.py`/`external_toolkit.py`. No caller. |
| `Scripts/Extras/Current_Stable/memory.py` | **LEGACY** | Older memory implementation superseded by core memory modules. No caller. |
| `Scripts/Extras/Current_Stable/server.py` | **LEGACY** | Older server implementation superseded by `core/api_gateway.py`. No caller. |
| `Scripts/Extras/Current_Stable/Setup_AI.bat` | **LEGACY** | Installer preserved inside explicitly named stable backup. No caller. |
| `Scripts/Extras/New Current backup/brain.py` | **LEGACY BACKUP** | Earlier monolithic implementation using the lowercase `memory/` layout. No caller. |
| `Scripts/Extras/New Current backup/db.py` | **LEGACY BACKUP** | Earlier database implementation. No caller. |
| `Scripts/Extras/New Current backup/executor.py` | **LEGACY BACKUP** | Earlier executor implementation. No caller. |
| `Scripts/Extras/New Current backup/server.py` | **LEGACY BACKUP** | Earlier server implementation. No caller. |
| `Scripts/Extras/New Current backup/static/FixHTML1Line.py` | **LEGACY DUPLICATE** | Exact SHA-256 duplicate of `Scripts/Extras/FixHTML1Line.py`. |
| `Scripts/Extras/old/brain.py` | **LEGACY** | Explicitly stored in `old/`; no caller. |
| `Scripts/Extras/old/intent.py` | **LEGACY** | Explicitly stored in `old/`; no caller. |
| `Scripts/Extras/old/router.py` | **LEGACY** | Explicitly stored in `old/`; no caller. |
| `Scripts/Extras/FixHTML1Line.py` | **LEGACY EXPERIMENT** | Standalone formatter for `index.txt` to `index_formatted.html`; not part of frontend build/startup. Its non-runtime dependencies are not installed by the project. |
| `Scripts/Extras/test.py` | **LEGACY TEST** | Hardcodes old `H:\Sentimina\AI\chroma_memory` and old name. Not part of an active test suite. |
| `Scripts/Extras/test_conversation.py` | **LEGACY TEST** | Calls obsolete singular `/api/conversation/create`; current route is `/api/conversations/create`. No test runner registration. |
| `Scripts/Extras/registry_migrate_aetheraeon.py` | **LEGACY MIGRATION** | One-time Windows registry migration from “Sentimina” to “Aetheraeon”; no runtime caller. |
| `Scripts/Extras/registry_backup_aetheraeon.json` | **LEGACY / SENSITIVE REVIEW** | Captured registry data with old absolute paths and machine state. Input/output artifact for the one-time migration, not runtime. |
| `Scripts/Extras/index.txt`, `index_formatted.html`, `Mouse effects.html` | **LEGACY FRONTEND EXPERIMENTS** | Not served by Flask and not linked from `WebUI/index.html`. |
| `Scripts/Extras/New Current backup/static/index.html`, `index.txt`, `index_formatted.html` | **LEGACY BACKUPS** | Old frontend copies. `index_formatted.html` is an exact duplicate of the top Extras copy. |
| `Scripts/Extras/Current_Stable/static/index.html` | **LEGACY BACKUP** | Old frontend paired with the old stable server. Not served by active Flask. |
| `Scripts/Extras/Current_Stable/requirements.txt` | **LEGACY MANIFEST** | Dependency list for the old stable implementation; not used by current install docs. |
| `Scripts/New_Backups/core_Backup.zip` | **BACKUP / UNUSED** | Archive of all current-named core modules plus copied `__pycache__`; no reference. |
| `Scripts/New_Backups/WebUI.zip` | **BACKUP / UNUSED** | Archive containing `index.html`; no reference. |
| `Scripts/CreateCMDCommand.txt` | **OPTIONAL LEGACY NOTE** | Manual Windows registry command note for creating a shell command. No code reference. It points at the correct module name but is not needed to run the app. |
| `Scripts/OllamaSetup.exe` | **LEGACY BUNDLED INSTALLER / UNKNOWN PROVENANCE** | Used only by the legacy `1.Ollama_Install.bat`, ignored by Git, and not required when Ollama is installed normally. Binary provenance/signature was not established by static source analysis. |
| `Models/Pull_Models.txt` | **LEGACY MANUAL NOTE** | Not parsed by code and lists a different older model set from the active defaults. |

# 12. Dead code report

## Orphan modules and unreachable scripts

- `core/system_debug.py` is the only unreachable core module from the active entry point.
- Every script in `Scripts/Extras/`, every legacy setup batch file, `Scripts/API_Server.py`, the model training script, and the `Users/**/__init__.py` files are unreachable from current startup.
- There is no dynamic-import/plugin mechanism that could make these modules reachable indirectly. The only `__import__` use outside the developer validator occurs in the already broken legacy `Scripts/API_Server.py`.

## Uncalled function candidates in otherwise required modules

Repository-wide symbol search found these definitions with no call sites:

| Function | Location | Assessment |
|---|---|---|
| `extract_memory_text` | `core/memory_interface.py:708` | Uncalled utility candidate. |
| `save_personality` | `core/personality_engine.py:315` | Uncalled utility candidate; active route uses other personality APIs. |
| `classify_memory_domain` | `core/request_router.py:754` | Uncalled routing helper candidate. |
| `write_log` | `core/system_logger.py:271` | Uncalled compatibility/helper candidate. |
| `get_timestamp` | `core/system_utils.py:160` | Uncalled utility candidate. |
| `get_unix_timestamp` | `core/system_utils.py:243` | Uncalled utility candidate. |
| `dbg_memory` | `core/system_debug.py:150` | Uncalled function inside the orphan module. |

These are **review candidates only**. Removing individual functions would be a code change/refactor and was outside this audit.

The local validator also flagged `api_installed_models`, `api_personality_traits`, and `api_greeting` as “unused.” Those are false positives: each is a Flask-decorated route handler, and `WebUI/index.html` fetches the corresponding endpoints. They are required and must not be treated as dead code.

## Duplicate and abandoned implementations

- Three server generations coexist: active `core/api_gateway.py`, broken `Scripts/API_Server.py`, and old `server.py` copies in `Scripts/Extras`.
- Multiple old “brain”, executor, memory, server, and frontend copies live under `Current_Stable`, `New Current backup`, and `old`.
- Exact duplicates:
  - `Scripts/Extras/FixHTML1Line.py` = `Scripts/Extras/New Current backup/static/FixHTML1Line.py`
  - `Scripts/Extras/index_formatted.html` = `Scripts/Extras/New Current backup/static/index_formatted.html`
- ZIP snapshots duplicate the active `core` and `WebUI` trees and are not referenced.
- Two n8n package layouts coexist. The root layout is the one consistent with active launch behavior; `Services/N8N` is used only by the old installer.
- Two settings layouts coexist. Active code targets `Data/Memory`; lowercase `memory/` is legacy.

# 13. Safe cleanup candidates

The following have strong static evidence for personal review. This is not an instruction to delete them.

## Highest-confidence inactive artifacts

- Empty/unreferenced folders: `.agents/`, `Backups/`, `TestShell/`, `Tools/`, `Users_Templates/`, plus the empty scaffolding under `Shared/`, `System/`, and `Users/`.
- Empty root files: `start.bat`, `readme.md` (replace README content if preparing GitHub).
- `Scripts/API_Server.py`.
- All of `Scripts/Extras/`.
- `Scripts/New_Backups/` ZIP files.
- Legacy batch installers: `0.AI_Project_Layout.bat`, `1.Ollama_Install.bat`, `2.Install_Aetheraeon_ENV.bat`, `First_Setup_AI.bat`.
- `Docs/lowercase_files.bat`.
- Existing `Data/Logs/install_*.log` outputs.
- Lowercase `memory/` legacy data, after confirming nothing external still relies on it.
- `Shared/SystemPrompts/SystemPrompt.txt` and `System/Settings/README.txt`, which have no reader.
- Non-excluded `Models/all-MiniLM-L6-v2/` and `Models/Pull_Models.txt`, after confirming the local model bundle is not wanted for offline/manual purposes.
- `Services/N8N/package.json` and `package-lock.json`, after confirming the root n8n layout is authoritative.

## Items to review carefully rather than treat as routine cleanup

- `Users/` contains personal/profile/session data even though it is unused. It is already broadly ignored by `.gitignore`; confirm no private data is staged or historically tracked.
- `.env` is locally required and must not be committed.
- `playbooks/*.json` are actively discovered but contain `H:\MQ2_Project` and “Sentimina” examples. Removing them changes the available playbook feature content; editing/replacing them is a product/content decision.
- `core/system_debug.py` is unused today, but it may have been retained intentionally as a manual diagnostic library.
- Root npm files are optional for the base app but required for the supported n8n integration.
- `Scripts/MemoryEditor.py` is not automatic, but it is a valid manual Chroma administration tool.
- `Scripts/OllamaSetup.exe` is a large ignored binary with unknown provenance in this source audit.

# 14. Unknown items requiring manual review

| Item | Why manual review is required |
|---|---|
| `.git/` | Local Git metadata was not usable as a repository during this audit. Determine whether this is an empty placeholder, incomplete copy, or workspace-specific state. Never copy `.git` as ordinary release content. |
| `.agents/` | Empty and unused by application code, but its intended relationship to local agent tooling cannot be inferred from project source. |
| `Users/James/**` | Unused by code, but ownership/privacy and archival value cannot be inferred. |
| `Scripts/OllamaSetup.exe` | Static source references show only the obsolete installer path; binary signature, source, and trust were not established. |
| `Models/all-MiniLM-L6-v2/` | Runtime does not reference it, but the owner may retain it for offline experiments outside the application. |
| `core/system_debug.py` | Orphaned by current imports, but may be intentionally retained for manual debugging. |

## Final folder inventory summary

Every non-excluded top-level folder is accounted for below:

| Status | Folders |
|---|---|
| **REQUIRED** | `core/`, `database/`, `WebUI/` |
| **REFERENCED** | `Data/`, `playbooks/`, `Services/` (path constant only; current bundled contents inactive) |
| **OPTIONAL** | `Docs/`, `Scripts/`, `.git/` (metadata/manual review) |
| **UNUSED / LEGACY** | `.agents/`, `Backups/`, `memory/`, `Models/` non-excluded content, `Shared/`, `System/`, `TestShell/`, `Tools/`, `Users/`, `Users_Templates/` |
| **EXCLUDED BY REQUEST** | `env/`, `node_modules/`, `chroma_memory/`, `__pycache__/` and the listed nested cache/model/vendor locations |

## Final root-file inventory summary

Every top-level file is accounted for below:

| File | Classification |
|---|---|
| `.env` | **REQUIRED LOCALLY; DO NOT COMMIT** |
| `.env.example` | **REQUIRED FOR DISTRIBUTION** |
| `.gitignore` | **REQUIRED FOR GITHUB SAFETY** |
| `AISystem_DIRECTORY_GUIDE.md` | **OPTIONAL / PARTLY STALE** |
| `dependency_validator.py` | **OPTIONAL DEVELOPMENT TOOL** |
| `package.json` | **OPTIONAL n8n MANIFEST** |
| `package-lock.json` | **OPTIONAL n8n LOCKFILE** |
| `readme.md` | **UNUSED EMPTY PLACEHOLDER** |
| `requirements.txt` | **REQUIRED** |
| `requirements-dev.txt` | **OPTIONAL DEVELOPMENT MANIFEST** |
| `start.bat` | **UNUSED EMPTY PLACEHOLDER** |

## Audit limitations

This is an evidence-based static repository audit. It cannot detect manually invoked files, external shortcuts, scheduled tasks, user workflows outside the repository, or intent to preserve archives. Flask decorators and package-manager conventions were explicitly accounted for to avoid obvious static-analysis false positives. No cleanup action was performed.

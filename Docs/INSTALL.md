# Aetheraeon AI installation (Windows)

This guide installs Aetheraeon AI on a clean Windows computer. Run all commands from PowerShell unless a step says otherwise. The tested runtime is Windows with Python 3.12, MariaDB, and Ollama.

## 1. Install prerequisites

Install these before cloning:

- Git for Windows 2.x: <https://git-scm.com/install/windows>
- Python 3.12 x64 (3.10 is the code/dependency minimum; 3.12 is recommended): <https://www.python.org/downloads/windows/>
- MariaDB Community Server 10.6 or newer (11.4 LTS recommended): <https://mariadb.org/download/>
- Ollama for Windows: <https://ollama.com/download/windows>

During Python setup, enable **Add Python to PATH**. During MariaDB setup, install the database instance as a Windows service, keep TCP enabled on port `3306`, and record the root password.

Node.js is only needed for the optional n8n automation feature. Aetheraeon's frontend has no Node build step.

## 2. Clone the repository

```powershell
git clone <repository-url> Aetheraeon-AI
Set-Location Aetheraeon-AI
```

Every remaining command assumes the repository root is the current directory. The application now resolves this directory dynamically and does not require an `H:` drive.

## 3. Create and activate a virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks activation, run this once in the same terminal and retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 4. Install Python runtime packages

```powershell
python -m pip install -r requirements.txt
```

Optional development/helper package:

```powershell
python -m pip install -r requirements-dev.txt
```

Verify the runtime imports:

```powershell
python -c "import bcrypt, chromadb, colorama, flask, mysql.connector, ollama, psutil, requests, waitress; from dotenv import load_dotenv; print('Python dependencies OK')"
```

## 5. Create the MariaDB database and account

Open the MariaDB client from the Start menu, or run:

```powershell
mariadb -u root -p
```

At the MariaDB prompt, replace the sample password and execute:

```sql
CREATE DATABASE aetheraeon
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'aetheraeon_app'@'127.0.0.1'
  IDENTIFIED BY 'replace_with_a_strong_database_password';

GRANT ALL PRIVILEGES ON aetheraeon.*
  TO 'aetheraeon_app'@'127.0.0.1';

FLUSH PRIVILEGES;
EXIT;
```

Import the schema from the repository. `cmd /c` is used because PowerShell does not implement input redirection with `<`:

```powershell
cmd /c "mariadb -u root -p aetheraeon < database\aetheraeon_schema.sql"
```

Verify all seven tables exist:

```powershell
mariadb -u root -p -D aetheraeon -e "SHOW TABLES;"
```

Expected tables are `users`, `user_settings`, `user_personality_traits`, `conversations`, `messages`, `memory`, and `logs`. No seed file is required: the first account registered through the web UI is promoted to administrator by the existing application logic.

## 6. Configure `.env`

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
notepad .env
```

Put the generated value in `SECRET_KEY`, and make `DB_PASS` match the MariaDB account password. The default values assume the database and account created above. Never commit `.env`.

Google Custom Search credentials are optional. Leave `GOOGLE_CSE_API_KEY` and `GOOGLE_CSE_CX` blank unless `Data\Memory\settings.json` is configured to use the `google_cse` provider. DuckDuckGo search does not require credentials.

## 7. Install Ollama and pull the configured models

Install Ollama from <https://ollama.com/download/windows>. Windows 10 22H2 or newer is required by Ollama. Verify its local API:

```powershell
ollama --version
ollama list
```

The repository defaults currently reference these three models:

```powershell
ollama pull qwen2.5-coder:14b
ollama pull gpt-oss:20b
ollama pull qwen2.5-coder:32b
```

These models require substantial disk space and memory. If the computer cannot run them, pull suitable alternatives first, start the application, and select the installed alternatives in Settings. The router model must exist for normal request routing. Ollama serves its API at `http://127.0.0.1:11434`.

## 8. Optional: install n8n automation

Skip this section if n8n workflows are not needed. Install Node.js 22 LTS (`>=22.16` is required by the locked n8n package): <https://nodejs.org/en/download>

From the repository root:

```powershell
node --version
npm --version
npm ci
npx n8n --version
npx n8n start
```

Complete n8n's first-run setup at <http://127.0.0.1:5678>. Keep this terminal open. Aetheraeon calls n8n webhooks only when an n8n tool/playbook is used.

## 9. Optional: install Aider code-agent support

The rest of Aetheraeon runs without Aider. To enable the `aider` tool:

```powershell
python -m pip install "aider-chat==0.86.2"
aider --version
```

Aider uses the already-required `qwen2.5-coder:14b` through Ollama by default.

## 10. Start the backend and frontend

Ensure the MariaDB Windows service and Ollama are running, activate the virtual environment, then start from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m core.api_gateway
```

The backend and static frontend start together on port `8080`. There is no separate frontend server or build command. Leave the backend terminal open and browse to:

<http://127.0.0.1:8080>

Register the first account, sign in, create a conversation, and send a message.

## 11. Verify the installation

In a second PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/status
Invoke-RestMethod http://127.0.0.1:11434/api/tags
Test-NetConnection 127.0.0.1 -Port 3306
```

Also verify that `chroma_memory\` is created after startup and that the web UI can register/login, create a conversation, and receive an Ollama response.

## Optional Apache frontend hosting

The normal installation does not require Apache: Flask serves `WebUI\index.html`, `/css/aetheraeon.css`, and `/js/aetheraeon.js` directly. If Apache is used for public hosting, serve `WebUI\` as the site document root and reverse-proxy only `/api/` to the local Flask service.

Example Apache directives for a Windows installation:

```apache
DocumentRoot "H:/AISystem/WebUI"

<Directory "H:/AISystem/WebUI">
    Options -Indexes
    AllowOverride None
    Require all granted
</Directory>

ProxyPass        /api/ http://127.0.0.1:8080/api/
ProxyPassReverse /api/ http://127.0.0.1:8080/api/
```

Enable `mod_proxy`, `mod_proxy_http`, `mod_headers`, and `mod_ssl` as appropriate for the Apache installation. Keep Flask bound behind the reverse proxy, configure HTTPS with a real certificate, and preserve same-origin session cookies. Do not expose MariaDB, Ollama, ChromaDB data, `.env`, or the repository root as public files.

When Apache is online but Flask is stopped, the login screen displays the backend-offline message and disables authentication. It automatically restores the login button after `/api/status` becomes reachable again.

## Troubleshooting

- `Can't connect to MySQL server`: start the MariaDB service and recheck `DB_HOST`, `DB_PORT`, and credentials in `.env`.
- `Table ... doesn't exist`: repeat the schema import against the same database named by `DB_NAME`.
- `Ollama ... model not found`: run `ollama list`, then pull or select the configured router/chat/code models.
- `npx` or `node` not found: install Node.js 22 LTS, reopen PowerShell, and rerun `npm ci` from the repository root.
- Port already in use: stop the other process using `8080`, `11434`, `5678`, or `3306`. These ports are currently fixed by the application or their respective services.
- Do not run `Scripts\API_Server.py`; it is an incomplete legacy fragment and is not the application entry point.

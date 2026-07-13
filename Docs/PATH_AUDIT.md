# Hardcoded path audit

The repository was scanned for Windows drive paths, user-profile paths, home-directory paths, AppData, and temporary-folder references. Generated/vendor trees (`env`, both `node_modules` trees, bundled Ollama binaries, model blobs, and Chroma binary indexes) were excluded from text-path analysis.

## Distinct path literals found

| Literal or family | Where found | Classification |
|---|---|---|
| `H:\AISystem` | Active help examples, old installers, directory guide, command-registration note | Runtime root was fixed; remaining uses are examples/legacy |
| `H:\Aetheraeon\AI` and `H:\Aetheraeon\AI\chroma_memory` | `Scripts\First_Setup_AI.bat`, former MemoryEditor default, old requirements comment | Legacy; active editor path was fixed |
| `H:\Sentimina\AI` plus its `Ollama`, `node_modules\n8n`, and `chroma_memory` children | Extras/setup and registry backup files | Historical/private backup |
| `H:\MQ2_Project`, `H:\MQ2_Project\E3`, and `H:\MQ2_Project\test.py` | User session/memory, playbooks, setup tests, help examples | User data/example |
| Generic `H:\MQ2`, `H:\Foo`, `H:\path`, `H:\cfg.ini`, and `H:\MyProject` | Historical help prompts and HTML examples | Example only |
| `C:\Windows` and `C:\MQ2_Project` | Setup/parser/help examples | Example only |
| `C:\Temp` and `C:\Temp\file.txt` | Security/path parser comments | Example only |
| `D:\Data\a.txt` | Path parser comment | Example only |
| `E:\Backup` | Path parser comment | Example only |
| `%TEMP%\pylist.txt` | `core\PY_Files_Names.bat` | Portable Windows temporary path |
| `HKCU:\Software\Microsoft\Command Processor` | `Scripts\CreateCMDCommand.txt` | PowerShell registry-provider path, not a filesystem dependency |

No literal `C:\Users\<developer>`, `/Users/<developer>`, or `/home/<developer>` path was found in non-vendor project text.

## Portability fixes made

- `core\system_paths.py`: replaced `H:\AISystem` with the directory derived from the file location. All active core data/UI/service paths now follow the clone location.
- `dependency_validator.py`: validator core and virtual-environment paths now follow the clone location.
- `Scripts\MemoryEditor.py`: Chroma path now uses the central project root.
- `Scripts\Emojii_Finder.py`: accepts a command-line directory and otherwise scans the project root.

## Remaining active-code matches

The remaining matches in active `core` files are documentation/examples, not machine-bound storage configuration:

- `core\tool_executor.py`: help examples use `H:\AISystem`.
- `core\system_utils.py`: parser comments demonstrate `C:\Temp`, `D:\Data`, and `E:\Backup`.
- `core\system_security.py`: validation comments demonstrate `C:\Temp` and generic drive-letter paths.

These examples intentionally demonstrate Windows path parsing and do not control runtime locations.

## Machine-specific data files

- `memory\memory.json`: legacy state contains `H:\MQ2_Project`.
- `Users\James\Session\SessionState.json`: private session paths point to `H:\MQ2_Project`.
- `playbooks\open_mq2.json` and `playbooks\test_sentimina.json`: user-authored sample targets point to `H:\MQ2_Project`.
- `Scripts\Extras\registry_backup_aetheraeon.json`: private machine registry backup contains `H:\Sentimina\AI` paths for Ollama, n8n, and Chroma.

These files are user/session/example data rather than application configuration. They were not rewritten because doing so would alter user content. Private runtime files and the registry backup should not be committed; playbooks must be sanitized or replaced with portable examples before publication.

## Legacy/setup/documentation matches

- `AISystem_DIRECTORY_GUIDE.md`: identifies the old `H:\AISystem` layout.
- `Scripts\0.AI_Project_Layout.bat`, `Scripts\1.Ollama_Install.bat`, and `Scripts\2.Install_Aetheraeon_ENV.bat`: assume installation at `H:\AISystem`.
- `Scripts\First_Setup_AI.bat`: assumes `H:\Aetheraeon\AI` and includes `H:\MQ2_Project`/`C:\Windows` test examples.
- `Scripts\CreateCMDCommand.txt`: registry command assumes `H:\AISystem`.
- `Scripts\Extras\Current_Stable\Setup_AI.bat`, `memory.py`, `test.py`, old/current backup Python and HTML files: historical code assumes `H:\Sentimina\AI`, `H:\MQ2_Project`, or generic `C:\Windows` paths.
- `core\PY_Files_Names.bat`: uses `%TEMP%`, which is a portable Windows environment variable and is safe.

The legacy installers were not made authoritative because they also encode obsolete startup commands and duplicated installation layouts. Follow `Docs\INSTALL.md` for a clean install.

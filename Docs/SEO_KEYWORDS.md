# Aetheraeon AI SEO Keywords

This document defines accurate search terminology for Aetheraeon AI. Keywords should appear naturally in useful project descriptions; they should not be repeated solely to influence rankings.

## Primary keywords

| Keyword | Why it applies | Natural placement |
|---|---|---|
| Aetheraeon AI | Official project and application name | Page title, main heading, README title, Open Graph title, structured data |
| self-hosted AI assistant | The operator installs and runs the application and its supporting services | HTML description, README overview, installation documentation |
| personal AI assistant | The application provides authenticated conversations, memory, personality, and personal settings | HTML description, README overview and features |
| local AI assistant | Ollama models run through a locally configured model service | README local AI and Ollama sections |
| private AI assistant | Application, database, model service, and memory can be operated on the user's machine | README overview and security discussion; avoid absolute privacy guarantees |
| local LLM assistant | Ollama provides locally served language models | HTML keywords, README architecture and local AI sections |
| Ollama AI | Ollama is the active local model service | README Ollama section and dependency documentation |

## Secondary keywords

| Keyword | Why it applies | Natural placement |
|---|---|---|
| open source AI assistant | Appropriate when the repository is published with a suitable open-source license | Repository description and README only after a license is added |
| AI memory system | ChromaDB and MariaDB provide persistent memory and application data | README memory section and technical documentation |
| AI personality system | Users can configure style, tone, detail, humor, greeting style, and traits | README personality section and feature descriptions |
| conversational AI | The primary WebUI provides managed conversations and messages | Feature summary and application metadata |
| AI automation system | Playbooks and optional n8n integration provide automation features | README features and architecture documentation |
| persistent AI memory | ChromaDB entries persist locally between sessions | Memory documentation |
| self-hosted conversational AI | Accurately combines the hosting model and chat interface | Repository description or longer overview copy |
| local AI memory manager | The WebUI includes create, search, edit, delete, import, and export controls for Chroma memory | Feature documentation or sanitized screenshots |

## Current placement

- `WebUI/index.html` uses the project name and concise primary terms in the title, description, keyword metadata, Open Graph metadata, Twitter summary metadata, and JSON-LD.
- `readme.md` uses the primary terms in the overview, features, architecture, local AI, Ollama, memory, personality, and security sections.
- `Docs/INSTALL.md`, `Docs/DEPENDENCIES.md`, and `Docs/CONFIGURATION.md` provide detailed supporting content for installation and technical queries.

## Usage guidance

- Prefer one precise phrase over a list of near-duplicates in visible prose.
- Describe actual capabilities only; do not claim autonomy, training, guaranteed privacy, or cloud independence beyond what the deployment supports.
- Do not claim the project is open source until a license granting those permissions is committed.
- Do not invent a canonical URL, social profile, download count, review score, pricing, or organization name.
- Add `og:url`, canonical URL, and social preview images only after stable public URLs and sanitized assets exist.
- Keep titles and descriptions readable for people first.

# Aetheraeon AI — Persistence Database Architecture

## File

`memory_database.py`

## Architecture Layer

**Persistence Layer**

## Current Status

Active Implementation  
Planned Future Repository Migration

---

# Purpose

`memory_database.py` is the current central persistence module
for the Aetheraeon AI system.

It provides the storage interface between the AI architecture
and persistent data systems.

Currently this module manages:

- User accounts
- Conversations
- Messages
- User settings
- Automation playbooks
- Long-term semantic memory
- ChromaDB vector memory

This file is intentionally designed for future decomposition
into smaller repository modules as the system grows.

---

# System Role

## Persistence Layer

The responsibility of this layer is:

- Store information
- Retrieve information
- Update persistent records
- Delete persistent records
- Communicate with storage systems
- Return structured data to higher layers

This layer does not create intelligence.

It provides the memory foundation that allows intelligence
layers to maintain continuity.

---

# Architecture Position

Current architecture:

```
AI Intelligence Layers

        ↓

memory_interface.py

        ↓

memory_database.py

        ↓

MariaDB + ChromaDB

        ↓

Persistent Storage
```

---

# Current Responsibilities

## MariaDB Persistence

Handles structured application data:

- User accounts
- User settings
- Conversations
- Messages
- Automation playbooks
- Metadata

---

## ChromaDB Semantic Memory

Handles AI long-term memory:

- Memory storage
- Vector embeddings
- Semantic recall
- Similarity search
- Memory updates
- Memory deletion

---

# Current Function Groups

## User Management

Responsible for user persistence.

Functions:

- `create_user()`
- `get_user_by_id()`
- `get_user_by_email()`
- `get_user_by_username()`
- `update_last_login()`
- `update_username()`
- `update_password()`
- `delete_user()`

---

## User Settings

Responsible for user configuration storage.

Functions:

- `get_user_settings()`
- `upsert_user_settings()`

---

## Conversation Management

Responsible for conversation persistence.

Functions:

- `create_conversation()`
- `get_conversations()`
- `rename_conversation()`
- `delete_conversation()`
- `pin_conversation()`

---

## Message Storage

Responsible for storing conversation messages.

Functions:

- `save_message_user()`
- `save_message_ai()`
- `get_messages()`
- `search_messages()`

---

## Automation Playbook Storage

Responsible for automation workflow persistence.

Functions:

- `get_playbooks()`
- `save_playbook()`
- `update_playbook()`
- `delete_playbook()`

---

## Semantic Memory Storage

Responsible for ChromaDB memory operations.

Functions:

- `chroma_store()`
- `chroma_recall()`
- `chroma_recall_with_meta()`
- `chroma_get_by_type()`
- `chroma_get_all()`
- `chroma_update_by_id()`
- `chroma_delete_by_id()`
- `chroma_exists_similar()`

---

# Strict Boundaries

## This File SHOULD:

- Handle database communication
- Perform persistence operations
- Return structured storage results
- Manage storage-related errors

---

## This File MUST NOT:

- Perform AI reasoning
- Generate AI responses
- Decide user intent
- Execute external tools
- Handle frontend requests
- Manage UI state
- Select AI models
- Build AI context
- Perform memory interpretation

---

# Data Flow

```
Application Request

        ↓

memory_interface.py

        ↓

memory_database.py

        ↓

MariaDB / ChromaDB

        ↓

Structured Result

        ↓

Calling Layer
```

---

# Relationship With Memory System

Aetheraeon memory is separated into multiple layers.

```
Raw Storage

(memory_database.py)

        ↓

Memory Organization

(memory_context_builder.py)

        ↓

AI Understanding

(ai_orchestrator.py)
```

---

# Future Architecture Migration

## Current Design

Currently:

```
memory_interface.py

        ↓

memory_database.py

        ↓

Storage Engines
```

---

## Target Design

Future repository structure:

```
database/

│
├── database_connection.py
│       MariaDB connection management
│
├── user_repository.py
│       User accounts and profiles
│
├── conversation_repository.py
│       Conversations and messages
│
├── settings_repository.py
│       User settings
│
├── playbook_repository.py
│       Automation playbooks
│
└── memory_repository.py
        ChromaDB semantic memory
```

---

# Future Access Pattern

```
AI Layers

        ↓

memory_interface.py

        ↓

Repository Layer

        ↓

Database Connection Layer

        ↓

MariaDB / ChromaDB
```

---

# Migration Goals

The repository migration will:

- Reduce module size
- Improve maintainability
- Separate responsibilities
- Improve testing
- Reduce coupling
- Make storage engines replaceable
- Keep AI layers independent from databases

---

# Migration Rules

When refactoring:

1. Keep `memory_interface.py` as the abstraction boundary.
2. Move one responsibility at a time.
3. Preserve existing behavior.
4. Avoid changing AI layer code unnecessarily.
5. Keep database details hidden from intelligence layers.

---

# Layer Responsibility Map

| Layer | Responsibility |
|---|---|
| `ai_orchestrator.py` | Reasoning and AI coordination |
| `core_cognition.py` | Cognitive processing |
| `memory_context_builder.py` | Memory interpretation and context creation |
| `memory_interface.py` | Memory access abstraction |
| `memory_database.py` | Current persistence implementation |
| Repository Layer | Future storage separation |
| MariaDB | Structured persistent storage |
| ChromaDB | Semantic vector memory |

---

# Design Philosophy

## "The Database Remembers. The AI Understands."

The persistence layer stores experience.

The memory layer organizes experience.

The cognition layer interprets experience.

The orchestrator combines understanding into intelligent behavior.

Aetheraeon AI maintains separation between:

```
Storage

↓

Memory

↓

Understanding

↓

Reasoning

↓

Action
```

This separation allows the system to grow into a scalable,
modular cognitive architecture.
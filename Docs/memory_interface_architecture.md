# Aetheraeon AI — Memory Interface Architecture

## File

`memory_interface.py`

## Architecture Layer

**Memory Access Abstraction Layer**

## Current Status

Active Core Architecture Component

Future Storage Migration Boundary

---

# Purpose

`memory_interface.py` is the unified memory and persistence
access layer for the Aetheraeon AI system.

It provides a stable interface between intelligence layers
and underlying storage systems.

Higher-level AI components should communicate through this
layer instead of directly accessing:

- MariaDB
- ChromaDB
- Repository implementations
- Storage engines

This protects the AI architecture from storage changes.

---

# System Role

## Memory Access Gateway

The responsibility of this layer is:

- Provide memory access functions
- Provide persistence access functions
- Normalize storage responses
- Hide storage implementation details
- Maintain clean architecture boundaries

This layer does not create intelligence.

It provides controlled access to stored information.

---

# Core Architecture Principle

## "The AI Should Know Memory, Not Storage"

The intelligence system should understand:

- What information it needs
- How to request memory
- How to use returned context

The intelligence system should NOT need to know:

- Database type
- Table structure
- Query logic
- Storage implementation

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

# Future Architecture

Target:

```
AI Intelligence Layers

        ↓

memory_interface.py

        ↓

Repository Layer

        ↓

Database Connection Layer

        ↓

MariaDB / ChromaDB
```

The interface remains stable while storage components
can evolve underneath.

---

# Responsibilities

## Memory Access

Provides:

- Memory storage
- Memory retrieval
- Memory updates
- Memory deletion
- Similarity checking

---

## Conversation Access

Provides:

- Conversation creation
- Conversation deletion
- Conversation management

---

## Message Access

Provides:

- User message storage
- AI message storage

---

## User Settings Access

Provides:

- User configuration retrieval
- User configuration updates

---

## Persistence Translation

Converts storage operations into normalized results
that higher layers can safely consume.

---

# Strict Boundaries

## This File MAY:

- Call persistence providers
- Translate storage requests
- Normalize returned data
- Provide memory access functions

---

## This File MUST NOT:

- Perform AI reasoning
- Generate responses
- Execute tools
- Handle HTTP requests
- Manage UI state
- Build prompts
- Perform cognitive processing
- Implement database engines

---

# Data Flow

```
AI Request

        ↓

ai_orchestrator.py

        ↓

memory_interface.py

        ↓

Storage Provider

        ↓

MariaDB / ChromaDB

        ↓

Normalized Data

        ↓

AI System
```

---

# Relationship With Memory System

Aetheraeon memory is divided into multiple layers.

```
Storage Layer

memory_database.py

        ↓

Access Layer

memory_interface.py

        ↓

Context Layer

memory_context_builder.py

        ↓

Intelligence Layer

ai_orchestrator.py
```

---

# Current Storage Provider

Currently:

```
memory_interface.py

        ↓

memory_database.py
```

`memory_database.py` currently provides:

- MariaDB operations
- ChromaDB operations
- Persistence functions

---

# Future Repository Integration

The future architecture:

```
memory_interface.py

        ↓

database/

├── database_connection.py

├── user_repository.py

├── conversation_repository.py

├── settings_repository.py

├── playbook_repository.py

└── memory_repository.py
```

The interface should remain unchanged during migration.

---

# Current Function Groups

## Memory State

Functions:

- `get_memory_state()`
- `update_memory_state()`

---

## Conversations

Functions:

- `create_conversation()`
- `delete_conversation()`
- `pin_conversation()`

---

## Messages

Functions:

- `save_message_user()`
- `save_message_ai()`

---

## User Settings

Functions:

- `get_user_settings()`

---

## Semantic Memory

Functions:

- `memory_store()`
- `memory_recall()`
- `memory_update()`
- `memory_delete()`
- `memory_exists_similar()`

---

## Memory Persistence

Functions:

- `load_memory()`
- `save_memory()`

---

## Utilities

Functions:

- `extract_memory_text()`

---

# Layer Responsibility Map

| Layer | Responsibility |
|---|---|
| `ai_orchestrator.py` | Reasoning and AI coordination |
| `memory_interface.py` | Memory access abstraction |
| `memory_context_builder.py` | Memory organization and context creation |
| `memory_database.py` | Current storage implementation |
| Repository Layer | Future storage separation |
| MariaDB | Structured data storage |
| ChromaDB | Semantic vector memory |

---

# Migration Goals

The abstraction layer allows:

- Database refactoring without AI changes
- Storage engine replacement
- Cleaner testing
- Better debugging
- Reduced coupling
- Scalable memory architecture

---

# Design Philosophy

## "Memory Is a Service, Not a Database"

Aetheraeon AI should interact with memory through
meaningful operations, not storage mechanics.

The separation is:

```
Database stores

↓

Memory Interface provides access

↓

Context Builder organizes

↓

Cognition understands

↓

Orchestrator reasons
```

This design allows Aetheraeon AI to develop a scalable,
modular, human-like cognitive architecture while keeping
storage systems replaceable.
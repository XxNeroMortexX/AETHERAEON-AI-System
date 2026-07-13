# Aetheraeon AI — Request Router Specification

## Component

`request_router.py`

## Architecture Layer

**System Routing and Decision Flow Layer**

---

# Purpose

The Request Router is the traffic control system of the Aetheraeon AI architecture.

It receives normalized requests from the API layer and determines which internal subsystem should handle the request.

The router does not solve problems.

It does not generate responses.

It determines the correct path through the architecture.

---

# System Role

**"Traffic Control Layer"**

The Request Router is responsible for:

- Request classification
- Execution path selection
- System flow coordination
- Command routing
- Intent categorization

It acts as the connection point between incoming requests and specialized system components.

---

# Responsibilities

`request_router.py` is responsible for:

- Classifying incoming user requests
- Detecting request categories
- Identifying memory-related requests
- Identifying tool-related requests
- Identifying system commands
- Determining whether AI reasoning is required
- Preparing routing information
- Maintaining separation between system layers

---

# Architecture Boundaries

## This File MUST NOT:

- Perform deep AI reasoning
- Generate AI responses
- Execute tools directly
- Access databases directly
- Handle HTTP requests
- Modify frontend state
- Store persistent memory
- Perform model inference

The Request Router only decides where requests should go.

---

# Separation of Responsibilities

```
User Input
      |
      v
api_gateway.py
      |
      v
request_router.py
      |
      |
      +----------------------+
      |          |           |
      v          v           v

ai_orchestrator.py
tool_executor.py
memory_interface.py

      |
      v

Structured Result
      |
      v

api_gateway.py
      |
      v

Web UI
```

---

# Internal Flow

```
Incoming Request
        |
        v
clean_input()
        |
        v
classify_request()
        |
        v
Determine Request Domain
        |
        |
        +----------------+
        |                |
        v                v

AI Request          System Request

        |                |
        v                v

ai_orchestrator    Specialized Handler

        |
        v

Return Routing Result
```

---

# Core Functions

## `classify_request(user_input: str)`

Purpose:

Analyzes incoming user input and determines the general request category.

Returns routing information used by the system pipeline.

---

## `fast_path_intent(user_input: str)`

Purpose:

Detects simple commands or requests that can bypass the full AI reasoning pipeline.

Used for fast execution paths.

---

## `classify_memory_domain(user_input: str)`

Purpose:

Determines whether a request relates to a memory operation.

Examples:

- memory recall
- memory storage
- memory updates
- memory management

---

## `clean_input(text)`

Purpose:

Normalizes incoming text before routing decisions are made.

Handles input cleanup required for consistent classification.

---

# Dependencies

## Used By:

- `api_gateway.py`

---

## Connects With:

- `ai_orchestrator.py`
- `tool_executor.py`
- `memory_interface.py`
- `help_system.py`
- `model_registry.py`

---

# Output Contract

The Request Router returns structured routing information.

Example:

```json
{
    "route": "ai",
    "requires_tool": false,
    "requires_memory": true,
    "metadata": {}
}
```

---

# Design Philosophy

## "Centralized Routing, Decentralized Execution"

The router controls movement, not intelligence.

Architecture separation:

```
request_router.py
        |
        | Routes
        v

ai_orchestrator.py
        |
        | Thinks
        v

core_cognition.py


tool_executor.py
        |
        | Acts
        v

external_toolkit.py


memory_interface.py
        |
        | Retrieves
        v

memory_database.py
```

---

# Future Expansion

The Request Router is designed to support:

- More specialized AI agents
- Advanced intent classification
- Multi-agent routing
- Priority handling
- Request scheduling
- Context-aware routing
- Dynamic workflow selection

---

# Architectural Rules

The Request Router must remain:

- Lightweight
- Predictable
- Independent from reasoning
- Independent from execution
- Easy to debug
- Focused only on routing decisions

Aetheraeon AI should have one clear traffic controller, while each specialized layer remains responsible for its own purpose.
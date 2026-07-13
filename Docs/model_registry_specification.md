# Aetheraeon AI — Model Registry Specification

## Component

`model_registry.py`

## Architecture Layer

**Model Management Layer**

---

# Purpose

The Model Registry is the centralized system responsible for discovering, tracking, and selecting AI models available to the Aetheraeon AI architecture.

It provides a controlled interface for model information and selection decisions without performing model execution.

The registry exists to prevent model selection logic from being duplicated across the system.

---

# System Role

**"Model Discovery + Capability Registry Layer"**

The Model Registry provides information about:

- Available AI models
- Model capabilities
- Model naming normalization
- Model availability
- Default model selection
- Model routing preferences

The Model Registry does NOT perform reasoning or generate responses.

It only provides structured model information to the systems responsible for AI execution.

---

# Responsibilities

`model_registry.py` is responsible for:

- Discovering available models
- Reading available Ollama models
- Normalizing model names
- Matching models by capability
- Selecting appropriate default models
- Handling model availability checks
- Supporting multi-model architecture
- Providing model status information
- Supporting future model providers

---

# Architecture Boundaries

## This File MUST NOT:

- Execute LLM requests
- Call model inference directly
- Generate AI responses
- Perform reasoning
- Build prompts
- Store memory
- Access databases
- Execute tools
- Handle frontend/API requests

---

# Separation of Responsibilities

```
User Request
      |
      v
api_gateway.py
      |
      v
request_router.py
      |
      v
ai_orchestrator.py
      |
      |
      +----------------+
      |                |
      v                |
model_registry.py     |
      |                |
      v                |
Selected Model        |
Configuration         |
      |                |
      +----------------+
               |
               v
       llm_interface.py
               |
               v
          AI Model
```

---

# Internal Flow

```
AI Request
      |
      v
Check Available Models
      |
      v
Normalize Model Names
      |
      v
Evaluate Model Tags / Capabilities
      |
      v
Select Matching Model
      |
      v
Return Model Information
      |
      v
llm_interface.py
```

---

# Core Functions

## `ollama_models()`

Purpose:

Retrieves the available Ollama models currently installed on the system.

Returns available model names for selection and validation.

---

## `_normalize_model_name()`

Purpose:

Normalizes model names into a consistent internal format.

Used to prevent mismatches between:

- Ollama model names
- Configuration names
- User commands

---

## `pick_default_models_from_tags()`

Purpose:

Selects appropriate default models based on available model capabilities and tags.

Supports selecting models for different roles such as:

- General conversation
- Coding
- Reasoning
- Specialized tasks

---

## `_find_first_matching_model()`

Purpose:

Internal helper used to locate the first model matching a required capability or selection rule.

---

## `handle_model_command()`

Purpose:

Handles model-related user commands.

Examples:

- Checking current model information
- Displaying available models
- Managing model selection commands

---

## `build_model_status_display()`

Purpose:

Creates formatted model status information for display.

---

# Dependencies

## Used By:

- `ai_orchestrator.py`
- `llm_interface.py`
- `request_router.py`

---

## Depends On:

- `config_loader.py`
- Ollama local model environment
- System configuration data

---

# Output Contract

The Model Registry returns structured model information.

Example:

```json
{
    "model": "model_name",
    "available": true,
    "provider": "ollama",
    "capabilities": [
        "chat",
        "coding",
        "reasoning"
    ]
}
```

---

# Design Philosophy

## "The Registry Chooses the Engine, Not the Thought"

The Model Registry does not make the AI intelligent.

It provides the correct intelligence engine for the task.

Architecture separation:

```
core_cognition.py
        |
        |  Cognitive processing
        v

ai_orchestrator.py
        |
        |  Decision and workflow control
        v

model_registry.py
        |
        |  Model selection
        v

llm_interface.py
        |
        |  Model communication
        v

AI Model
```

---

# Future Expansion

The Model Registry is designed to support:

- Multiple local models
- Cloud model providers
- Automatic model switching
- Capability-based routing
- Hardware-aware model selection
- Performance-based optimization
- Specialized AI agents

---

# Architectural Rules

The Model Registry must remain:

- Centralized
- Predictable
- Stateless
- Independent from reasoning
- Independent from execution
- Easy to debug

Aetheraeon AI should always understand:

**Which intelligence engine is available, without confusing the engine with the intelligence system itself.**
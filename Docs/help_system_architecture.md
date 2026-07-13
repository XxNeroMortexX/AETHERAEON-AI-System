# Aetheraeon AI - Help System Architecture

## Document Purpose

This document defines the architecture, responsibilities, and boundaries of the **Help System Layer** within Aetheraeon AI.

The Help System provides a centralized mechanism for generating dynamic documentation from the system itself.

Rather than relying on manually written help pages, the Help System builds documentation directly from registered tool metadata, ensuring that user guidance remains synchronized with the capabilities of the AI.

---

# Component Overview

## File

```text
help_system.py
```

## Layer

```text
Knowledge & Documentation Layer
```

## System Role

The Help System provides self-documentation for Aetheraeon AI.

It transforms structured metadata into readable documentation for:

* Users
* Developers
* AI prompt context
* Debugging tools

The Help System never controls the system.

It only explains it.

---

# Core Design Principle

## Documentation Without Execution

Aetheraeon separates documentation from execution.

The Help System describes system capabilities.

It never performs them.

Architecture separation:

```text
Tool Registry

        ▼

Help System

        ▼

Formatted Documentation

        ▼

User / AI / Developer
```

This keeps documentation synchronized with the actual architecture while maintaining strict separation of responsibilities.

---

# Primary Responsibilities

## Dynamic Documentation

Generates documentation directly from registered tool metadata.

This eliminates duplicated documentation and reduces maintenance overhead.

---

## Tool Discovery

Provides an organized view of available tools and their capabilities.

This allows both users and AI components to understand what functionality exists without inspecting source code.

---

## Metadata Organization

Groups and structures tool information into a consistent format suitable for display and prompting.

---

## AI Context Support

Produces structured documentation that can be included in AI prompts to improve tool awareness and capability discovery.

---

## Developer Support

Provides a centralized view of registered tools for debugging, validation, and architectural inspection.

---

# Architectural Boundaries

## The Help System MUST NOT

---

## Execute Tools

Tool execution belongs to:

```text
tool_executor.py
```

---

## Perform AI Reasoning

Reasoning belongs to:

```text
ai_orchestrator.py
core_cognition.py
```

---

## Modify Memory

Persistent memory belongs to:

```text
memory_database.py
```

---

## Change System Configuration

Configuration belongs to:

```text
config_loader.py
config_manager.py
```

---

## Perform External Communication

External communication belongs to:

```text
external_toolkit.py
```

---

# Documentation Generation Flow

```text
Tool Registry

        ▼

build_help()

        ▼

Structured Help Data

        ▼

format_help_output()

        ▼

Formatted Documentation

        ▼

User / AI / Developer
```

---

# System Position

Within the overall Aetheraeon architecture:

```text
Tool Registry

      ▼

help_system.py

      ▼

Formatted Help

      ▼

AI Context

      ▼

User Interface / Developer Tools
```

The Help System is invoked only when documentation or capability information is requested.

---

# Dependencies

The Help System works closely with:

| Component          | Purpose                                                |
| ------------------ | ------------------------------------------------------ |
| `tool_registry.py` | Provides registered tool metadata                      |
| `tool_executor.py` | Referenced for execution context (no direct execution) |
| `json_helpers.py`  | Assists with structured formatting when required       |

---

# Core Functions

Primary functions within this component:

| Function               | Purpose                                                                                      |
| ---------------------- | -------------------------------------------------------------------------------------------- |
| `build_help()`         | Builds a structured representation of available tools using metadata from the Tool Registry. |
| `format_help_output()` | Converts structured help information into a readable, formatted documentation output.        |

---

# Output Contract

The Help System returns structured documentation.

Example:

```text
Help Output

├── Tool Categories
│
├── Tool Descriptions
│
├── Usage Information
│
└── Formatted Documentation
```

The output is intended for display and reference rather than execution.

---

# Relationship With Aetheraeon AI Architecture

The Help System acts as the documentation interface for the platform.

Architecture model:

```text
System Capabilities

        ▼

Metadata

        ▼

Help System

        ▼

Knowledge

        ▼

Users & Developers
```

This allows Aetheraeon AI to explain its own capabilities while preserving strict architectural boundaries.

---

# Future Expansion

Potential future capabilities include:

* Interactive help search
* Context-aware documentation
* Automatic API reference generation
* Architecture visualization
* Markdown and HTML documentation export
* Developer introspection tools

Future enhancements should preserve the component's primary responsibility:

**Explain the system without controlling it.**

---

# Summary

The Help System provides the self-documentation layer of Aetheraeon AI.

Its purpose is to:

* Build documentation from tool metadata
* Organize system capabilities
* Support AI prompting
* Assist developers and users

Its defining principle:

> The Help System describes what Aetheraeon can do. It never performs the work itself.

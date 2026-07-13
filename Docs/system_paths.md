# AETHERAEON — SYSTEM PATH MANAGEMENT LAYER

## File Purpose

`system_paths.py` is responsible for centralized filesystem path management across the Aetheraeon AI system.

It provides a single location for system directory definitions, file locations, and shared path references so other modules do not contain duplicated hardcoded paths.

This file helps maintain:

- Consistent directory structure
- Reliable file location references
- Easier system migration and maintenance
- Cleaner module separation

---

# System Role

## "Path Reference + Directory Configuration Layer"

This module does not perform AI reasoning.

This module does not execute commands.

This module does not control file operations.

It only provides and manages known system path definitions.

---

# Current Responsibilities

`system_paths.py` currently handles:

- Centralized path constants
- AI system root directory references
- Configuration file locations
- Database/storage locations
- Runtime directory references
- Shared filesystem location management

---

# Strict Boundaries

`system_paths.py` MUST NOT:

- Execute shell commands
- Modify files directly
- Perform AI reasoning
- Access databases
- Execute tools
- Handle API requests
- Manage user requests
- Perform security enforcement

This module only defines and provides path information.

---

# Architecture Position

Current flow:

```
Any System Module
        |
        ↓
system_paths.py
        |
        ↓
Returns known path locations
        |
        ↓
Calling module performs its own operation
```

---

# System Usage

Used by modules that require centralized locations:

- config_loader.py
- config_manager.py
- memory_database.py
- system_logger.py
- tool execution layers
- storage systems
- runtime services

---

# Future Evolution

As Aetheraeon grows, path handling may be expanded into a dedicated security-aware filesystem layer.

Possible future responsibilities:

- Path validation
- Directory boundary enforcement
- Sandbox protection
- Permission checking
- Safe file access policies
- Protection against unsafe external paths

These security responsibilities should eventually belong to:

```
system_security.py
```

rather than this file.

---

# Design Philosophy

## "One Source of Truth for System Locations"

The purpose of this layer is:

- Centralize paths
- Reduce duplication
- Improve maintainability
- Keep architecture organized

Other modules should ask:

"Where is this resource located?"

They should not hardcode:

"Where do I think this resource is located?"

---

# Future Architecture Goal

```
system_paths.py
        |
        ├── Defines locations
        |
        └── Provides references


system_security.py
        |
        ├── Validates access
        |
        └── Protects filesystem boundaries
```

---

# Summary

`system_paths.py` is a foundational utility layer that keeps Aetheraeon's filesystem organization consistent.

It should remain simple, predictable, and focused only on path management.
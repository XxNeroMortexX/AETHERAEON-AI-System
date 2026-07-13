# AETHERAEON — System Health Monitor

## Overview

The **System Health Monitor** is responsible for monitoring the operational health of the Aetheraeon AI platform.

Unlike the AI Orchestrator, this component does **not** perform reasoning, make decisions, or execute user requests.

Its responsibility is to continuously verify that all critical services required by the AI architecture are available, responsive, and operating correctly.

It serves as the centralized diagnostics and readiness layer for the system.

---

# Purpose

The System Health Monitor exists to answer one question:

> **"Is every required part of Aetheraeon operating correctly?"**

Rather than performing work itself, this component validates the health of the services that other components depend upon.

This allows startup validation, runtime monitoring, diagnostics, and future self-healing capabilities without mixing monitoring logic into the rest of the architecture.

---

# Responsibilities

The System Health Monitor is responsible for:

- Verifying core service availability
- Monitoring AI model connectivity
- Checking database connectivity
- Validating vector memory availability
- Monitoring external integrations
- Detecting degraded system states
- Collecting diagnostic information
- Reporting system readiness
- Supporting startup validation
- Supporting runtime health monitoring

---

# Architecture Role

The System Health Monitor is the **Diagnostics Layer** of the Aetheraeon architecture.

It does **not** perform AI reasoning.

It does **not** execute tools.

It does **not** modify application state.

Its only responsibility is to observe and report system health.

---

# Design Boundaries

This component **MUST**:

- Monitor system components
- Verify service availability
- Report health status
- Aggregate diagnostics
- Return structured health information

This component **MUST NOT**:

- Perform AI reasoning
- Execute tools
- Modify databases
- Change configuration
- Route user requests
- Generate AI responses
- Perform business logic

If health monitoring begins controlling application behavior, the architecture has been violated.

---

# System Position

```
User
    │
    ▼
api_gateway.py
    │
    ▼
request_router.py
    │
    ├───────────────► system_health_check.py
    │                      │
    │                      ▼
    │              Service Diagnostics
    │
    ▼
ai_orchestrator.py
```

The health monitor may be invoked:

- during application startup
- by administrative APIs
- by maintenance tools
- by scheduled monitoring
- by diagnostic interfaces

---

# Services Monitored

Examples of monitored components include:

- Ollama
- MariaDB
- ChromaDB
- n8n
- Aider
- External APIs
- AI model availability
- Database connectivity
- Memory subsystem
- Tool execution subsystem

As Aetheraeon grows, additional services can be monitored without changing higher architecture layers.

---

# Primary Functions

Current public functions include:

## Primary Functions

The current implementation exposes the following public functions:

| Function | Purpose |
|----------|---------|
| `startup_banner()` | Displays the Aetheraeon startup banner and initialization information. |
| `check_ollama()` | Verifies that the Ollama service is available and responding correctly. |
| `check_n8n()` | Checks the availability of the n8n automation service. |
| `check_aider()` | Verifies that the Aider service is installed and operational. |
| `print_status(active_session)` | Displays the current status of monitored system services. |
| `print_status_summary()` | Prints a summarized overview of overall system health. |
| `run_startup_checks()` | Executes all startup diagnostics and validates required services before system initialization. |
| `get_lan_ip()` | Retrieves the local network (LAN) IP address of the current machine. |
| `get_public_ip()` | Retrieves the public internet IP address used by the system. |

---

> **Future Evolution**
>
> As Aetheraeon continues to evolve, these service-specific functions may eventually be consolidated into a more modular diagnostics framework (for example, generic service health checks, dependency validation, and centralized health reporting). This document reflects the current implementation while allowing the architecture to evolve over time.

---

> This document describes architectural responsibilities rather than requiring exact function names. Function implementations may evolve while maintaining the same system role.

---

# Output Contract

The System Health Monitor returns structured diagnostic information rather than user-facing responses.

Typical output includes:

- Overall system status
- Individual service status
- Connectivity results
- Availability information
- Diagnostic messages
- Startup readiness
- Runtime health information

The output should always be deterministic and machine-readable.

---

# Future Expansion

This component is designed to support future capabilities such as:

- Automatic recovery
- Service restart recommendations
- Dependency validation
- Resource monitoring
- Performance metrics
- Health history
- Alert generation
- Predictive diagnostics

These capabilities should remain within the monitoring domain and should never introduce AI reasoning or execution logic.

---

# Design Philosophy

> **"Observe Everything. Change Nothing."**

The System Health Monitor provides visibility into the operational state of Aetheraeon without influencing system behavior.

Its purpose is to ensure that every layer of the architecture can determine whether the platform is healthy before attempting execution.

By separating diagnostics from execution, Aetheraeon remains modular, predictable, and easier to maintain as the platform continues to grow.
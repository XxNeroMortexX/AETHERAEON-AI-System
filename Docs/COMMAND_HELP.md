# Dynamic command help

The `help` command is generated from registered tool metadata. There is no separate active command list to maintain.

The flow is:

`TOOL_META` in each tool-owning module → `register_tool()` in `core/tool_registry.py` → `REGISTERED_TOOLS` → `build_help()` in `core/help_system.py` → formatted help output.

`build_help()` reads each registry entry's `meta` object and groups it by `category`. The displayed command name, description, usage, examples, options, and confirmation requirement all come directly from that metadata. Handlers are registered alongside metadata but are never executed by the help builder.

## Adding a command

1. Create the command handler in the module that owns the behavior.
2. Create its `TOOL_META` dictionary with at least `name`, `category`, `description`, and `usage`; add examples, options, and confirmation requirements when relevant.
3. Call `register_tool(TOOL_META, handler)`.
4. Connect the command to the existing routing and execution flow.
5. Run `help`. The new metadata is included automatically.

Do not add a second help list. Command-specific fallback help must also filter and format entries from the registry metadata.

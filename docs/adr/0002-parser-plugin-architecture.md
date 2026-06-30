# ADR-0002: Parser Plugin Architecture

## Status

Accepted

## Context

The Knowledge Engine must parse raw source code into Abstract Syntax Trees (ASTs) as part of Phase 2. Since AIEKP aims to support multiple programming languages (e.g., Python, TypeScript, Java, Flutter/Dart), coupling all language-specific parsers into a single package would result in a bloated, fragile dependency tree. Adding or updating a parser for a specific language shouldn't require testing and deploying the entire parsing engine.

## Decision Drivers

* **Extensibility**: It must be easy to add support for new programming languages.
* **Separation of Concerns**: The core engine should only know *how* to orchestrate parsing, not the specifics of any one language's AST logic.
* **Dependency Isolation**: `tree-sitter` provides individual grammar packages (e.g., `tree-sitter-python`). A TypeScript project doesn't need Python dependencies.

## Decision

We will use a **Plugin Architecture** coupled with the **Strategy Pattern**:

1. **`packages/parser-core`**: A standalone `uv` package containing the core parsing strategy interface (`BaseParser` or `LanguageParser`) and common AST node models. It knows nothing about specific languages.
2. **`plugins/<language>-parser`**: Each language parser will be an independent `uv` package (e.g., `plugins/python-parser`). These plugins will implement the strategy interface and depend *only* on `parser-core` and their specific `tree-sitter` grammar.
3. **Registry**: At runtime, available plugins will be discovered and registered with a central parser factory.

## Rationale

By making each language parser an independent `uv` package, we ensure true dependency isolation. A bug or dependency conflict in the `java-parser` will not break the `python-parser`. Furthermore, the community or users can seamlessly inject their own parsers by adhering to the core interface without modifying the main codebase.

## Consequences

### Positive
* Highly decoupled system.
* Easier to unit-test specific language parsers in isolation.
* Fast builds and smaller dependency trees per plugin.

### Negative
* Increased boilerplate: each new language requires setting up a new `uv` workspace package (`pyproject.toml`, tests, etc.).
* Version alignment: requires careful versioning to ensure all plugins are compatible with the current `parser-core` interface.

### Implementation Notes
* Define the Strategy interface in `parser-core`.
* Start with `plugins/python-parser` as the reference implementation.

# Phase 2: Parser Engine Specification

## 1. Goal
Implement the **Parser Engine** to transform raw source code into Abstract Syntax Trees (ASTs) using `tree-sitter`. The engine must utilize a Plugin Architecture to support multiple languages, ensuring clean dependency separation and easy extensibility.

## 2. Prerequisites
* Phase 1 Repository Scanner is completed and capable of identifying source files.
* Python version `^3.11` is configured via `uv`.

## 3. Technical Requirements

### 3.1 Architecture (ADR-0002)
*   **Strategy Pattern**: Define a common interface for all language parsers.
*   **Plugin Architecture**: Each language parser is an independent `uv` package in the `plugins/` directory.

### 3.2 Parser Core Package (`packages/parser-core`)
*   Initialize as a new `uv` library.
*   **AST Models**: Define normalized AST models (e.g., `AiekpAstNode`) that wrap `tree-sitter` nodes. This ensures that downstream consumers (Phase 3) don't need to depend on the raw `tree-sitter` package.
*   **Interface**: Define `LanguageParser` (ABC) with a method like `parse(file_content: str) -> AiekpAstNode`.
*   **Parser Factory**: Implement a registry/factory pattern to instantiate the correct parser based on file extensions.

### 3.3 Python Plugin (`plugins/python-parser`)
*   Initialize as a new `uv` library in the workspace.
*   Dependencies: `aiekp-parser-core`, `tree-sitter`, `tree-sitter-python`.
*   Implement `PythonParser` adhering to the `LanguageParser` interface.
*   Logic: Initialize the python `tree-sitter` language, parse the byte string, and map the root node to the common AST model.

### 3.4 Integration
*   Ensure that the `FileScanEvent` from Phase 1 can be passed to the Parser Factory to get the corresponding AST.

## 4. Definition of Done (DoD)
- [ ] `packages/parser-core` is created with a clean interface.
- [ ] `plugins/python-parser` is created and successfully parses a `.py` file into an AST.
- [ ] `ADR-0002` is documented and finalized.
- [ ] Appropriate unit tests are written for the parser core and the python plugin.
- [ ] `docs/conductor/roadmap.md` and `docs/conductor/tracks.md` reflect Phase 2 progress.

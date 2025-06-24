### **Research & Design: The DW4 Protocol**

**Objective:** To design a new, modern development workflow protocol, DW4, based on the lessons learned from the analysis and refactoring of DW3.

**1. Core Principles of DW4:**

The failures of DW3 were rooted in its conflicting, dual-language state machines. DW4 will be designed to avoid these pitfalls from the start.

*   **Single Source of Truth:** The entire workflow will be managed by a single, pure-Python application. There will be no wrapper scripts with conflicting logic.
*   **Clean Architecture:** The application will be modular, with separate components for state management, configuration, and user interaction. This makes it easy to maintain and extend.
*   **Configuration-Driven:** Core settings (like stage names and deliverable paths) will be stored in a dedicated configuration file, not hardcoded in the script.
*   **Atomic State Transitions:** If any step in a stage transition fails, the workflow will halt without being left in an inconsistent state.
*   **Extensibility:** The design will be inherently modular, making it simple to add new stages, checks, or actions in the future.
*   **Superior User Feedback:** The CLI will provide clear, color-coded, and context-aware feedback for every action, success, and failure.

**2. Proposed DW4 Architecture:**

The project will be restructured to be more Python-native.

*   **New Directory Structure:**
    ```
    /
    ├── .git/
    ├── dw4/                  # The workflow engine itself
    │   ├── __main__.py       # Allows running with 'python -m dw4'
    │   ├── cli.py            # Argparse command-line interface
    │   ├── state_manager.py  # The core state machine logic
    │   ├── config.py         # All configuration variables
    │   └── git_handler.py    # All Git-related functions
    ├── docs/                 # Unchanged: houses workflow state files
    │   ├── WORKFLOW_MASTER.md
    │   └── ...
    ├── deliverables/         # A unified directory for all stage outputs
    │   ├── plan/
    │   ├── research/
    │   └── ...
    └── tests/                # For testing the user's project
    ```

*   **Core Components:**
    *   `cli.py`: The user's entry point. It will use Python's `argparse` library to handle commands like `dw4 approve` and `dw4 status`. It will be responsible *only* for parsing user input and calling the state manager.
    *   `state_manager.py`: The heart of DW4. It will contain the `WorkflowManager` class, which will be the single, authoritative source of truth for all workflow logic, including checking deliverables, running tests, and advancing stages.
    *   `git_handler.py`: All Git operations will be isolated in this module. The state manager will call these functions when needed (e.g., `git_handler.commit_changes()`).

**3. Path Forward:**

This design provides a clear and robust foundation for building a professional-grade development workflow. It directly addresses the architectural flaws of DW3 and establishes a pattern for long-term stability and maintainability.

The next step in the **Coder** stage will be to build out this new architecture, starting with the `dw4` directory and its core Python modules.
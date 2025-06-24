### **Research: Root-Cause Analysis of DW3 State Failures**

**Objective:** To conduct a deep-dive code review of the `dw3` workflow scripts (`workflow.sh` and `advance_stage.py`) to identify the precise cause of the recurring state management bugs.

**1. Code Analysis:**

*   **`workflow.sh`:**
    *   This script acts as the primary user interface.
    *   It contains a large `case` statement within the `approve` command block that determines the `next_stage`.
    *   Crucially, it has started to accumulate its own state transition logic, such as deliverable checks (e.g., `if [ ! -f "PLAN.md" ]`) and Git operations.
    *   It delegates the final state change to `advance_stage.py`.

*   **`advance_stage.py`:**
    *   This Python script is intended to be the state management engine.
    *   The `WorkflowManager.advance()` method contains its own, separate logic for handling stage transitions.
    *   It has functions like `_handle_git_operations()` and `_complete_requirement_cycle()` that perform actions based on the stage transition (e.g., committing code when moving from `Validator` to `Deployer`).

**2. The Root Cause: Conflicting State Machines**

The fundamental bug is a violation of the **Single Responsibility Principle**. The project has two independent and conflicting state machines trying to manage the workflow simultaneously:

*   **State Machine 1 (in `workflow.sh`):** A bash-based system that checks some conditions and decides what the next stage should be.
*   **State Machine 2 (in `advance_stage.py`):** A more complex, Python-based system that *also* checks conditions and performs actions, including Git operations that the bash script is unaware of.

When the user runs `./scripts/workflow.sh approve`, the bash script performs its checks and then calls the Python script. The Python script then executes its own logic, which often conflicts with or duplicates the logic in the bash script. This leads to the unpredictable behavior we've observed, such as skipping stages, creating premature commits, and failing to enforce gate conditions.

**3. Hypothesis:**

The workflow is failing because there is no single source of truth for state transition logic. The `workflow.sh` script was likely intended to be a simple wrapper, but it has evolved to contain complex logic that conflicts with the more robust engine in `advance_stage.py`.

**4. Path Forward:**

To fix this, we must refactor the system to have a single, authoritative state machine.

*   **Proposed Solution:** All state transition logic (deliverable checks, Git operations, file modifications) must be consolidated into `advance_stage.py`. The `workflow.sh` script should be simplified to only handle user interaction and then call the Python script, trusting it to manage the state correctly.

This research provides a clear path forward for either creating a stable `dw3-v2` or designing a new, more reliable `dw4`.
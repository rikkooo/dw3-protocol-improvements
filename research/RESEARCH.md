### **Research for `PROTOCOL.md`**

**Objective:** To consolidate all observed behaviors and implicit rules of the `dw3` workflow into a structured document. This research will serve as the foundation for creating the official `PROTOCOL.md`.

**1. Workflow Stages & Progression:**
*   The workflow consists of five linear stages: `Engineer` -> `Researcher` -> `Coder` -> `Validator` -> `Deployer`.
*   Progression is managed by the `./scripts/workflow.sh` script.
*   Advancing stages requires creating a specific deliverable and then running `./scripts/workflow.sh approve`.

**2. Deliverables and Directory Structure:**
*   **Engineer:**
    *   **Deliverable:** `PLAN.md`
    *   **Path:** Project root (`/`)
*   **Researcher:**
    *   **Deliverable:** `RESEARCH.md`
    *   **Path:** `research/`
*   **Coder:**
    *   **Deliverable:** One or more Git commits.
    *   **Path:** N/A (Code should be placed in `src/` by convention, but the script only checks for new commits).
*   **Validator:**
    *   **Deliverable:** `VALIDATION.md`
    *   **Path:** `validation/`
    *   **Note:** The script also runs an automated test (`tests/test_example.sh`).
*   **Deployer:**
    *   **Deliverable:** `DEPLOYMENT.md`
    *   **Path:** `deployment/`
    *   **Note:** The script attempts a `git push` and requires an approval (`./scripts/workflow.sh approve`) to complete the cycle.

**3. Git Integration Details:**
*   A Git repository is automatically initialized when moving from Researcher to Coder.
*   An initial commit is created automatically at this point.
*   The Coder stage is gated by the creation of new commits.
*   The Validator stage automatically commits all changes (including the validation report) with a generic message (`feat(req-X): ...`) before moving to Deployer.
*   The Deployer stage fails if a remote is not configured, indicating that `git push` is the expected action.

**Conclusion:**
This research provides a clear, structured outline of the protocol's mechanics. The next step is to formalize this information into a user-friendly `PROTOCOL.md` document in the Coder stage.

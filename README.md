# WindSurf DW3 Workflow Template

## 1. Purpose

This directory contains the `dw3` workflow, an improved, standardized template for bootstrapping new development projects. It is designed to be used with the WindSurf AI assistant to create a consistent, transparent, and robust development process.

**IMPORTANT:** Do not work directly in this template directory. It is meant to be copied to a new project folder.

## 2. How to Start a New Project

To create a new project from this template, copy this directory to a new location.

## 3. The Workflow

The `dw3` workflow is managed by the `./scripts/workflow.sh` script. It guides the project through five distinct stages. To check the current stage and see available actions, run:

```bash
./scripts/workflow.sh
```

### Advancing Stages

To advance from one stage to the next, a single, unified command is used:

```bash
./scripts/workflow.sh approve
```

This command works for all stages, provided the stage's specific requirements have been met.

### Workflow Stages

1.  **Engineer:**
    *   **Goal:** Define the requirements and scope of a task.
    *   **Deliverable:** A `PLAN.md` file outlining the work to be done.

2.  **Researcher:**
    *   **Goal:** Plan the implementation, choose tools, and outline the solution.
    *   **Deliverable:** A `research/RESEARCH.md` file detailing the implementation strategy.

3.  **Coder:**
    *   **Goal:** Write the code to implement the plan.
    *   **Requirement:** At least one new `git commit` must be made. The workflow script automatically detects new commits.

4.  **Validator:**
    *   **Goal:** Automatically verify the new code.
    *   **Process:** The workflow automatically runs the test suite located in the `/tests` directory using the `scripts/run_tests.sh` script. All tests must pass to proceed.

5.  **Deployer:**
    *   **Goal:** Finalize the feature and prepare for the next cycle.
    *   **Process:** This stage marks the completion of the current requirement. Approving this stage will loop the workflow back to the **Engineer** stage for the next requirement in the project.

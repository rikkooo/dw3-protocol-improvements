# The DW3 Development Workflow Protocol

Welcome to the DW3 development workflow. This document outlines the structured, five-stage process for building and deploying software. Following this protocol ensures consistency, quality, and robust version control for every project.

## The Five Stages

The workflow is a linear progression through five distinct stages. You must complete the deliverable for each stage before moving to the next.

1.  **Engineer:** Plan the work.
2.  **Researcher:** Investigate the best approach.
3.  **Coder:** Write the code.
4.  **Validator:** Test and verify the code.
5.  **Deployer:** Deploy the final product.

## Advancing the Workflow

Progression is managed by a single script:

```bash
# Run from the project root
./scripts/workflow.sh
```

- To **check the current stage**, run the script with no arguments.
- To **advance to the next stage**, you must first create the required deliverable and then run `./scripts/workflow.sh approve`.

## Deliverables and Directory Structure

Each stage has a specific deliverable that must be placed in a designated directory.

| Stage      | Deliverable                                | Required Path        |
| :--------- | :----------------------------------------- | :------------------- |
| Engineer   | `PLAN.md`                                  | `/` (Project Root)   |
| Researcher | `RESEARCH.md`                              | `research/`          |
| Coder      | One or more Git commits                    | `src/` (by convention) |
| Validator  | `VALIDATION.md`                            | `validation/`        |
| Deployer   | `DEPLOYMENT.md` & a successful `git push`  | `deployment/`        |

## Key Automation and Rules

- **Git Initialization:** The workflow automatically initializes a Git repository when you advance from the Researcher to the Coder stage.
- **Commits are Mandatory:** You cannot complete the Coder stage without making at least one new Git commit.
- **Automated Commits:** The workflow automatically creates commits when you approve the plan and the validation report to save the project state.
- **Automated Testing:** The Validator stage includes a hook to run automated tests located in the `tests/` directory.

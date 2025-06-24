from pathlib import Path

# --- Core Paths ---
# Assumes the script is run from the project root.
ROOT_DIR = Path.cwd()
DOCS_DIR = ROOT_DIR / "docs"
DELIVERABLES_DIR = ROOT_DIR / "deliverables"
MASTER_FILE = DOCS_DIR / "WORKFLOW_MASTER.md"
REQUIREMENTS_FILE = DOCS_DIR / "PROJECT_REQUIREMENTS.md"
APPROVAL_FILE = DOCS_DIR / "PROJECT_APPROVAL.md"
LAST_COMMIT_FILE = ROOT_DIR / ".last_commit_sha"

# --- Workflow Stages ---
STAGES = ["Engineer", "Researcher", "Coder", "Validator", "Deployer"]

# --- Deliverable Paths ---
# Using a dictionary to map stages to their deliverable paths
DELIVERABLE_PATHS = {
    "Engineer": DELIVERABLES_DIR / "plan" / "PLAN.md",
    "Researcher": DELIVERABLES_DIR / "research" / "RESEARCH.md",
    "Validator": DELIVERABLES_DIR / "validation" / "VALIDATION.md",
    "Deployer": DELIVERABLES_DIR / "deployment" / "DEPLOYMENT.md",
    # Coder stage is checked via git commits, not a specific file
}

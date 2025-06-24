import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Assuming config.py exists and STAGES is defined there
# from config import STAGES 
# For standalone execution, define STAGES here:
STAGES = ["Engineer", "Researcher", "Coder", "Validator", "Deployer"]


# Define constants for filenames
PROJECT_REQUIREMENTS_FILENAME = "PROJECT_REQUIREMENTS.md"
PROJECT_APPROVAL_FILENAME = "PROJECT_APPROVAL.md"

class WorkflowState:
    """Manages reading and writing the state to the master workflow file."""

    def __init__(self, master_path):
        self.path = master_path
        if not self.path.exists():
            print(f"Error: Master workflow file not found at {self.path}", file=sys.stderr)
            sys.exit(1)
        self.lines = self.path.read_text().splitlines()
        self.data = {}
        self._parse()

    def _parse(self):
        """Parses key-value pairs from the file."""
        for line in self.lines:
            if ":" in line:
                key, value_part = line.split(":", 1)
                value = value_part.split("#", 1)[0].strip()
                self.data[key.strip()] = value

    def get(self, key, default=None):
        """Gets a value from the parsed state."""
        return self.data.get(key, default)

    def set(self, key, value):
        """Sets a value in the state. This updates the raw lines."""
        self.data[key] = str(value)
        for i, line in enumerate(self.lines):
            if line.strip().startswith(key + ":"):
                comment = "" 
                if "#" in line:
                    comment = " #" + line.split("#", 1)[1].strip()
                self.lines[i] = f"{key}: {value}{comment}"
                return
        # If key not found, add it
        self.lines.append(f"{key}: {value}")

    def update_checklist(self, next_stage):
        """Updates the StageStatus checklist based on the new stage."""
        in_checklist_section = False
        # Reset all to unchecked first
        for i, line in enumerate(self.lines):
            if line.strip().startswith("StageStatus (checklist):"):
                in_checklist_section = True
                continue
            if in_checklist_section and line.strip().startswith("- ["):
                 self.lines[i] = line.replace("x]", " ]")

        # Now, check all stages up to and including the current one
        in_checklist_section = False
        for i, line in enumerate(self.lines):
            if line.strip().startswith("StageStatus (checklist):"):
                in_checklist_section = True
                continue
            if in_checklist_section and line.strip().startswith("- ["):
                stage_in_line = line.split("]", 1)[1].strip()
                if stage_in_line in STAGES:
                    self.lines[i] = line.replace(" ]", "x]")
                    if stage_in_line == next_stage:
                        break

    def save(self):
        """Saves the updated lines back to the file."""
        self.path.write_text("\n".join(self.lines) + "\n")

class WorkflowManager:
    """The single source of truth for all workflow advancement logic."""

    def __init__(self, master_file, next_stage):
        self.state = WorkflowState(Path(master_file))
        self.existing_stage = self.state.get("CurrentStage")
        self.next_stage = next_stage

    def _check_deliverables(self):
        """Checks for required deliverables before advancing."""
        if self.existing_stage == "Engineer" and not Path("PLAN.md").exists():
            print("ERROR: Deliverable 'PLAN.md' not found in project root.", file=sys.stderr)
            sys.exit(1)
        if self.existing_stage == "Researcher" and not Path("research/RESEARCH.md").exists():
            print("ERROR: Deliverable 'RESEARCH.md' not found in 'research/'.", file=sys.stderr)
            sys.exit(1)
        if self.existing_stage == "Validator" and not Path("validation/VALIDATION.md").exists():
            print("ERROR: Deliverable 'VALIDATION.md' not found in 'validation/'.", file=sys.stderr)
            sys.exit(1)
        if self.existing_stage == "Deployer" and not Path("deployment/DEPLOYMENT.md").exists():
            print("ERROR: Deliverable 'DEPLOYMENT.md' not found in 'deployment/'.", file=sys.stderr)
            sys.exit(1)
        if self.existing_stage == "Coder":
            last_commit_file = Path(".last_commit_sha")
            if not last_commit_file.exists():
                print("ERROR: Git tracking file .last_commit_sha not found.", file=sys.stderr)
                sys.exit(1)
            last_commit_sha = last_commit_file.read_text().strip()
            current_commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            if last_commit_sha == current_commit_sha:
                print("ERROR: No new commits detected. Please make one or more commits to proceed.", file=sys.stderr)
                sys.exit(1)

    def _handle_git_operations(self):
        """Handles all git-related tasks for stage transitions."""
        if self.next_stage == "Coder":
            if not Path(".git").exists():
                 print("[GIT] This is not a Git repository. Initializing...")
                 subprocess.run(["git", "init"], check=True, capture_output=True)
                 subprocess.run(["git", "add", "."], check=True, capture_output=True)
                 subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit: Project setup"], check=True, capture_output=True)
                 print("[GIT] Repository initialized and initial commit created.")
            commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            Path(".last_commit_sha").write_text(commit_sha)
            print("[GIT] Saved current commit SHA. Proceeding to Coder stage.")

        if self.existing_stage == "Coder" and self.next_stage == "Validator":
            print("[GIT] Committing approved code...")
            req_id = self.state.get("RequirementPointer")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"feat(req-{req_id}): Coder stage submission for requirement {req_id}"], check=True)
            print("[GIT] Code committed.")

        if self.existing_stage == "Deployer" and self.next_stage == "Engineer":
             print("[GIT] Pushing changes to remote...")
             result = subprocess.run(["git", "push"], capture_output=True, text=True)
             if result.returncode != 0:
                 print("Error: Command 'git push' failed.", file=sys.stderr)
                 print(result.stderr, file=sys.stderr)
                 print("[GIT] Push failed. Please ensure your remote is configured correctly.", file=sys.stderr)

    def _complete_requirement_cycle(self):
        """Handles logic for completing a full A-Z cycle."""
        if self.existing_stage == "Deployer" and self.next_stage == "Engineer":
            req_id = int(self.state.get("RequirementPointer"))
            self._log_approval(req_id)
            self._update_requirements_checklist(str(req_id))
            self.state.set("RequirementPointer", req_id + 1)
            print(f"[INFO] Advanced to next requirement: {req_id + 1}.")

    def _log_approval(self, req_id):
        """Logs the completion of a requirement."""
        approval_path = Path(self.state.path.parent, PROJECT_APPROVAL_FILENAME)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        with approval_path.open("a") as f:
            f.write(f"Requirement {req_id} approved at {timestamp}\n")
        print(f"[INFO] Logged approval for Requirement ID {req_id}.")

    def _update_requirements_checklist(self, req_id):
        """Updates the checklist in the requirements file."""
        req_path = Path(self.state.path.parent, PROJECT_REQUIREMENTS_FILENAME)
        if not req_path.exists():
            return
        lines = req_path.read_text().splitlines()
        pattern = re.compile(r"^(\s*-\s*\[\s\]\s*(?:\*\*ID\s+|ID\s+))(" + re.escape(req_id) + r")((?:\s*\*\*|\s+).*)$")
        for i, line in enumerate(lines):
            match = pattern.match(line)
            if match:
                lines[i] = f"{match.group(1).replace('[ ]', '[x]')}{match.group(2)}{match.group(3)}"
                req_path.write_text("\n".join(lines) + "\n")
                print(f"Updated checkbox for Req ID {req_id} in {PROJECT_REQUIREMENTS_FILENAME}")
                break

    def advance(self):
        """Executes the full workflow advancement logic."""
        self._check_deliverables()
        self._handle_git_operations()
        self._complete_requirement_cycle()
        self.state.set("CurrentStage", self.next_stage)
        self.state.update_checklist(self.next_stage)
        self.state.save()
        print(f"Advanced workflow. Current stage is now: {self.next_stage}")

def main():
    """Main function to run the script from the command line."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <path_to_master_file> <next_stage>", file=sys.stderr)
        sys.exit(1)
    master_file = sys.argv[1]
    next_stage = sys.argv[2]
    if next_stage not in STAGES:
        print(f"Error: '{next_stage}' is not a valid stage. Must be one of {STAGES}", file=sys.stderr)
        sys.exit(1)
    manager = WorkflowManager(master_file, next_stage)
    manager.advance()

if __name__ == "__main__":
    main()

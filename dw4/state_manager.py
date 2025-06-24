import re
import sys
from datetime import datetime, timezone
from dw4.config import (
    MASTER_FILE, REQUIREMENTS_FILE, APPROVAL_FILE, STAGES, DELIVERABLE_PATHS
)
from dw4 import git_handler

class WorkflowState:
    def __init__(self):
        if not MASTER_FILE.exists():
            print(f"Error: Master workflow file not found at {MASTER_FILE}", file=sys.stderr)
            sys.exit(1)
        self.lines = MASTER_FILE.read_text().splitlines()
        self.data = {}
        self._parse()

    def _parse(self):
        for line in self.lines:
            if ":" in line:
                key, value_part = line.split(":", 1)
                value = value_part.split("#", 1)[0].strip()
                self.data[key.strip()] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = str(value)
        for i, line in enumerate(self.lines):
            if line.strip().startswith(key + ":"):
                comment = ""
                if "#" in line:
                    comment = " #" + line.split("#", 1)[1].strip()
                self.lines[i] = f"{key}: {value}{comment}"
                return
        self.lines.append(f"{key}: {value}")

    def save(self):
        MASTER_FILE.write_text("\n".join(self.lines) + "\n")

class WorkflowManager:
    def __init__(self):
        self.state = WorkflowState()
        self.current_stage = self.state.get("CurrentStage")

    def get_status(self):
        print(f"CRITICAL DIRECTIVE: CURRENT STAGE IS: {self.current_stage}")
        if self.current_stage == "Coder":
             if not git_handler.has_new_commits():
                 print("TASK: No new commits detected. Please commit your changes to proceed.")
             else:
                 print("--- New commits detected. Ready for approval. ---")
        elif self.current_stage == "Validator":
            print("--- Running automated validation... ---")
            try:
                subprocess.run([sys.executable, "tests/run_tests.py"], check=True)
                print("--- ✅ VALIDATION PASSED ---")
            except subprocess.CalledProcessError:
                print("--- ⛔️ VALIDATION FAILED ---", file=sys.stderr)
                sys.exit(1)
        elif self.current_stage in DELIVERABLE_PATHS:
            deliverable = DELIVERABLE_PATHS[self.current_stage]
            print(f"TASK: Ensure deliverable '{deliverable.name}' is complete in '{deliverable.parent}'.")
        
        print(f"\n--- To approve this stage and advance, run: python -m dw4 approve ---")

    def approve(self):
        self._check_deliverables()
        
        current_stage_index = STAGES.index(self.current_stage)
        next_stage_index = (current_stage_index + 1) % len(STAGES)
        next_stage = STAGES[next_stage_index]

        self._run_pre_transition_actions(next_stage)

        self.state.set("CurrentStage", next_stage)
        self.state.save()
        
        self._run_post_transition_actions()

        print(f"Advanced workflow. Current stage is now: {next_stage}")

    def _check_deliverables(self):
        if self.current_stage == "Coder":
            if not git_handler.has_new_commits():
                print("ERROR: No new commits detected. Please make one or more commits to proceed.", file=sys.stderr)
                sys.exit(1)
        elif self.current_stage in DELIVERABLE_PATHS:
            deliverable_path = DELIVERABLE_PATHS[self.current_stage]
            if not deliverable_path.exists():
                print(f"ERROR: Deliverable '{deliverable_path.name}' not found in '{deliverable_path.parent}'.", file=sys.stderr)
                sys.exit(1)

    def _run_pre_transition_actions(self, next_stage):
        if self.current_stage == "Coder" and next_stage == "Validator":
            req_id = self.state.get("RequirementPointer")
            git_handler.commit_changes(req_id)
        
        if self.current_stage == "Deployer" and next_stage == "Engineer":
            git_handler.push_changes()
            self._complete_requirement_cycle()

    def _run_post_transition_actions(self):
        if self.state.get("CurrentStage") == "Coder":
            git_handler.save_current_commit_sha()

    def _complete_requirement_cycle(self):
        req_id = int(self.state.get("RequirementPointer"))
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        with APPROVAL_FILE.open("a") as f:
            f.write(f"Requirement {req_id} approved at {timestamp}\n")
        print(f"[INFO] Logged approval for Requirement ID {req_id}.")
        
        if REQUIREMENTS_FILE.exists():
            lines = REQUIREMENTS_FILE.read_text().splitlines()
            pattern = re.compile(r"^(\\s*-\\s*\\[\\s\\]\\s*(?:\\*\\*ID\\s+|ID\\s+))(" + re.escape(str(req_id)) + r")((?:\\s*\\*\\*|\\s+).*)$")
            for i, line in enumerate(lines):
                match = pattern.match(line)
                if match:
                    lines[i] = f"{match.group(1).replace('[ ]', '[x]')}{match.group(2)}{match.group(3)}"
                    REQUIREMENTS_FILE.write_text("\n".join(lines) + "\n")
                    print(f"Updated checkbox for Req ID {req_id} in {REQUIREMENTS_FILE.name}")
                    break

        next_req_id = req_id + 1
        self.state.set("RequirementPointer", next_req_id)
        print(f"[INFO] Advanced to next requirement: {next_req_id}.")

#!/bin/bash

# DW3: A more robust, git-integrated, and automated workflow script.
set -euo pipefail

# --- Configuration ---
MASTER_FILE="docs/WORKFLOW_MASTER.md"
ADVANCE_SCRIPT_PATH="scripts/advance_stage.py"
TEST_RUNNER_SCRIPT="scripts/run_tests.sh"
LAST_COMMIT_FILE=".last_commit_sha"

# --- Helper Functions ---
get_current_stage() {
    grep "CurrentStage:" "$MASTER_FILE" | awk '{print $2}'
}

# --- Command Handling ---
if [ "$#" -gt 0 ]; then
    command="$1"
    current_stage=$(get_current_stage)
    next_stage=""

    # Universal 'approve' command for all stages
    if [ "$command" == "approve" ]; then
        case $current_stage in
            "Engineer")
                if [ ! -f "PLAN.md" ]; then
                    echo "ERROR: Deliverable 'PLAN.md' not found in project root. Please create it before approving."
                    exit 1
                fi
                next_stage="Researcher"
                ;;
            "Researcher")
                if [ ! -f "research/RESEARCH.md" ]; then
                    echo "ERROR: Deliverable 'RESEARCH.md' not found in 'research/'. Please create it before approving."
                    exit 1
                fi
                next_stage="Coder"
                ;;
            "Coder")
                LAST_COMMIT_SHA=$(cat "$LAST_COMMIT_FILE")
                CURRENT_COMMIT_SHA=$(git rev-parse HEAD)
                if [ "$LAST_COMMIT_SHA" == "$CURRENT_COMMIT_SHA" ]; then
                    echo "ERROR: No new commits detected. Please make one or more commits to proceed."
                    exit 1
                fi
                next_stage="Validator"
                ;;
            "Validator")
                if [ ! -f "validation/VALIDATION.md" ]; then
                    echo "ERROR: Deliverable 'VALIDATION.md' not found in 'validation/'. Please create it before approving."
                    exit 1
                fi
                next_stage="Deployer"
                ;;
            "Deployer")
                if [ ! -f "deployment/DEPLOYMENT.md" ]; then
                    echo "ERROR: Deliverable 'DEPLOYMENT.md' not found in 'deployment/'. Please create it before approving."
                    exit 1
                fi
                next_stage="Engineer" # Loop back for the next requirement
                # Increment requirement ID logic
                req_id=$(grep "RequirementPointer:" "$MASTER_FILE" | awk '{print $2}')
                req_id=$((req_id + 1))
                sed -i "s/RequirementPointer: .*/RequirementPointer: $req_id/" "$MASTER_FILE"
                prev_req_id=$((req_id - 1))
                sed -i "s/-\[ \].*Req ID: $prev_req_id/-\[x\].*Req ID: $prev_req_id/" "docs/PROJECT_REQUIREMENTS.md"
                echo "[INFO] Logged approval for Requirement ID $prev_req_id."
                echo "[INFO] Advanced to next requirement: $req_id."
                ;;
        esac
    fi

    if [ -n "$next_stage" ]; then
        echo "--- Advancing Stage ---"
        
        # --- GIT INTEGRATION: Store commit SHA before entering Coder stage ---
        if [ "$next_stage" == "Coder" ]; then
            if [ ! -d ".git" ]; then
                echo "[GIT] This is not a Git repository. Initializing..."
                git init > /dev/null
                git add . > /dev/null
                git commit -m "Initial commit: Project setup" > /dev/null
                echo "[GIT] Repository initialized and initial commit created."
            fi
            git rev-parse HEAD > "$LAST_COMMIT_FILE"
            echo "[GIT] Saved current commit SHA. Proceeding to Coder stage."
        fi
        
        # --- GIT INTEGRATION: Commit code when leaving Coder stage ---
        if [ "$next_stage" == "Validator" ]; then
            echo "[GIT] Committing approved code..."
            req_id=$(grep "RequirementPointer:" "$MASTER_FILE" | awk '{print $2}')
            git add .
            git commit -m "feat(req-$req_id): Coder stage submission for requirement $req_id"
            echo "[GIT] Code committed."
        fi

        # --- GIT INTEGRATION: Push changes when leaving Deployer stage ---
        if [ "$current_stage" == "Deployer" ]; then
            echo "[GIT] Pushing changes to remote..."
            if ! git push; then
                echo "Error: Command 'git push' failed with exit code $?."
                echo "[GIT] Push failed. Please ensure your remote is configured correctly."
            fi
        fi

        python3 "$ADVANCE_SCRIPT_PATH" "$MASTER_FILE" "$next_stage"
        exit 0
    fi
fi

# --- Stage-specific Logic ---
current_stage=$(get_current_stage)
case $current_stage in
    "Engineer")
        echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
        echo "TASK: Review and update the project plan in 'PLAN.md'."
        if [ -f "PLAN.md" ]; then
            echo "--- Current Plan: ---"
            cat PLAN.md
        else
            echo "WARNING: 'PLAN.md' not found. Please create it."
        fi
        echo -e "\n--- To approve this plan, run: ./scripts/workflow.sh approve ---"
        ;;

    "Researcher")
        echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
        echo "TASK: Document your research in 'research/RESEARCH.md'."
        if [ -f "research/RESEARCH.md" ]; then
            echo "--- Current Research: ---"
            cat research/RESEARCH.md
        else
            echo "WARNING: 'research/RESEARCH.md' not found. Please create it."
        fi
        echo -e "\n--- To approve this research, run: ./scripts/workflow.sh approve ---"
        ;;

    "Coder")
        echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
        if [ ! -f "$LAST_COMMIT_FILE" ]; then
            echo "[GIT] Initializing git tracking..."
            if [ ! -d ".git" ]; then
                git init > /dev/null
                git add . > /dev/null
                git commit -m "Initial commit: Project setup" > /dev/null
            fi
            git rev-parse HEAD > "$LAST_COMMIT_FILE"
        fi
        LAST_COMMIT_SHA=$(cat "$LAST_COMMIT_FILE")
        CURRENT_COMMIT_SHA=$(git rev-parse HEAD)

        if [ "$LAST_COMMIT_SHA" == "$CURRENT_COMMIT_SHA" ]; then
            echo -e "TASK: No new commits detected. Please commit your changes to proceed.\nExample: git add . && git commit -m \"Your message\""
        else
            echo "--- New commits detected since last stage: ---"
            git --no-pager log "$LAST_COMMIT_SHA..$CURRENT_COMMIT_SHA" --oneline
            echo -e "\n--- To approve this code and move to validation, run: ./scripts/workflow.sh approve ---"
        fi
        ;;

    "Validator")
        echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
        echo "--- Running automated validation... ---"
        if output=$(bash "$TEST_RUNNER_SCRIPT" 2>&1); then
            echo "--- ✅ VALIDATION PASSED ---"
            echo -e "\n--- To approve this validation and move to deployment, run: ./scripts/workflow.sh approve ---"
        else
            echo "--- ⛔️ VALIDATION FAILED ---"
            echo "Error details:"
            echo "$output"
            exit 1
        fi
        ;;

    "Deployer")
        echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
        echo "TASK: The project is ready for deployment."
        echo -e "\n--- To mark deployment as successful and start the next requirement, run: ./scripts/workflow.sh approve ---"
        ;;

    *)
        echo "WARNING: Logic for stage '$current_stage' is not defined."
        ;;
esac
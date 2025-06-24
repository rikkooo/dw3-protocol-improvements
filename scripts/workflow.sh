#!/bin/bash

# DW3: A more robust, git-integrated, and automated workflow script.

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
            "Engineer")   next_stage="Researcher" ;;
            "Researcher") next_stage="Coder" ;;
            "Coder")      next_stage="Validator" ;;
            "Validator")  next_stage="Deployer" ;;
            "Deployer")
                next_stage="Engineer" # Loop back for the next requirement
                # Increment requirement ID logic
                req_id=$(grep "RequirementPointer:" "$MASTER_FILE" | awk '{print $2}')
                req_id=$((req_id + 1))
                sed -i "s/RequirementPointer: .*/RequirementPointer: $req_id/" "$MASTER_FILE"
                prev_req_id=$((req_id - 1))
                sed -i "s/-\\[ \\].*Req ID: $prev_req_id/-\\[x\\].*Req ID: $prev_req_id/" "docs/PROJECT_REQUIREMENTS.md"
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
                echo "[GIT] Initialized repository and created initial commit."
            fi
            git rev-parse HEAD > "$LAST_COMMIT_FILE"
            echo "[GIT] Saved current commit SHA. Proceeding to Coder stage."
        fi

        python3 "$ADVANCE_SCRIPT_PATH" "$MASTER_FILE" "$next_stage"
        exit 0
    else
        echo "--- ⛔️ ERROR ---"
        echo "Invalid command '$command' for the current stage '$current_stage'."
        echo "Please run './scripts/workflow.sh' without arguments to see the correct options."
        exit 1
    fi
fi

# --- Main Logic: Display status and instructions based on the current stage ---
current_stage=$(get_current_stage)
echo "INFO: Workflow state is managed in '$MASTER_FILE'"
echo "--------------------------------------------------"

case $current_stage in
    "Engineer")
        if [ ! -f "PLAN.md" ]; then
            echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
            echo "Deliverable 'PLAN.md' not found. Please complete the Engineer's task."
        else
            echo "--- The Engineer has produced the following plan: ---"
            cat PLAN.md
            echo "\n--- To approve this plan, run: ./scripts/workflow.sh approve ---"
        fi
        ;;

    "Researcher")
        if [ ! -f "research/RESEARCH.md" ]; then
            echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
            echo "Deliverable 'research/RESEARCH.md' not found. Please complete the Researcher's task."
        else
            echo "--- The Researcher has gathered the following information: ---"
            cat research/RESEARCH.md
            echo "\n--- To approve this research, run: ./scripts/workflow.sh approve ---"
        fi
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
            echo "TASK: No new commits detected. Please make one or more commits to proceed."
        else
            echo "--- New commits detected since last stage: ---"
            git --no-pager log "$LAST_COMMIT_SHA..$CURRENT_COMMIT_SHA" --oneline
            echo "\n--- To approve this code and move to validation, run: ./scripts/workflow.sh approve ---"
        fi
        ;;

    "Validator")
        echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
        echo "--- Running automated validation... ---"
        if bash "$TEST_RUNNER_SCRIPT"; then
            echo "--- ✅ VALIDATION PASSED ---"
            echo "\n--- To approve this validation and move to deployment, run: ./scripts/workflow.sh approve ---"
        else
            echo "--- ⛔️ VALIDATION FAILED ---"
            echo "Please fix the tests and run './scripts/workflow.sh' again."
            exit 1
        fi
        ;;

    "Deployer")
        echo "CRITICAL DIRECTIVE: CURRENT STAGE IS: $current_stage"
        echo "TASK: The project is ready for deployment."
        echo "\n--- To mark deployment as successful and start the next requirement, run: ./scripts/workflow.sh approve ---"
        ;;

    *)
        echo "WARNING: Logic for stage '$current_stage' is not defined."
        ;;
esac

#!/bin/bash

# Check if a project name was passed as an argument
if [ -n "$1" ]; then
    project_name="$1"
else
    # If not, prompt for the new project name
    echo "Enter the name for your new project (e.g., my-new-app):"
    read project_name
fi

# Validate input
if [ -z "$project_name" ]; then
    echo "Project name cannot be empty. Exiting."
    exit 1
fi

# --- Corrected Directory Logic ---
# Get the absolute path of the directory where this script is running (e.g., /home/ubuntu/devs/dw2)
source_dir=$(cd "$(dirname "$0")" && pwd)
# Get the parent directory (e.g., /home/ubuntu/devs)
parent_dir=$(dirname "$source_dir")
# Define the destination for the new project in the parent directory
dest_dir="$parent_dir/$project_name"

# Check for existing directory
if [ -d "$dest_dir" ]; then
    echo "Error: Directory '$dest_dir' already exists. Exiting."
    exit 1
fi

# Create and copy
echo "Creating project '$project_name' in '$parent_dir'..."
mkdir -p "$dest_dir"
cp -r "$source_dir/docs" "$dest_dir/"
cp -r "$source_dir/scripts" "$dest_dir/"
cp -r "$source_dir/research" "$dest_dir/"
cp -r "$source_dir/status" "$dest_dir/"
cp "$source_dir/README.md" "$dest_dir/"

# Create a failure counter file
echo "0" > "$dest_dir/.failure_count"

# Replace placeholder in the new project's master file
master_file="$dest_dir/docs/WORKFLOW_MASTER.md"
sed -i "s/# <PROJECT_NAME_PLACEHOLDER> – Workflow Master/# $project_name – Workflow Master/g" "$master_file"
# Reset the RequirementPointer to 1 for the new project
sed -i "s/RequirementPointer: .*/RequirementPointer: 1 #Current active requirement ID (integer). This points to the Nth requirement in PROJECT_REQUIREMENTS.md or a specific req-ID./g" "$master_file"

# Make scripts executable in the new project
chmod +x "$dest_dir/scripts/workflow.sh"

echo "--------------------------------------------------"
echo "Project '$project_name' created successfully in '$dest_dir'."
echo ""
echo "Next Steps:"
echo "To manage the workflow, cd into the new project directory:"
echo "cd $dest_dir"
echo ""
echo "Then, to see the current status and your next task, run:"
echo "cd $dest_dir && ./scripts/workflow.sh"
echo ""
echo "You will be prompted to approve deliverables at each stage by running commands like './scripts/workflow.sh approve'."
echo "--------------------------------------------------"

#!/bin/bash

# Simple test runner script
# It executes all .sh files in the ../tests/ directory

TEST_DIR="$(dirname "$0")/../tests"

for test_file in "$TEST_DIR"/*.sh; do
    if [ -f "$test_file" ] && [ -x "$test_file" ]; then
        echo "--- Executing $test_file ---"
        if ! "$test_file"; then
            echo "--- Test Failed: $test_file ---"
            exit 1
        fi
        echo "--- Test Passed: $test_file ---"
    elif [ ! -x "$test_file" ]; then
        echo "--- WARNING: $test_file is not executable. Making it executable... ---"
        chmod +x "$test_file"
        echo "--- Re-executing $test_file ---"
        if ! "$test_file"; then
            echo "--- Test Failed: $test_file ---"
            exit 1
        fi
        echo "--- Test Passed: $test_file ---"
    fi
done

echo "
All tests completed successfully."
exit 0

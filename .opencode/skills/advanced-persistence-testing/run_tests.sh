#!/bin/bash
# Script to run all persistence tests

echo "Starting persistence tests..."

echo "Running persistence manager tests..."
python tests/integration/test_persistence.py
persistence_manager_result=$?

echo "Running database persistence tests..."
python tests/integration/test_database_persistence.py
database_result=$?

echo "\nTest Results:"
echo "Persistence Manager: $(if [ $persistence_manager_result -eq 0 ]; then echo \"PASSED\"; else echo \"FAILED\"; fi)"
echo "Database Persistence: $(if [ $database_result -eq 0 ]; then echo \"PASSED\"; else echo \"FAILED\"; fi)"

total_result=$((persistence_manager_result + database_result))

if [ $total_result -eq 0 ]; then
    echo "\nAll tests PASSED"
    exit 0
else
    echo "\nSome tests FAILED"
    exit 1
fi

###############################################################################
# Bash script file to create and populate test database for unit tests.
# And for running all unit tests. It is recommended to use this script for
# testing.
###############################################################################
#!/bin/bash

# File and folder names
DB_FOLDER="database/"
DB_SCHEMA_FILE_NAME="tellus_schema_dump.sql"
DB_DATA_FILE_NAME="tellus_data_dump.sql"
DB_TEST_FILE_NAME="test_tellus.db"
TEST_FOLDER="tests/"
declare -a test_files=("tests_database_api_bookings" "tests_database_api_users")

function create_test_db {
    ## Check database folder exists
    if [ ! -d "$DB_FOLDER" ]; then
        echo "$DB_FOLDER does not exist. Please control your setup."
        exit 0
    fi

    ## Check database schema dump exists
    if [ ! -f "$DB_FOLDER$DB_SCHEMA_FILE_NAME" ]; then
        echo "$DB_SCHEMA_FILE_NAME does not exist. Please control your setup."
        exit 0
    fi

    ## Check database data dump exists
    if [ ! -f "$DB_FOLDER$DB_DATA_FILE_NAME" ]; then
        echo "$DB_DATA_FILE_NAME does not exist. Please control your setup."
        exit 0
    fi

    ## Remove old test database
    if [ -f "$DB_FOLDER$DB_TEST_FILE_NAME" ]; then
        echo "Removing old test database."
        echo ".........................."
        rm $DB_FOLDER$DB_TEST_FILE_NAME
        echo "Old test database is removed."
        echo ".........................."
    fi

    ## Create and populate new test database
    echo "Tables are creating."
    echo ".........................."
    cat $DB_FOLDER$DB_SCHEMA_FILE_NAME | sqlite3 $DB_FOLDER$DB_TEST_FILE_NAME

    echo "Database is populating."
    echo ".........................."
    cat $DB_FOLDER$DB_DATA_FILE_NAME | sqlite3 $DB_FOLDER$DB_TEST_FILE_NAME
}

# Run tests
for i in "${test_files[@]}"
do
    # First create test db
    create_test_db
    if [ ! -f "$TEST_FOLDER$i" ]; then
        echo "Test file $i is running."
        echo ".........................."
        python -m $TEST_FOLDER$i
    fi

    ## Remove old test database
    if [ -f "$DB_FOLDER$DB_TEST_FILE_NAME" ]; then
        echo "Removing old test database."
        echo ".........................."
        rm $DB_FOLDER$DB_TEST_FILE_NAME
        echo "Old test database is removed."
        echo ".........................."
    fi
done

echo "Everything is done."
echo "Bye"
exit 0

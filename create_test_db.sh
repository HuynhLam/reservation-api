###############################################################################
# Bash script file to create and populate test database for unit tests.
# It must be run before every test to make sure that test database is correctly
# created under right directory.
###############################################################################
#!/bin/bash

# File and folder names
DB_FOLDER="database/"
DB_SCHEMA_FILE_NAME="tellus_schema_dump.sql"
DB_DATA_FILE_NAME="tellus_data_dump.sql"
DB_TEST_FILE_NAME="test_tellus.db"

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
    rm $DB_FOLDER$DB_TEST_FILE_NAME
    echo "Old test database is removed."
fi

## Create and populate new test database
echo "Tables are creating."
cat $DB_FOLDER$DB_SCHEMA_FILE_NAME | sqlite3 $DB_FOLDER$DB_TEST_FILE_NAME

echo "Database is populating."
cat $DB_FOLDER$DB_DATA_FILE_NAME | sqlite3 $DB_FOLDER$DB_TEST_FILE_NAME

echo "Everything is done."
echo "Bye"
exit 0

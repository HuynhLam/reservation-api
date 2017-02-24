###############################################################################
# Bash script file to create and populate database.
# It is recommended to run this script for creating db.
# WARNING: It removes old db files, so, be careful if you have changes and
# want to keep them. Please, create a copy of your changes to keep them safe.
###############################################################################
#!/bin/bash

# File and folder names
DB_FOLDER="database/"
DB_SCHEMA_FILE_NAME="tellus_schema_dump.sql"
DB_DATA_FILE_NAME="tellus_data_dump.sql"
DB_FILE_NAME="tellus.db"

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

## Remove old database
if [ -f "$DB_FOLDER$DB_FILE_NAME" ]; then
    echo "Removing old database."
    rm $DB_FOLDER$DB_FILE_NAME
    echo "Old database is removed."
    echo ".........................."
fi

## Create and populate new database
echo "Tables are creating."
echo ".........................."
cat $DB_FOLDER$DB_SCHEMA_FILE_NAME | sqlite3 $DB_FOLDER$DB_FILE_NAME

echo "Database is populating."
echo ".........................."
cat $DB_FOLDER$DB_DATA_FILE_NAME | sqlite3 $DB_FOLDER$DB_FILE_NAME

echo "Database is created."
echo "Bye"
exit 0

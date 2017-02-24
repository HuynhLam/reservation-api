###############################################################################
# Bash script file to make sure that everything is well structured.
# It is recommended to run this script, after installation.
###############################################################################
#!/bin/bash

# Folder names
DB_FOLDER="database/"
API_FOLDER="reservation/"
TEST_FOLDER="tests/"

# File names
declare -a db_files=("tellus_schema_dump.sql" "tellus_data_dump.sql")
declare -a api_files=("database.py" "resources.py")
declare -a test_files=("tests_database_api_bookings.py" "tests_database_api_users.py")

# Messages to inform user
ERR="ERROR: API cannot work properly without this file."
WARN="Warning: API can still work without this file, however it is recommended to install it."

## Check database folder exists
echo "Checking $DB_FOLDER"
if [ ! -d "$DB_FOLDER" ]; then
    echo "$DB_FOLDER does not exist. Please control your setup."
    echo $ERR
    exit 0
fi
echo "$DB_FOLDER is in right place."

echo "Checking $API_FOLDER"
## Check api folder exists
if [ ! -d "$API_FOLDER" ]; then
    echo "$API_FOLDER does not exist. Please control your setup."
    echo $ERR
    exit 0
fi
echo "$API_FOLDER is in right place."

echo "Checking $TEST_FOLDER"
## Check tests folder exists
if [ ! -d "$TEST_FOLDER" ]; then
    echo "$TEST_FOLDER does not exist. Please control your setup."
    echo $WARN
    exit 0
fi
echo "$TEST_FOLDER is in right place."

## Check database files.
for i in "${db_files[@]}"
do
    echo "Checking $i"
    if [ ! -f "$DB_FOLDER$i" ]; then
        echo "$i does not exist. Please control your setup."
        echo $ERR
        exit 0
    fi
    echo "$i is in right place."
done

## Check api files.
for i in "${api_files[@]}"
do
    echo "Checking $i"
    if [ ! -f "$API_FOLDER$i" ]; then
        echo "$i does not exist. Please control your setup."
        echo $ERR
        exit 0
    fi
    echo "$i is in right place."
done

## Check database files.
for i in "${test_files[@]}"
do
    echo "Checking $i"
    if [ ! -f "$TEST_FOLDER$i" ]; then
        echo "$i does not exist."
        echo $WARN
        exit 0
    fi
    echo "$i is in right place."
done

echo "It seems that everything is OK."
echo "Enjoy with it, bye."
exit 0

###############################################################################
# Bash script file to make sure that everything is well structured.
# It is recommended to run this script, after installation.
###############################################################################
#!/bin/bash

# Folder names
EXAMPLE_CLIENT_FOLDER="example_client/"
STATIC_FOLDER="${EXAMPLE_CLIENT_FOLDER}static/"
CSS_FOLDER="${STATIC_FOLDER}css/"
JS_FOLDER="${STATIC_FOLDER}js/"

# File names
declare -a client_files=("client.py")
declare -a html_files=("index.html")
declare -a css_files=("ui.css")
declare -a js_files=("example_client.js" "jquery-3.2.1.min.js")
MIDDLEWARE="run_with_client.py"

# Messages to inform user
ERR="ERROR: Client cannot work properly without this file."
WARN="Warning: Client can still work without this file, however it is recommended to install it."

## Check client folder exists
echo "Checking $EXAMPLE_CLIENT_FOLDER"
if [ ! -d "$EXAMPLE_CLIENT_FOLDER" ]; then
    echo "$EXAMPLE_CLIENT_FOLDER does not exist. Please control your setup."
    echo $ERR
    exit 0
fi
echo "$EXAMPLE_CLIENT_FOLDER is in right place."
echo ".........................."

echo "Checking $STATIC_FOLDER"
## Check static folder exists
if [ ! -d "$STATIC_FOLDER" ]; then
    echo "$STATIC_FOLDER does not exist. Please control your setup."
    echo $ERR
    exit 0
fi
echo "$STATIC_FOLDER is in right place."
echo ".........................."

echo "Checking $CSS_FOLDER"
## Check css folder folder exists
if [ ! -d "$CSS_FOLDER" ]; then
    echo "$CSS_FOLDER does not exist. Please control your setup."
    echo $ERR
    exit 0
fi
echo "$CSS_FOLDER is in right place."
echo ".........................."

## Check client files.
for i in "${client_files[@]}"
do
    echo "Checking $i"
    if [ ! -f "$EXAMPLE_CLIENT_FOLDER$i" ]; then
        echo "$i does not exist. Please control your setup."
        echo $ERR
        exit 0
    fi
    echo "$i is in right place."
    echo ".........................."
done

## Check html files files.
for i in "${html_files[@]}"
do
    echo "Checking $i"
    if [ ! -f "$STATIC_FOLDER$i" ]; then
        echo "$i does not exist. Please control your setup."
        echo $ERR
        exit 0
    fi
    echo "$i is in right place."
    echo ".........................."
done

## Check css files files.
for i in "${css_files[@]}"
do
    echo "Checking $i"
    if [ ! -f "$CSS_FOLDER$i" ]; then
        echo "$i does not exist."
        echo $ERR
        exit 0
    fi
    echo "$i is in right place."
    echo ".........................."
done

## Check js files files.
for i in "${js_files[@]}"
do
    echo "Checking $i"
    if [ ! -f "$JS_FOLDER$i" ]; then
        echo "$i does not exist."
        echo $ERR
        exit 0
    fi
    echo "$i is in right place."
    echo ".........................."
done

echo "Checking $MIDDLEWARE"
## Check middleware file exists
if [ ! -f "$MIDDLEWARE" ]; then
    echo "$MIDDLEWARE does not exist. Please control your setup."
    echo $ERR
    exit 0
fi
echo "$MIDDLEWARE is in right place."
echo ".........................."

echo "It seems that everything is OK."
echo "Enjoy with it, bye."
exit 0

#!/bin/sh

DC_DIRECTORY=$HOME/GITLEAKS
PROJECT_URL=$1
PROJECT_NAME=$2
SO_USER_ID=$3
SO_TEST_ID=$4
USE_CURL=$5
DATA_DIRECTORY="$DC_DIRECTORY/data"
CACHE_DIRECTORY="$DC_DIRECTORY/data/cache"
URL=""

if [ -z "$1" ]; then
    echo "PROJECT_URL (1) argument is required."
    exit 22
fi

if [ -z "$2" ]; then
    echo "PROJECT_NAME (2) argument is required."
    exit 22
fi

if [ -z "$3" ]; then
    echo "SO_USER_ID (3) argument is required."
    exit 22
fi

if [ -z "$4" ]; then
    echo "SO_TEST_ID (4) argument is required."
    exit 22
fi

if [ -z "$5" ] || [ "$5" != "true" ]; then
    USE_CURL="false" 
fi

if [ ! -d "$DATA_DIRECTORY" ]; then
    echo "Initially creating persistent directory: $DATA_DIRECTORY"
    mkdir -p "$DATA_DIRECTORY"
fi
if [ ! -d "$CACHE_DIRECTORY" ]; then
    echo "Initially creating persistent directory: $CACHE_DIRECTORY"
    mkdir -p "$CACHE_DIRECTORY"
fi

# PLATFORM REPOSITORY
URL="$PROJECT_URL"

if [ -d "${PWD}/reports/gitleaks/$SO_USER_ID" ]; then
    echo "Reports folder already exists."
else
    echo "Reports folder doesn't exist. Creating..."
    sudo mkdir -p "${PWD}"/reports/gitleaks/$SO_USER_ID
fi

# Naming folder by repo name
folder=$PROJECT_NAME

if [ -d "${PWD}/reports/gitleaks/$SO_USER_ID/$folder" ]; then
    echo 'Folder already exists, deleting...'
    sudo rm -r "${PWD}"/reports/gitleaks/$SO_USER_ID/$folder
fi 

cd "${PWD}"/reports/gitleaks/$SO_USER_ID
# Use clone or curl
if [ "$5" = "true" ]; then
    curl --request GET --header "Accept: application/zip" --output "./$folder.zip" "$URL" && unzip -o ./$folder.zip -d ./$folder
else
    git clone "$URL"
fi


if [ ! -d "${PWD}/$folder" ]; then
    echo "Repo wasn't cloned properly. Exiting."
    exit 2
fi 
cd ./"$folder"

DC_PROJECT="$folder"

cd ..
sudo gitleaks detect -s $DC_PROJECT -v -r ./report-gitleaks-$SO_TEST_ID.json


# remove repo
echo "Removing $folder"
if [ "$5" = "true" ]; then
    sudo rm ./"$folder".zip
fi
sudo rm -r ./"$folder"
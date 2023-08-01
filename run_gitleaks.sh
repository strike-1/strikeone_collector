#!/bin/sh

DC_DIRECTORY=$HOME/GITLEAKS
PROJECT_URL=$1
PROJECT_NAME=$2
PROJECT_BRANCH=$3
SO_USER_ID=$4
SO_TEST_ID=$5
USE_CURL=$6
DATA_DIRECTORY="$DC_DIRECTORY/data"
CACHE_DIRECTORY="$DC_DIRECTORY/data/cache"
URL=""

if [ -z "$1" ]; then
    echo "[GITLEAKS] PROJECT_URL (1) argument is required."
    exit 22
fi

if [ -z "$2" ]; then
    echo "[GITLEAKS] PROJECT_NAME (2) argument is required."
    exit 22
fi

if [ -z "$3" ]; then
    echo "[GITLEAKS] PROJECT_BRANCH (3) argument is required."
    exit 22
fi

if [ -z "$4" ]; then
    echo "[GITLEAKS] SO_USER_ID (4) argument is required."
    exit 22
fi

if [ -z "$5" ]; then
    echo "[GITLEAKS] SO_TEST_ID (5) argument is required."
    exit 22
fi

if [ -z "$6" ] || [ "$6" != "true" ]; then
    USE_CURL="false" 
fi

if [ ! -d "$DATA_DIRECTORY" ]; then
    echo "[GITLEAKS] Creating persistent directory: $DATA_DIRECTORY"
    mkdir -p "$DATA_DIRECTORY"
fi
if [ ! -d "$CACHE_DIRECTORY" ]; then
    echo "[GITLEAKS] Creating persistent directory: $CACHE_DIRECTORY"
    mkdir -p "$CACHE_DIRECTORY"
fi

# PLATFORM REPOSITORY
URL="$PROJECT_URL"

if [ -d "${PWD}/reports/gitleaks/$SO_USER_ID" ]; then
    echo "[GITLEAKS] Reports folder already exists."
else
    echo "[GITLEAKS] Reports folder doesn't exist. Creating..."
    sudo mkdir -p "${PWD}"/reports/gitleaks/$SO_USER_ID
fi

# Naming folder by repo name
folder=$PROJECT_NAME

if [ -d "${PWD}/reports/gitleaks/$SO_USER_ID/$folder" ]; then
    echo '[GITLEAKS] Folder already exists, deleting...'
    sudo rm -r "${PWD}"/reports/gitleaks/$SO_USER_ID/$folder
fi 

cd "${PWD}"/reports/gitleaks/$SO_USER_ID
# Use clone or curl
if [ "$6" = "true" ]; then
    echo "[GITLEAKS] Running curl..."
    curl --request GET --header "Accept: application/zip" --output "./$folder.zip" "$URL" && unzip -o ./$folder.zip -d ./$folder
else
    echo "[GITLEAKS] Cloning repo using "$PROJECT_BRANCH" branch..."
    git clone --branch "$PROJECT_BRANCH" "$URL"
fi


if [ ! -d "${PWD}/$folder" ]; then
    echo "[GITLEAKS] Repo wasn't cloned properly. Exiting."
    exit 2
fi 
cd ./"$folder"

DC_PROJECT="$folder"

cd ..
echo "[GITLEAKS] Running Gitleaks..."
sudo gitleaks detect -s $DC_PROJECT -v -r ./report-gitleaks-$SO_TEST_ID.json


# remove repo
if [ "$6" = "true" ]; then
    echo "[GITLEAKS] Removing repo zip file..."
    sudo rm ./"$folder".zip
fi
echo "[GITLEAKS] Removing repo folder..."
sudo rm -r ./"$folder"

echo "[GITLEAKS] Gitleaks scan completed."
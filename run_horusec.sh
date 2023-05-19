#!/bin/sh

DC_DIRECTORY=$HOME/HORUSEC
PROJECT_URL=$1
PROJECT_NAME=$2
SO_USER_ID=$3
SO_TEST_ID=$4
USE_CURL=$5
URL=""

if [ -z "$1" ]; then
    echo "[HORUSEC] PROJECT_URL (1) argument is required."
    exit 22
fi

if [ -z "$2" ]; then
    echo "[HORUSEC] PROJECT_NAME (2) argument is required."
    exit 22
fi

if [ -z "$3" ]; then
    echo "[HORUSEC] SO_USER_ID (3) argument is required."
    exit 22
fi

if [ -z "$4" ]; then
    echo "[HORUSEC] SO_TEST_ID (4) argument is required."
    exit 22
fi

if [ -z "$5" ] || [ "$5" != "true" ]; then
    USE_CURL="false" 
fi

# PLATFORM REPOSITORY
URL="$PROJECT_URL"

if [ -d "${PWD}/reports/horusec/$SO_USER_ID" ]; then
    echo "[HORUSEC] Reports folder already exists."
else
    echo "[HORUSEC] Reports folder doesn't exist. Creating..."
    sudo mkdir -p "${PWD}"/reports/horusec/$SO_USER_ID
fi

# Naming folder by repo name
folder=$PROJECT_NAME

if [ -d "${PWD}/reports/horusec/$SO_USER_ID/$folder" ]; then
    echo '[HORUSEC] Folder already exists, deleting...'
    sudo rm -r "${PWD}"/reports/horusec/$SO_USER_ID/$folder
fi 

cd "${PWD}"/reports/horusec/$SO_USER_ID
# Use clone or curl
if [ "$5" = "true" ]; then
    echo "[HORUSEC] Running curl..."
    curl --request GET --header "Accept: application/zip" --output "./$folder.zip" "$URL" && unzip -o ./$folder.zip -d ./$folder
else
    echo "[HORUSEC] Cloning repo..."
    git clone "$URL"
fi

if [ ! -d "${PWD}/$folder" ]; then
    echo "[HORUSEC] Repo wasn't cloned properly. Exiting."
    exit 2
fi 
cd ./"$folder"

DC_PROJECT="$folder"

cd ..
echo "[HORUSEC] Running Horusec..."
sudo horusec start -p $DC_PROJECT -o json -O ./report-horusec-$SO_TEST_ID.json --disable-docker true


# remove repo
if [ "$5" = "true" ]; then
    echo "[HORUSEC] Removing repo zip file..."
    sudo rm ./"$folder".zip
fi
echo "[HORUSEC] Removing repo folder..."
sudo rm -r ./"$folder"

echo "[HORUSEC] Horusec scan completed."
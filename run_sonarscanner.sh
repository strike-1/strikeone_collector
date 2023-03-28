#!/bin/sh

DC_VERSION="latest"
PROJECT_URL=$1
PROJECT_NAME=$2
SONARQUBE_TOKEN=$3
SONARQUBE_ADDRESS=$4
SO_USER_ID=$5
SO_TEST_ID=$6
USE_CURL=$7
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
    echo "SONARQUBE_TOKEN (3) argument is required."
    exit 22
fi

if [ -z "$4" ]; then
    echo "SONARQUBE_ADDRESS (4) argument is required."
    exit 22
fi

if [ -z "$5" ]; then
    echo "SO_USER_ID (5) argument is required."
    exit 22
fi

if [ -z "$6" ]; then
    echo "SO_TEST_ID (6) argument is required."
    exit 22
fi

if [ -z "$7" ] || [ "$7" != "true" ]; then
    USE_CURL="false" 
fi

# PLATFORM REPOSITORY
URL="$PROJECT_URL"

if [ -d "${PWD}/reports/sonarscanner/$SO_USER_ID" ]; then
    echo "Reports folder already exists."
else
    echo "Reports folder doesn't exist. Creating..."
    sudo mkdir -p "${PWD}"/reports/sonarscanner/$SO_USER_ID
fi

# Naming folder by repo name
folder=$PROJECT_NAME

if [ -d "${PWD}/reports/sonarscanner/$SO_USER_ID/$folder" ]; then
    echo 'Folder already exists, deleting...'
    sudo rm -r "${PWD}"/reports/sonarscanner/$SO_USER_ID/$folder
fi 

cd "${PWD}"/reports/sonarscanner/$SO_USER_ID
# Use clone or curl
if [ "$7" = "true" ]; then
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

sudo docker pull sonarsource/sonar-scanner-cli:$DC_VERSION
sudo docker run --rm \
    -e SONAR_HOST_URL="$SONARQUBE_ADDRESS" \
    -e SONAR_SCANNER_OPTS="-Dsonar.projectKey=$PROJECT_NAME" \
    -e SONAR_LOGIN="$SONARQUBE_TOKEN" \
    -v "${PWD}:/usr/src" \
    sonarsource/sonar-scanner-cli

# remove repo
cd ..
if [ "$7" = "true" ]; then
    sudo rm ./"$folder".zip
fi
sudo rm -r ./"$folder"
#!/bin/sh

DC_VERSION="latest"
PROJECT_URL=$1
PROJECT_NAME=$2
PROJECT_BRANCH=$3
SONARQUBE_TOKEN=$4
SONARQUBE_ADDRESS=$5
SO_USER_ID=$6
SO_TEST_ID=$7
USE_CURL=$8
EXCLUSIONS=$9
URL=""

if [ -z "$1" ]; then
    echo "[SONARSCANNER] PROJECT_URL (1) argument is required."
    exit 22
fi

if [ -z "$2" ]; then
    echo "[SONARSCANNER] PROJECT_NAME (2) argument is required."
    exit 22
fi

if [ -z "$3" ]; then
    echo "[SONARSCANNER] PROJECT_BRANCH (3) argument is required."
    exit 22
fi

if [ -z "$4" ]; then
    echo "[SONARSCANNER] SONARQUBE_TOKEN (4) argument is required."
    exit 22
fi

if [ -z "$5" ]; then
    echo "[SONARSCANNER] SONARQUBE_ADDRESS (5) argument is required."
    exit 22
fi

if [ -z "$6" ]; then
    echo "[SONARSCANNER] SO_USER_ID (6) argument is required."
    exit 22
fi

if [ -z "$7" ]; then
    echo "[SONARSCANNER] SO_TEST_ID (7) argument is required."
    exit 22
fi

if [ -z "$8" ] || [ "$8" != "true" ]; then
    USE_CURL="false"
fi

# PLATFORM REPOSITORY
URL="$PROJECT_URL"

if [ -d "${PWD}/reports/sonarscanner/$SO_USER_ID" ]; then
    echo "[SONARSCANNER] Reports folder already exists."
else
    echo "[SONARSCANNER] Reports folder doesn't exist. Creating..."
    sudo mkdir -p "${PWD}"/reports/sonarscanner/$SO_USER_ID
fi

# Naming folder by repo name
folder=$PROJECT_NAME

if [ -d "${PWD}/reports/sonarscanner/$SO_USER_ID/$folder" ]; then
    echo '[SONARSCANNER] Folder already exists, deleting...'
    sudo rm -r "${PWD}"/reports/sonarscanner/$SO_USER_ID/$folder
fi

cd "${PWD}"/reports/sonarscanner/$SO_USER_ID
# Use clone or curl
if [ "$8" = "true" ]; then
    echo "[SONARSCANNER] Running curl..."
    curl --request GET --header "Accept: application/zip" --output "./$folder.zip" "$URL" && unzip -o ./$folder.zip -d ./$folder
else
    echo "[SONARSCANNER] Cloning repo using "$PROJECT_BRANCH" branch..."
    git clone --branch "$PROJECT_BRANCH" "$URL"
fi

if [ ! -d "${PWD}/$folder" ]; then
    echo "[SONARSCANNER] Repo wasn't cloned properly. Exiting."
    exit 2
fi
cd ./"$folder"

DC_PROJECT="$folder"

echo "[SONARSCANNER] Running Docker..."
sudo docker pull sonarsource/sonar-scanner-cli:$DC_VERSION

if [ -n "$9" ]; then
    echo "[SONARSCANNER] SonarQube Scan have exclusions (9)"
    sudo docker run --rm \
        -e SONAR_HOST_URL="$SONARQUBE_ADDRESS" \
        -e SONAR_SCANNER_OPTS="-Dsonar.projectKey=$PROJECT_NAME -Dsonar.exclusions=$EXCLUSIONS" \
        -e SONAR_TOKEN="$SONARQUBE_TOKEN" \
        -v "${PWD}:/usr/src" \
        sonarsource/sonar-scanner-cli
fi

if [ -z "$9" ]; then
    sudo docker run --rm \
        -e SONAR_HOST_URL="$SONARQUBE_ADDRESS" \
        -e SONAR_SCANNER_OPTS="-Dsonar.projectKey=$PROJECT_NAME" \
        -e SONAR_TOKEN="$SONARQUBE_TOKEN" \
        -v "${PWD}:/usr/src" \
        sonarsource/sonar-scanner-cli

fi

# remove repo
cd ..
if [ "$8" = "true" ]; then
    echo "[SONARSCANNER] Removing repo zip file..."
    sudo rm ./"$folder".zip
fi
echo "[SONARSCANNER] Removing repo folder..."
sudo rm -r ./"$folder"

echo "[SONARSCANNER] Scan completed."

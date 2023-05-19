#!/bin/sh

DC_VERSION="latest"
DC_DIRECTORY=$HOME/OWASP-Dependency-Check
PROJECT_URL=$1
PROJECT_NAME=$2
SO_USER_ID=$3
SO_TEST_ID=$4
USE_CURL=$5
DATA_DIRECTORY="$DC_DIRECTORY/data"
CACHE_DIRECTORY="$DC_DIRECTORY/data/cache"
URL=""

if [ -z "$1" ]; then
    echo "[OWASP DEP CHECK] PROJECT_URL (1) argument is required."
    exit 22
fi

if [ -z "$2" ]; then
    echo "[OWASP DEP CHECK] PROJECT_NAME (2) argument is required."
    exit 22
fi

if [ -z "$3" ]; then
    echo "[OWASP DEP CHECK] SO_USER_ID (3) argument is required."
    exit 22
fi

if [ -z "$4" ]; then
    echo "[OWASP DEP CHECK] SO_TEST_ID (4) argument is required."
    exit 22
fi

if [ -z "$5" ] || [ "$5" != "true" ]; then
    USE_CURL="false" 
fi

if [ ! -d "$DATA_DIRECTORY" ]; then
    echo "[OWASP DEP CHECK] Creating persistent directory: $DATA_DIRECTORY"
    mkdir -p "$DATA_DIRECTORY"
fi
if [ ! -d "$CACHE_DIRECTORY" ]; then
    echo "[OWASP DEP CHECK] Creating persistent directory: $CACHE_DIRECTORY"
    mkdir -p "$CACHE_DIRECTORY"
fi

# PLATFORM REPOSITORY
URL="$PROJECT_URL"

if [ -d "${PWD}/reports/dep_check/$SO_USER_ID" ]; then
    echo "[OWASP DEP CHECK] Reports folder already exists."
else
    echo "[OWASP DEP CHECK] Reports folder doesn't exist. Creating..."
    sudo mkdir -p "${PWD}"/reports/dep_check/$SO_USER_ID
fi

# Naming folder by repo name
folder=$PROJECT_NAME

if [ -d "${PWD}/reports/dep_check/$SO_USER_ID/$folder" ]; then
    echo '[OWASP DEP CHECK] Folder already exists, deleting...'
    sudo rm -r "${PWD}"/reports/dep_check/$SO_USER_ID/$folder
fi 

cd "${PWD}"/reports/dep_check/$SO_USER_ID
# Use clone or curl
if [ "$5" = "true" ]; then
    echo "[OWASP DEP CHECK] Running curl..."
    curl --request GET --header "Accept: application/zip" --output "./$folder.zip" "$URL" && unzip -o ./$folder.zip -d ./$folder
else
    echo "[OWASP DEP CHECK] Cloning repo..."
    git clone "$URL"
fi

if [ ! -d "${PWD}/$folder" ]; then
    echo "[OWASP DEP CHECK] Repo wasn't cloned properly. Exiting."
    exit 2
fi 
cd ./"$folder"

# run yarn to install modules
echo "[OWASP DEP CHECK] Running yarn..."
yarn

DC_PROJECT="$folder"

cd ..
echo "[OWASP DEP CHECK] Running Docker..."
sudo docker pull owasp/dependency-check:$DC_VERSION
sudo docker run --rm \
    -e user=$USER \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    --volume $(pwd):/src:z \
    --volume "$DATA_DIRECTORY":/usr/share/dependency-check/data:z \
    --volume $(pwd)/odc-reports:/report:z \
    owasp/dependency-check:$DC_VERSION \
    --scan  ./$folder \
    --format "JSON" \
    --project "$DC_PROJECT" \
    --out ./report-dep-check-$SO_TEST_ID.json

# remove repo
if [ "$5" = "true" ]; then
    echo "[OWASP DEP CHECK] Removing repo zip file..."
    sudo rm ./"$folder".zip
fi
echo "[OWASP DEP CHECK] Removing repo folder..."
sudo rm -r ./"$folder"

echo "[OWASP DEP CHECK] Dependency check completed."
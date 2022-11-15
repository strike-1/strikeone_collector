#!/bin/sh

DC_VERSION="latest"
DC_DIRECTORY=$HOME/OWASP-Dependency-Check
PROJECT_REPO=$1
PLATFORM=$2
USER_REPO=$3 #If type is azure, use org name
TOKEN=$4
SO_USER_ID=$5
SO_TEST_ID=$6
DATA_DIRECTORY="$DC_DIRECTORY/data"
CACHE_DIRECTORY="$DC_DIRECTORY/data/cache"
URL=""

if [ -z "$1" ]; then
    echo "PROJECT_REPO (1) argument is required."
    exit 22
fi

if [ -z "$2" ]; then
    echo "PLATFORM (2) argument is required."
    exit 22
fi

if [ -z "$3" ]; then
    echo "USER_REPO (3) argument is required."
    exit 22
fi

if [ -z "$4" ]; then
    echo "TOKEN (4) argument is required."
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

if [ ! -d "$DATA_DIRECTORY" ]; then
    echo "Initially creating persistent directory: $DATA_DIRECTORY"
    mkdir -p "$DATA_DIRECTORY"
fi
if [ ! -d "$CACHE_DIRECTORY" ]; then
    echo "Initially creating persistent directory: $CACHE_DIRECTORY"
    mkdir -p "$CACHE_DIRECTORY"
fi

# PLATFORM REPOSITORY
if [ "$PLATFORM" = "github" ]; then
    URL="https://$USER_REPO:$TOKEN@github.com/$USER_REPO/$PROJECT_REPO.git"
fi
if [ "$PLATFORM" = "gitlab" ]; then
    GROUP=$5
    URL="https://$USER_REPO:$TOKEN@gitlab.com/$GROUP/$PROJECT_REPO.git"
fi
if [ "$PLATFORM" = "azure" ]; then
    URL="https://$USER_REPO:$TOKEN@dev.azure.com/$USER_REPO/$PROJECT_REPO/_git/$PROJECT_REPO"
fi
if [ "$PLATFORM" = "bitbucket" ]; then
    URL="https://$USER_REPO:$TOKEN@bitbucket.org/$USER_REPO/$PROJECT_REPO.git"
fi

if [ -d "${PWD}/reports/dep_check/$SO_USER_ID" ]; then
    echo "Reports folder already exists."
else
    echo "Reports folder doesn't exist. Creating..."
    sudo mkdir -p "${PWD}"/reports/dep_check/$SO_USER_ID
fi

# Naming folder by repo name
folder=$PROJECT_REPO

if [ -d "${PWD}/reports/dep_check/$SO_USER_ID/$folder" ]; then
    echo 'Folder already exists, deleting...'
    sudo rm -r "${PWD}"/reports/dep_check/$SO_USER_ID/$folder
fi 

cd "${PWD}"/reports/dep_check/$SO_USER_ID
git clone "$URL"

if [ ! -d "${PWD}/$folder" ]; then
    echo "Repo wasn't cloned properly. Exiting."
    exit 2
fi 
cd ./"$folder"

# run npm to install modules
echo "Running npm install..."
npm install

DC_PROJECT="$folder"

cd ..
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
sudo rm -r ./"$folder"
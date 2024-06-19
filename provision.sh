#!/bin/bash

set -e

git clone -n --depth=1 --filter=tree:0 https://github.com/receevi/receevi | true
pushd receevi
git sparse-checkout set --no-cone supabase
git checkout
git pull
popd

if [ ! -f ./.env ]; then
    cp ./.env.example ./.env
fi

./setup-python.sh

source .venv/bin/activate
python initialize-variables.py

./supabase.sh

source supabase/docker/.env

docker compose up -d

# supabase db push --db-url "postgres://user:pass@127.0.0.1:5432/postgres"

if ! command -v supabase &> /dev/null
then
    mkdir -p tmp
    pushd tmp
    curl -L -o supabase_1.175.0_linux_amd64.deb https://github.com/supabase/cli/releases/download/v1.175.0/supabase_1.175.0_linux_amd64.deb
    sudo dpkg -i supabase_1.175.0_linux_amd64.deb
    popd
fi

echo "Sleeping for 10 seconds..."
sleep 10

pushd receevi
yes | supabase db push --db-url "postgres://postgres:$POSTGRES_PASSWORD@127.0.0.1:5432/$POSTGRES_DB"
# supabase functions deploy
popd

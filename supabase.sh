#!/bin/bash

set -e

git clone -n --depth=1 --filter=tree:0 https://github.com/supabase/supabase | true
pushd supabase
git sparse-checkout set --no-cone docker
git checkout
git pull

if [ ! -f ./docker/.env ]; then
    cp ./docker/.env.example ./docker/.env
fi

cp -r ../receevi/supabase/functions/* ./docker/volumes/functions
rm -f ./docker/volumes/functions/_shared/database.types.ts
cp ../receevi/lib/database.types.ts ./docker/volumes/functions/_shared/database.types.ts

popd

source .venv/bin/activate
python setup-supabase.py

pushd supabase/docker

docker compose up -d # kong auth rest realtime storage functions analytics db
popd

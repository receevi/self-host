#!/bin/bash

set -e

pushd supabase/docker
docker compose down -v
popd

docker compose down -v

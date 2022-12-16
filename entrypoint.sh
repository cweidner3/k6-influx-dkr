#!/bin/bash
set -e

if [[ $APP_USE_WEBSERVER == '1' ]]; then
    echo ":: Starting webserver..."
    export FLASK_APP=server.main:app
    /venv/bin/python -m flask \
        run \
        --host "${APP_WEBSERVER_HOST:-0.0.0.0}" \
        --port "${APP_WEBSERVER_PORT:-5050}"
    exit $?
fi

echo ":: User $(id -u):$(id -g) $USER"

echo ":: Storing test script..."
cat > main.js < /dev/stdin

# echo ":: main.js"
# cat main.js
# echo "------------------------------------------------------------"

echo ":: Running webpack..."
npm run-script webpack

# echo ":: build/app.bundle.js"
# cat build/app.bundle.js
# echo "------------------------------------------------------------"

echo ":: Running test script..."
k6 run "${@}" build/app.bundle.js

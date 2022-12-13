#!/bin/bash
set -e

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

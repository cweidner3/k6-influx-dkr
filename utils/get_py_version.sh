#!/usr/bin/env python3

DIR="$(cd "$(dirname "$0")" && pwd)"

sed -n -E \
    -e "s~.*version='([^']+)'.*~\\1~p" \
    "${DIR}/../setup.py" \
    | tr -d '\n'

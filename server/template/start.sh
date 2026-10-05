#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
# Set JAVA_EXE to a Java 25 binary if it is not on PATH.
JAVA_EXE="${JAVA_EXE:-java}"
version="$("$JAVA_EXE" -version 2>&1 | sed -n 's/.*version "\([^"]*\)".*/\1/p' | head -n 1)" || version=""
major="${version%%[.+-]*}"
if [[ ! "$major" =~ ^[0-9]+$ ]] || (( major < 25 )); then
    printf 'Java 25 or newer is required. Found: %s\nSet JAVA_EXE to the Java 25 binary path.\n' "${version:-not available}" >&2
    exit 1
fi
if [[ ! -f fabric-server-launch.jar ]]; then
    printf 'Missing fabric-server-launch.jar. Complete the server build first.\n' >&2
    exit 1
fi
exec "$JAVA_EXE" -Xms1G -Xmx@RAM@ -XX:+UseG1GC -jar fabric-server-launch.jar nogui

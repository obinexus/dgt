#!/bin/bash
set -e

# Clean
rm -f demo_diram

# Compile
gcc -std=c99 -Iinclude -Wall -Wextra \
    src/main.c -o demo_diram

echo "Build OK → ./demo_diram"

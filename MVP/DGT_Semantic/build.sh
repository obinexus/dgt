#!/bin/bash
set -e  # Exit on any error

echo "=== DGT Semantic Build & Launch ==="
echo "Date: $(date)"
echo "Dir: $(pwd)"

# --- CLEAN ---
echo "🧹 Cleaning previous builds..."
rm -f demo_diram
rm -rf __pycache__  # Clean Python cache if any

# --- PYTHON DEPS (User install, idempotent) ---
echo "🐍 Installing/Updating Python deps..."
packages="textual markdown beautifulsoup4"
for pkg in $packages; do
    if ! python -c "import $pkg" 2>/dev/null; then
        echo "Installing $pkg..."
        python -m pip install --user $pkg || echo "⚠️  $pkg install skipped (perms or already done)"
    else
        echo "✅ $pkg already available"
    fi
done

# --- COMPILE C DEMO ---
echo "🔨 Compiling Di-RAM C demo..."
if gcc -std=c99 -Iinclude -Wall -Wextra src/main.c -o demo_diram; then
    echo "✅ C build OK → ./demo_diram"
else
    echo "❌ C compile failed – check src/main.c"
    exit 1
fi

# --- POST-BUILD UNION: Run Demo + Launch WSYS Editor ---
echo "🚀 Post-build launch..."
echo "--- Running C Demo ---"
./demo_diram

echo "--- Launching WSYS Editor on docs/DGT_SEMANTIC.md ---"
if [ -f "wsys/wsys_poc/wsys.py" ] && [ -f "docs/DGT_SEMANTIC.md" ]; then
    python wsys/wsys_poc/wsys.py docs/DGT_SEMANTIC.md
else
    echo "⚠️  WSYS or MD file missing – skipping editor launch"
    echo "Run manually: python wsys/wsys_poc/wsys.py docs/DGT_SEMANTIC.md"
fi

echo "=== Build Complete! ==="

#!/bin/bash
set -e

# Usage:
#   ./seal.sh                 # seal from current directory
#   ./seal.sh path/to/dir     # seal recursively inside directory
#   ./seal.sh path/to/file    # seal only that file

TARGET="${1:-.}"

# ---- Validate target ----
if [ ! -e "$TARGET" ]; then
  echo "Error: '$TARGET' does not exist."
  exit 1
fi

seal_file() {
  local file="$1"
  local base="$(basename "$file")"

  # Skip files already named sealed-*
  if [[ "$base" == sealed-* ]]; then
    echo "Skipping already sealed file: $file"
    return
  fi

  # Skip files without -secret.yaml
  if [[ "$file" != *-secret.yaml ]]; then
    echo "Skipping (not a *-secret.yaml file): $file"
    return
  fi

  local dir="$(dirname "$file")"
  local sealed_file="$dir/sealed-$base"

  # Skip if sealed file already exists
  if [ -f "$sealed_file" ]; then
    echo "Skipping (sealed already exists): $file"
    return
  fi

  echo "Sealing $file -> $sealed_file"
  kubeseal --format yaml < "$file" > "$sealed_file"
}

# ---- Process based on type ----
if [ -d "$TARGET" ]; then
  echo "Sealing all secrets under directory: $TARGET"
  echo

  find "$TARGET" -type f -name "*-secret.yaml" | while read -r file; do
    seal_file "$file"
  done

elif [ -f "$TARGET" ]; then
  echo "Sealing single file: $TARGET"
  echo

  seal_file "$TARGET"
else
  echo "Error: '$TARGET' is neither a file nor a directory."
  exit 1
fi

echo
echo "Sealing completed!"

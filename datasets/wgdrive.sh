#!/usr/bin/env bash
# gdrive2wget.sh
# Usage: ./gdrive2wget.sh "https://drive.google.com/file/d/1abcDEFgHiJkLmnopQRsTuvWxYZ/view?usp=sharing" "my-data.zip"

set -e

link="$1"
outfile="$2"

if [[ -z "$link" || -z "$outfile" ]]; then
  echo "Usage: $0 <google-drive-link> <output-file>"
  exit 1
fi

# Grab the first 25-to-50-character blob of letters/digits/-/_ (covers every Drive ID form).
id="$(echo "$link" | grep -oE '[-_0-9A-Za-z]{25,}' | head -1)"

if [[ -z "$id" ]]; then
  echo "Could not find a Drive file ID in: $link" >&2
  exit 2
fi

# Build the wget command
cmd="wget -O \"$outfile\" \"https://drive.usercontent.google.com/download?id=$id&export=download&confirm=yes\""

echo "$cmd"      # show it
# Uncomment next line if you want the script to execute it automatically:
eval "$cmd"


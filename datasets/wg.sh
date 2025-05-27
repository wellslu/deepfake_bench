FILE_ID="1N4X3rvx9IhmkEZK-KIk4OxBrQb9BRUcs"
OUT="FaceForensics++.zip"
COOKIE=$(mktemp)

# 第一次請求：一定要 docs.google.com/uc
CONFIRM=$(wget -q --save-cookies "$COOKIE" --keep-session-cookies \
  "https://docs.google.com/uc?export=download&id=${FILE_ID}" -O - |
  grep -oP '(?<=confirm=)[0-9A-Za-z_]+' )

[ -z "$CONFIRM" ] && { echo "✗ 需要登入或尚未同意 TOS"; exit 1; }

wget --load-cookies "$COOKIE" \
     "https://docs.google.com/uc?export=download&confirm=${CONFIRM}&id=${FILE_ID}" \
     -O "$OUT" --continue

rm -f "$COOKIE"
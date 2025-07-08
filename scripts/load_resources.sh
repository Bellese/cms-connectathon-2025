#!/bin/bash

set -euo pipefail

FHIR_SERVER_URL="https://connectathon.fhir-sandbox.bellese.dev/fhir"
RESOURCE_MANIFEST="${RESOURCE_MANIFEST:-resource_list.json}"

TMP_DIR="/tmp/ig-loader"
mkdir -p "$TMP_DIR"

echo "Reading resource manifest: $RESOURCE_MANIFEST"
manifest=$(cat "$RESOURCE_MANIFEST")

load_ig() {
  local name="$1"
  local canonical_url="$2"
  local url="$3"
  local path="$TMP_DIR/$name.tgz"
  local extract_dir="$TMP_DIR/$name"

  echo "Checking if IG $name is already loaded by canonical URL..."
  # one-liner python script needed to url-encode the canonical url
  encoded_url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$canonical_url'''))")
  is_loaded=$(curl -s "$FHIR_SERVER_URL/ImplementationGuide?url:below=$encoded_url&_summary=count" | jq -r '.total // 0')

  if [[ "$is_loaded" -gt 0 ]]; then
    echo "IG $name already exists, skipping."
    return
  fi

  echo "Downloading IG: $name from $url"
  curl -Ls "$url" -o "$path"

  echo "Installing IG package using \$install..."
  encoded=$(base64 -i "$path")

  payload_path="$TMP_DIR/${name}_payload.json"
  cat > "$payload_path" <<EOF
{
  "resourceType": "Parameters",
  "parameter": [
    {
      "name": "npmContent",
      "valueBase64Binary": "$encoded"
    },
    {
      "name": "installMode",
      "valueString": "STORE_AND_INSTALL"
    }
  ]
}
EOF

  curl -s -X POST "$FHIR_SERVER_URL/ImplementationGuide/\$install" \
    -H "Content-Type: application/json" \
    -d @"$payload_path"

# Manually extract IG resource from tar and upload it
  echo "Extracting IG resource manually..."
  mkdir -p "$extract_dir"
  tar -xzf "$path" -C "$extract_dir" >/dev/null 2>&1

  IG_FILE=$(find "$extract_dir/package" -iname "ImplementationGuide-*.json" 2>/dev/null | head -n 1)

  if [[ -f "$IG_FILE" ]]; then
    echo "Uploading ImplementationGuide resource directly..."
    # Delete reference fields from .defintion.resource array to avoid validation errors
    STRIPPED_IG_JSON=$(jq 'del(.definition.resource[]?.reference)' "$IG_FILE")

    IG_ID=$(jq -r '.id' <<< "$STRIPPED_IG_JSON")
    if [[ -z "$IG_ID" || "$IG_ID" == "null" ]]; then
      IG_ID="$name"
      STRIPPED_IG_JSON=$(jq --arg id "$IG_ID" '.id = $id' <<< "$STRIPPED_IG_JSON")
    fi

    # PUT to avoid duplicating IG resources
    response=$(curl -s -X PUT "$FHIR_SERVER_URL/ImplementationGuide/$IG_ID" \
      -H "Content-Type: application/fhir+json" \
      -d "$STRIPPED_IG_JSON")

    echo "$response" | jq -r '.issue[]?.diagnostics // empty'
    echo "ImplementationGuide resource uploaded."
  else
    echo "Could not find ImplementationGuide JSON in package."
  fi

  rm -rf "$payload_path" "$extract_dir"
}


load_valueset() {
  local name="$1"
  local url="$2"
  local path="$TMP_DIR/$name.json"

  echo "Checking if ValueSet $name is already loaded..."
  is_loaded=$(curl -s "$FHIR_SERVER_URL/ValueSet?name=$name&_summary=count" | jq '.total')
  if [[ "$is_loaded" -gt 0 ]]; then
    echo "ValueSet $name already exists, skipping."
    return
  fi

  echo "Downloading ValueSet: $name from $url"
  curl -Ls "$url" -o "$path"

  echo "Uploading ValueSet: $name to $FHIR_SERVER_URL/ValueSet"
  curl -s -X POST "$FHIR_SERVER_URL/ValueSet" \
    -H "Content-Type: application/fhir+json" \
    -d @"$path"

  echo "ValueSet $name loaded."
}

# Load IGs
echo "$manifest" | jq -c '.implementation_guides[]' | while read -r ig; do
  name=$(echo "$ig" | jq -r '.name')
  canonical=$(echo "$ig" | jq -r '.canonical_url')
  url=$(echo "$ig" | jq -r '.source')
  load_ig "$name" "$canonical" "$url"
done


# Load ValueSets
echo "$manifest" | jq -c '.value_sets[]' | while read -r vs; do
  name=$(echo "$vs" | jq -r '.name')
  url=$(echo "$vs" | jq -r '.source')
  load_valueset "$name" "$url"
done

echo "All resources processed."

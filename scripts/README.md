# IG & ValueSet Loader Script for HAPI FHIR

This script automates the loading of FHIR Implementation Guides (IGs) and ValueSets into a HAPI FHIR server. It ensures resources are not duplicated and leverages the `$install` operation for proper installation of IG packages.

## What Does it Do?

- Loads IG packages (.tgz) using the FHIR `$install` operation
- Uploads the ImplementationGuide resource separately using a PUT request to avoid duplication (the IG Resources was not persisting with the `$install` operation alone)
- Optionally loads ValueSets
- Skips loading if the resource is already present based on the canonical URL or name
- Cleans up temporary files automatically

## Prerequisites

- The following tools installed:
  - curl
  - jq
  - tar
  - base64
  - python3 (for encoding)
- A valid resource_list.json file
- Env var `FHIR_SERVER_URL` set to the HAPI FHIR server's base URL

## How to use it?
- Set the FHIR Env var `export FHIR_SERVER_URL=https://your.fhir.server/fhir`
- Run the script `./load_resources.sh`

## How to check which IGs are loaded?
- The script takes measures to prevent duplication, but just in case you can check using the curl statement below how many of which IGs are loaded
```
curl -s "$FHIR_SERVER_URL/ImplementationGuide?_count=1000" \
  | jq -r '.entry[].resource.url' | sort | uniq -c
```

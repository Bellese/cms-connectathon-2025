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

# import_testcases.py

This script imports FHIR JSON testcases to a FHIR server.
Follow these steps to run it:

1. **Install dependencies**  
   ```bash
   make install
   # or
   pip install -r requirements.txt
   ```
2. **Prepare your test data directory**  
   - By default, the script looks in `test/`.  
   - Alternatively, you can pass a path to any root folder as the first argument.  
   - That directory must contain one subdirectory per measure, for example:  
     ```text
     test/
     ├── CMS122FHIR-v0.5.000-FHIR6-TestCases/
     ├── CMS165FHIR-v0.5.000-FHIR6-TestCases/
     └── CMS506FHIR-v0.3.005-FHIR6-TestCases/
     ```

3. **Run the script**  
   ```bash
   python scripts/import_testcases.py [--verbose]
   ```
   - Omitting the folder argument defaults to `test/`.  
   - Use `--verbose` for debug logging.

4. **Check exit codes**  
   - `0` → All testcases uploaded successfully  
   - `1` → Invalid arguments or directory not found  
   - `2` → Some uploads failed

**Example:**  
```bash
python scripts/import_testcases.py
```

# evaluate_tests.py

This script fetches each uploaded `MeasureReport` from the FHIR server and checks that the population code encoded in the filename (e.g. `denom`, `denomexcept`) has a non-zero count.

1. **Install dependencies**  
   ```bash
   make install  # or: pip install -r requirements.txt
   ```
2. **Ensure your test data is in** `test/` **folder (or supply a path)**  
   The folder must contain one subdirectory per measure, each with JSON files named like `MeasureID-PopulationCode.json`.
3. **Run the script**  
   ```bash
   python scripts/evaluate_tests.py [<test_root_directory>] [--verbose]
   ```
   - Defaults to `test/` if no directory is provided.  
   - `--verbose` enables debug logs.
4. **Check exit codes**  
   - `0` → All testcases passed  
   - `1` → Invalid arguments or directory not found  
   - `2` → One or more testcases failed

**Example:**  
```bash
python scripts/evaluate_tests.py --verbose
```
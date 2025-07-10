# CMS Connectathon 2025 – DEQM Testing Repository

This repository is a central hub for materials related to the CMS Connectathon 2025, focused on DEQM (Data Exchange for Quality Measures) testing.

It includes:

- Scripts and tooling to interact with the Bellese-hosted FHIR server  
- Test data sets and supporting artifacts  
- Guidance for evaluating measures  

# FHIR Server

FHIR Base URL:  
https://connectathon.fhir-sandbox.bellese.dev/fhir/

Swagger UI:  
https://connectathon.fhir-sandbox.bellese.dev/fhir/swagger-ui/

The Bellese FHIR server is running HAPI FHIR JPA Server version 8.2 and is pre-loaded with the following Implementation Guides:

- US Core 6.1.0  
- CQF Measures 5.0.0  
- Da Vinci DEQM 5.0.0  
- QICore 6.0.0  

# Value Sets

For Bellese’s test environment, value sets were pulled from the VSAC 2025 eCQM download page:  
https://vsac.nlm.nih.gov/download/ecqm?rel=2025  
and expanded using the VSAC FHIR API.

# Measures on the Server

You can discover loaded measures using the FHIR Measure search endpoint.

## Option 1: Swagger UI

Navigate to:  
https://connectathon.fhir-sandbox.bellese.dev/fhir/swagger-ui/

Then:  
1. Expand the Measure section.  
2. Use the GET /Measure endpoint.  
3. Click "Try it out" and then "Execute".  
4. The server will return a Bundle of all Measure resources currently available.

## Option 2: API Call (Get All Measures)

```
curl -X GET "https://connectathon.fhir-sandbox.bellese.dev/fhir/Measure" \
     -H "Accept: application/fhir+json"
```

This returns a JSON Bundle of all Measure resources. You can inspect id, name, and url fields to identify what's available.

# How to Evaluate One or More Measures

The `/fhir/Measure/$evaluate` operation can be used to evaluate one or more measures on the server.
Include one or more `measureId` query parameters in your request with the IDs of the measures to be evaluated.
Refer to the [HL7 documentation](https://build.fhir.org/ig/HL7/davinci-deqm/OperationDefinition-evaluate.html)
for details on the `$evaluate` operation and its parameters.

This sample GET URL evaluates two parameters for a single patient:

```
https://connectathon.fhir-sandbox.bellese.dev/fhir/Measure/$evaluate?measureId==CMS816FHIRHHHypo&measureId==CMS506FHIRSafeUseofOpioids&periodStart==2026-01-01&periodEnd==2026-12-31&subject==1d298cf0-aa38-4943-ba4c-f7209cf59e63&reportType=subject
````

This curl command sends the sample request to the Bellese server.
The result should be a JSON encoded [Bundle resource](https://hl7.org/fhir/R4/bundle.html).

```
curl --get \
     --header 'Accept: application/fhir+json' \
     --data 'measureId=CMS816FHIRHHHypo' \
     --data 'measureId=CMS506FHIRSafeUseofOpioids' \
     --data 'periodStart=2026-01-01' \
     --data 'periodEnd=2026-12-31' \
     --data 'subject=1d298cf0-aa38-4943-ba4c-f7209cf59e63' \
     --data 'reportType=subject' \
     'https://connectathon.fhir-sandbox.bellese.dev/fhir/Measure/$evaluate'
```

# Contributing

Contributions and issues are welcome as we prepare for the Connectathon. Please open a pull request or issue with questions or additions.

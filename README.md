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
and expanded using the VSAC FHIR API. Each organization may use their own methods or tools to load value sets.

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

# How to Test Evaluating a Measure

todo

# How to Test Evaluating Multiple Measures

todo

# Contributing

Contributions and issues are welcome as we prepare for the Connectathon. Please open a pull request or issue with questions or additions.
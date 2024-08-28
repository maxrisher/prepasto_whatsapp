# prepasto_whatsapp

# Django hosted on railway

# AWS lambdas
Versioning:
- There is a 'production' and a 'stagingAlias' version of the lambda. The produciton version needs to be set manually in template.yaml. The stagingAlias version is always the most recently deployed one.

Deployment: 
- Download docker and the 'aws sam' CLI
- Run docker on your machine. 
- from the top level directory run: sam build --use-container
- run: sam build
- go through the menus
- You need to update the RAILWAY_PUBLIC_DOMAIN in the lambda to reflect either production or staging depending on what's needed

Environmental variables: NB that the lambda code requires environmental variables. You need to input these directly into the AWS management console by hand. To update the variables in the staging or production lambda versions **you must redeploy the lambdas**

Useful commands:
- To see lambda function versions:
aws lambda list-versions-by-function --function-name prepasto-whatsapp-sam-app-ProcessMessageFunction-ARnDrJlrXR28

# Testing

# TODOs:
- Get a LEGIT whatsapp account (!)
- integrate AWS layers into the testing environment
- Should I try to have all tests (django and pytest) run when I call pytest?
- use dataclasses for dish objects "from dataclasses import dataclass, asdict"

# Useful links
## Whatsapp
Sending messages: https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages
postman: https://www.postman.com/meta/whatsapp-business-platform/overview
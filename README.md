# prepasto_whatsapp
## whatsapp_bot

# Django hosted on railway
## Development
### Deployment
Make a whatsapp user for the site:
whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=14153476103)
### Gotchas
- Make sure when you're creating a new admin user on a new pull request version of the site: change your database url in the .env. Restart your terminal. THEN go ahead and make the superuser.

# AWS lambdas
Versioning:
- There is a 'production' and a 'stagingAlias' version of the lambda. The produciton version needs to be set manually in template.yaml. The stagingAlias version is always the most recently deployed one.

Deployment: 
- Download docker and the 'aws sam' CLI
- Run docker on your machine. 
- from the top level directory run: sam build --use-container
- run: sam deploy
- go through the menus
- You need to update the RAILWAY_PUBLIC_DOMAIN in the lambda to reflect either production or staging depending on what's needed

Environmental variables: NB that the lambda code requires environmental variables. You need to input these directly into the AWS management console by hand. To update the variables in the staging or production lambda versions **you must redeploy the lambdas**

Useful commands:
- To see lambda function versions:
aws lambda list-versions-by-function --function-name prepasto-whatsapp-sam-app-ProcessMessageFunction-ARnDrJlrXR28

# Testing

# Creating a new feature
- Change the railway url on AWS
- Change the AWS alias on railway

# TODOs:
## general
- Update testing of main app models
- Rotate secrets
- Handle users changing timezones
- use dataclasses for dish objects "from dataclasses import dataclass, asdict"
- index the direction and timestamp fields for better query performance of messages

## security
- Turn off debug on production django site
- Improve authentication method for django lambda webhook

# Useful links
## Whatsapp
Sending messages: https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages
postman: https://www.postman.com/meta/whatsapp-business-platform/overview

# Env variables
- Railway
- .env local file
- aws lambda
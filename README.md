# prepasto_whatsapp
## whatsapp_bot

# Django hosted on railway
## Development
### Hacking
Tailwind command
python manage.py tailwind start

### Deployment
Make a whatsapp user for the site:
from whatsapp_bot.models import WhatsappUser
whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id='14153476103')
print(created)

Tailwind
- python manage.py tailwind build
### Gotchas
- Make sure when you're creating a new admin user on a new pull request version of the site: change your database url in the .env. Restart your terminal. THEN go ahead and make the superuser.

# AWS lambdas
Versioning:
- There is a 'production', 'stagingAlias', and 'pullRequestAlias' version of the lambda. The production and staging versions need to be set manually in template.yaml. The pullRequestAlias version is always the most recently deployed one.

Deployment: 
- Download docker and the 'aws sam' CLI
- Run docker on your machine. 
- from the top level directory run: sam build --use-container
- run: sam deploy
- go through the menus
- You need to update the RAILWAY_PUBLIC_DOMAIN in the lambda to reflect either production or staging depending on what's needed

Environmental variables: NB that the lambda code requires environmental variables. These are stored in AWS Systems Manager Parameter Store. To update the variables **you must change the variable versions** or omit a version.

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
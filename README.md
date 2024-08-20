# prepasto_whatsapp

# Django hosted on railway

# AWS lambdas
Versioning:
- There is a 'production' and a 'stagingAlias' version of the lambda. The produciton version needs to be set manually in template.yaml. The stagingAlias version is always the most recently deployed one.

Deployment: 
- Run docker on your machine. 
- from the top level directory run: sam build --use-container
- run: sam build
- go through the menus

# Testing

# TODOs:
- Get a LEGIT whatsapp account (!)
- integrate AWS layers into the testing environment
- Should I try to have all tests (django and pytest) run when I call pytest?
- use dataclasses for dish objects "from dataclasses import dataclass, asdict"
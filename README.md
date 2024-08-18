# prepasto_whatsapp

# Django hosted on railway

# Lambdas hosted on AWS

# AWS layers
- to store the python dependencies for the lambdas
- This guy is created by running the following from the top level directory:
pip install -r requirements.txt -t aws_layer/python/

# Testing

# TODOs:
- integrate AWS layers into the testing environment
- Should I try to have all tests (django and pytest) run when I call pytest?
- use dataclasses for dish objects "from dataclasses import dataclass, asdict"
# prepasto_whatsapp

# Django hosted on railway

# Lambdas hosted on AWS
Packaging and uploading lambdas. Run:
python scripts/package_and_upload_lambdas.py 

# AWS layers
Packaging and uploading layers
1. From the top level directory, run: pip install -r requirements.txt -t aws_layer/python/ --upgrade
2. delete the layer.zip
3. From the aws_layer directory, run: zip -r layer.zip python/
4. From the top directory, run: aws lambda publish-layer-version --layer-name hummus_layer --zip-file fileb://aws_layer/layer.zip --compatible-runtimes python3.12

- to store the python dependencies for the lambdas

# Testing

# TODOs:
- integrate AWS layers into the testing environment
- Should I try to have all tests (django and pytest) run when I call pytest?
- use dataclasses for dish objects "from dataclasses import dataclass, asdict"
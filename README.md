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

1. pip freeze > requirements.txt
2. Copy requirements.txt to aws_layer
3. Go to aws_layer/
4. Start a docker container with the python 3.12 docker image:
docker run -it --rm -v $(pwd):/app -w /app python:3.12 /bin/bash
5. Within docker, download requirements.txt
pip install --no-cache-dir -r requirements.txt -t python/lib/python3.12/site-packages/
6. exit the docker container:
exit
7. zip up the new python packages into 'layer.zip':
zip -r9 layer.zip python/
8. Go to the top level directory and run:
aws lambda publish-layer-version --layer-name hummus_layer --zip-file fileb://aws_layer/layer.zip --compatible-runtimes python3.12

- to store the python dependencies for the lambdas

# Testing

# TODOs:
- Get a LEGIT whatsapp account (!)
- integrate AWS layers into the testing environment
- Should I try to have all tests (django and pytest) run when I call pytest?
- use dataclasses for dish objects "from dataclasses import dataclass, asdict"
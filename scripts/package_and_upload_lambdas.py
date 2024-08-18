import os
import subprocess
import boto3

def package_lambda(lambda_name):
    print(f"Current working directory: {os.getcwd()}")

    lambda_dir = f'lambda_functions/{lambda_name}'
    dist_dir = 'scripts'
    zip_file = f'{dist_dir}/{lambda_name}.zip'

    if os.path.exists(zip_file):
        os.remove(zip_file)

    #NB this assumes that lambda_dir is two folders deep from the project root!
    # go to the lambda directory, zip all its contents, then go up two directories, find the zip file destination directory and send our stuff there.
    subprocess.check_call(['zip', '-r', f'../../{zip_file}', '.'], cwd=lambda_dir)

    return zip_file

def upload_lambda(lambda_name, zip_file):
    client = boto3.client('lambda')

    with open(zip_file, 'rb') as f:
        response = client.update_function_code(
            FunctionName=lambda_name,
            ZipFile=f.read()
        )
    return response

def main():
    lambdas = ['process_message_lambda']

    for lambda_name in lambdas:
        print(f"Packaging {lambda_name}...")
        lam_zip = package_lambda(lambda_name)
        print(f"Uploading {lambda_name}...")
        response = upload_lambda(lambda_name, lam_zip)
        print(f"Uploaded {lambda_name}: {response['ResponseMetadata']['HTTPStatusCode']}")

if __name__ == '__main__':
    main()
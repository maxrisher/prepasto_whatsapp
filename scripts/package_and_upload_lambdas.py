import os
import subprocess
import boto3

# NB this assumes that this file is one step down from the project root AND that lambda functions is a folder in the project root
def package_lambda(lambda_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    lambda_dir = os.path.join(script_dir, '..', 'lambda_functions', lambda_name)
    dist_dir = script_dir
    zip_file = f'{dist_dir}/{lambda_name}.zip'

    # print(f"Script directory: {script_dir}")
    # print(f"Lambda directory: {lambda_dir}")
    # print(f"Dist directory: {dist_dir}")
    # print(f"Zip file will be created at: {zip_file}")

    if os.path.exists(zip_file):
        os.remove(zip_file)

    # go to the lambda directory, zip all its contents, then go up two directories, find the zip file destination directory and send our stuff there.
    subprocess.check_call(['zip', '-r', zip_file, '.'], cwd=lambda_dir)

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
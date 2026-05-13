import boto3
import os
import duckdb


ddb = duckdb.connect()
ddb.sql("CREATE OR REPLACE TABLE datasets (name VARCHAR, eml_content JSON);")


def duckdb_connect():
	return ddb

def create_s3_res():
	return boto3.client(
	    service_name='s3',
	    aws_access_key_id=os.getenv('S3_ACCESS_ID'),
	    aws_secret_access_key=os.getenv('S3_ACCESS_SECRET'),
	    endpoint_url=os.getenv('S3_ENDPOINT_URL'),
	    use_ssl=True,
	)


def list_eml_files_in_bucket(target_name, extension):
	s3_client = create_s3_res()
	bucket = os.getenv('S3_BUCKET_NAME')
	folders = set()
	continuation_token = None

	try:
		while True:
			params = {'Bucket': bucket}
			if continuation_token:
				params['ContinuationToken'] = continuation_token

			response = s3_client.list_objects_v2(**params)

			for obj in response.get('Contents', []):
				key = obj['Key']
				file_name = os.path.basename(key)
				name, ext = os.path.splitext(file_name)

				if name == target_name and ext.lower() == extension.lower():
					folders.add(os.path.dirname(key))

			if not response.get('IsTruncated'):
				break

			continuation_token = response.get('NextContinuationToken')
	except Exception as exc:
		print(f'There was an error listing files in S3: {exc}')
		return False

	if not folders:
		print('No matching files found in S3.')
		return []

	return sorted(folders)

def read_eml_from_s3(folder, ddb):
	s3_client = create_s3_res()
	bucket = os.getenv('S3_BUCKET_NAME')
	key = f"{folder}/eml.json"
	try:
		print(f"Reading from S3: bucket={bucket}, key={key}")
		response = s3_client.get_object(Bucket=bucket, Key=key)
		content = response['Body'].read().decode('utf-8')
		resp = ddb.sql("INSERT INTO datasets VALUES (?, ?);", params=(folder, content))
		print(f"Inserted into DuckDB: {resp.rowcount} row(s) affected.")
		return content
	except Exception as exc:
		print(f'There was an error reading the file from S3: {exc}')
		return None

def s3_to_duckdb(target_name, extension, ddb=ddb):
    try:
        folders = list_eml_files_in_bucket(target_name, extension)
        for folder in folders:
            print(f"Processing folder: {folder}")
            read_eml_from_s3(folder, ddb)
        return True
    except Exception as exc:
        print(f'There was an error processing the S3 data: {exc}')
        return False

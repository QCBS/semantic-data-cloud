import json
import os
#
import boto3
import duckdb


ddb = duckdb.connect()
ddb.sql("""
CREATE OR REPLACE TABLE datasets (
    name VARCHAR,
    eml_content JSON,
    min_lon DOUBLE,
    min_lat DOUBLE,
    max_lon DOUBLE,
    max_lat DOUBLE
);
""")


def duckdb_connect():
	return ddb

def create_s3_res():
	return boto3.client(
	    service_name='s3',
	    aws_access_key_id=os.getenv("S3_ACCESS_ID"),
	    aws_secret_access_key=os.getenv("S3_ACCESS_SECRET"),
	    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
	    use_ssl=True,
	)


def list_eml_files_in_bucket(target_name, extension):
	s3_client = create_s3_res()
	bucket = os.getenv("S3_BUCKET_NAME")
	datasets = dict()
	continuation_token = None

	try:
		while True:
			params = {"Bucket": bucket, "Prefix": "datasets/"}
			if continuation_token:
				params["ContinuationToken"] = continuation_token

			response = s3_client.list_objects_v2(**params)

			for obj in response.get("Contents", []):
				key = obj["Key"]
				file_name = os.path.basename(key)
				name, ext = os.path.splitext(file_name)
				dataset_name = os.path.dirname(key)
				if dataset_name not in datasets:
					datasets[dataset_name] = {"name": dataset_name.replace("datasets/", ""), "folder": None, "assets": dict()}
				if name == target_name and ext.lower() == extension.lower():
					datasets[dataset_name]["folder"] = dataset_name
				if ext.lower() == ".parquet":
					datasets[dataset_name]["assets"][file_name] = create_asset(dataset_name, file_name)

			if not response.get("IsTruncated"):
				break

			continuation_token = response.get("NextContinuationToken")
	except Exception as exc:
		print(f"There was an error listing files in S3: {exc}")
		return False

	if not datasets:
		print('No matching files found in S3.')
		return []

	return datasets

def create_asset(folder, file_name):
	href = f"{os.getenv("OBJECT_STORE_BASE_URL")}/{folder}/{file_name}"
	return {
		"href": f"{href}",
		"mimetype": "application/vnd.apache.parquet",
	}

def read_eml_from_s3(dataset, ddb):
	s3_client = create_s3_res()
	bucket = os.getenv("S3_BUCKET_NAME")
	key = f"{dataset["folder"]}/eml.json"
	try:
		print(f"Reading from S3: bucket={bucket}, key={key}")
		response = s3_client.get_object(Bucket=bucket, Key=key)
		content = json.loads(response["Body"].read().decode("utf-8"))
		if(len(dataset["assets"])>0):
			content["assets"] = list(dataset["assets"].values())
			species_list=[]
			if("occurrence.parquet" in dataset["assets"]):
				href = dataset["assets"]["occurrence.parquet"]["href"]
				content["recordedTaxa"] = species_from_occurrences(href)

		content["self"] = f"{os.getenv("API_BASE_URL")}/dataset/{dataset["name"]}"
		resp = ddb.sql("INSERT INTO datasets (name, eml_content) VALUES (?, ?);", params=[dataset["folder"].replace("datasets/", ""), json.dumps(content)])

		resp = ddb.sql("""
				UPDATE datasets
				SET
					min_lon = CAST(
						eml_content
							-> 'dataset'
							-> 'coverage'
							-> 'geographicCoverage'
							-> 'boundingCoordinates'
							->> 'westBoundingCoordinate'
					AS DOUBLE),

					max_lon = CAST(
						eml_content
							-> 'dataset'
							-> 'coverage'
							-> 'geographicCoverage'
							-> 'boundingCoordinates'
							->> 'eastBoundingCoordinate'
					AS DOUBLE),

					min_lat = CAST(
						eml_content
							-> 'dataset'
							-> 'coverage'
							-> 'geographicCoverage'
							-> 'boundingCoordinates'
							->> 'southBoundingCoordinate'
					AS DOUBLE),

					max_lat = CAST(
						eml_content
							-> 'dataset'
							-> 'coverage'
							-> 'geographicCoverage'
							-> 'boundingCoordinates'
							->> 'northBoundingCoordinate'
					AS DOUBLE);""")

		print(f"Inserted into DuckDB: {resp.rowcount} row(s) affected.")
		return content
	except Exception as exc:
		print(f"There was an error reading the file from S3: {exc}")
		return None

def s3_to_duckdb(target_name, extension, ddb=ddb):
	try:
		datasets = list_eml_files_in_bucket(target_name, extension)
		if not isinstance(datasets, dict):
			return False
		for dataset in datasets.values():
			read_eml_from_s3(dataset, ddb)
		return True
	except Exception as exc:
		print(f"There was an error processing the S3 data: {exc}")
		return False


def species_from_occurrences(href):
	species_list = ddb.sql("SELECT DISTINCT scientific_name from read_parquet(?);", params=[href])	
	return [row[0] for row in species_list.fetchall() if row[0] is not None]
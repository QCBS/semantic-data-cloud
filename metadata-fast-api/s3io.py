import json
import os
from concurrent.futures import as_completed, ThreadPoolExecutor
from pathlib import Path
from threading import Lock
#
import boto3
import duckdb


METADATA_DB_PATH = Path("/data/metadatadb.duckdb")
METADATA_API_PORT = os.getenv("METADATA_API_PORT")


def duckdb_connect():
    ddb = duckdb.connect(str(METADATA_DB_PATH))
    ddb.sql("""
    CREATE OR REPLACE TABLE datasets (
        name VARCHAR,
        eml_content JSON,
        min_lon DOUBLE,
        min_lat DOUBLE,
        max_lon DOUBLE,
        max_lat DOUBLE,
        begin_date DATE,
        end_date DATE,
        license_id VARCHAR,
        dataset_citation VARCHAR
    );
    """)
    return ddb


def create_s3_res():
    return boto3.client(
        service_name="s3",
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
            params = {
                "Bucket": bucket,
                "Prefix": "datasets/",
            }
            if continuation_token:
                params["ContinuationToken"] = continuation_token

            response = s3_client.list_objects_v2(**params)

            for obj in response.get("Contents", []):
                key = obj["Key"]
                file_name = os.path.basename(key)
                name, ext = os.path.splitext(file_name)
                dataset_name = os.path.dirname(key)
                if dataset_name not in datasets:
                    datasets[dataset_name] = {
                        "name": dataset_name.replace("datasets/", ""),
                        "folder": None,
                        "assets": dict(),
                    }
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
        print("No matching files found in S3.")
        return []

    return datasets


def create_asset(folder, file_name):
    href = f"{os.getenv('OBJECT_STORE_BASE_URL')}/{folder}/{file_name}"
    return {
        "href": f"{href}",
        "mimetype": "application/vnd.apache.parquet",
    }


def _fetch_eml_from_s3(dataset) -> tuple[dict, dict] | None:
    s3_client = create_s3_res()

    bucket = os.getenv("S3_BUCKET_NAME")
    key = f"{dataset['folder']}/eml.json"

    try:
        print(f"Reading from S3: bucket={bucket}, key={key}")
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = json.loads(response["Body"].read().decode("utf-8"))
        return dataset, content

    except Exception as exc:
        print(f"S3 file reading error for {dataset['name']}: {exc}")
        return None


def _write_eml_to_duckdb(dataset, content, ddb):
    try:
        if len(dataset["assets"]) > 0:
            content["assets"] = list(dataset["assets"].values())
            # if "occurrence.parquet" in dataset["assets"]:
            #     href = dataset["assets"]["occurrence.parquet"]["href"]
            #     content["recordedTaxa"] = species_from_occurrences(href, ddb)

        content["self"] = f"http://localhost:{METADATA_API_PORT}/dataset/{dataset['name']}"

        ddb.execute(
            "INSERT INTO datasets (name, eml_content) VALUES (?, ?);",
            [dataset["folder"].replace("datasets/", ""), json.dumps(content)],
        )

    except Exception as exc:
        print(f"Database error for {dataset['name']}: {exc}")


def _materialize_derived_columns(ddb):
        ddb.execute("""
            WITH extracted_coords AS (
                SELECT
                    name,
                    eml_content,
                    eml_content -> 'dataset' -> 'coverage' -> 'geographicCoverage' -> 'boundingCoordinates' AS bbox
                FROM datasets
            )

            UPDATE datasets
            SET
                min_lon = CAST(bbox ->> 'westBoundingCoordinate' AS DOUBLE),
                min_lat = CAST(bbox ->> 'southBoundingCoordinate' AS DOUBLE),
                max_lon = CAST(bbox ->> 'eastBoundingCoordinate' AS DOUBLE),
                max_lat = CAST(bbox ->> 'northBoundingCoordinate' AS DOUBLE)
            FROM extracted_coords
            WHERE datasets.name = extracted_coords.name;
        """)

        ddb.execute("""
            WITH exploded_temporal AS (
                SELECT
                    datasets.name,
                    CAST(
                        COALESCE(
                            je.value -> 'rangeOfDates' -> 'beginDate' ->> 'calendarDate',
                            je.value -> 'singleDateTime' ->> 'calendarDate'
                        ) AS DATE
                    ) AS start_date,
                    CAST(
                        COALESCE(
                            je.value -> 'rangeOfDates' -> 'endDate' ->> 'calendarDate',
                            je.value -> 'singleDateTime' ->> 'calendarDate'
                        ) AS DATE
                    ) AS end_date
                FROM datasets,
                json_each(
                    CASE
                        WHEN json_type(datasets.eml_content -> 'dataset' -> 'coverage' -> 'temporalCoverage') = 'ARRAY'
                            THEN datasets.eml_content -> 'dataset' -> 'coverage' -> 'temporalCoverage'
                        ELSE json_array(datasets.eml_content -> 'dataset' -> 'coverage' -> 'temporalCoverage')
                    END
                ) AS je
            ),

            aggregated AS (
                SELECT
                    name,
                    MIN(start_date) AS begin_date,
                    MAX(end_date) AS end_date
                FROM exploded_temporal
                GROUP BY name
            )

            UPDATE datasets
            SET
                begin_date = aggregated.begin_date,
                end_date = aggregated.end_date
            FROM aggregated
            WHERE datasets.name = aggregated.name;
        """)

        ddb.execute("""
            WITH extracted_license AS (
                SELECT
                    name,
                    eml_content,
                    eml_content -> 'dataset' -> 'licensed' ->> 'identifier' AS license_id
                FROM datasets
            )

            UPDATE datasets
            SET
                license_id = extracted_license.license_id
            FROM extracted_license
            WHERE datasets.name = extracted_license.name;
        """)

        ddb.execute("""
            WITH extracted_citation AS (
                SELECT
                    name,
                    eml_content,
                    CASE
                        WHEN json_type(eml_content -> 'additionalMetadata' -> 'metadata' -> 'gbif' -> 'citation') = 'OBJECT'
                            THEN eml_content -> 'additionalMetadata' -> 'metadata' -> 'gbif' -> 'citation' ->> 'citation'
                        ELSE eml_content -> 'additionalMetadata' -> 'metadata' -> 'gbif' ->> 'citation'
                    END AS dataset_citation
                FROM datasets
            )

            UPDATE datasets
            SET
                dataset_citation = extracted_citation.dataset_citation
            FROM extracted_citation
            WHERE datasets.name = extracted_citation.name;
        """)


def s3_to_duckdb(target_name, extension, ddb, max_workers=20):
    try:
        datasets = list_eml_files_in_bucket(target_name, extension)

        if not isinstance(datasets, dict):
            raise RuntimeError("No datasets found in S3")

        db_lock = Lock()

        def fetch_and_insert(dataset):
            result = _fetch_eml_from_s3(dataset)

            if result is None:
                return

            dataset, content = result

            with db_lock:
                _write_eml_to_duckdb(dataset, content, ddb)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(fetch_and_insert, dataset): dataset
                for dataset in datasets.values()
            }

            for future in as_completed(futures):
                exc = future.exception()
                if exc:
                    dataset = futures[future]
                    print(f"Error processing dataset {dataset['name']}: {exc}")

        with db_lock:
            _materialize_derived_columns(ddb)

    except Exception as exc:
        print(f"There was an error processing the S3 data: {exc}")


def species_from_occurrences(href, ddb):
    try:
        species_list = ddb.execute(
            "SELECT DISTINCT scientific_name FROM read_parquet(?);",
            [href],
        )
        return [row[0] for row in species_list.fetchall() if row[0] is not None]

    except Exception:
        return []
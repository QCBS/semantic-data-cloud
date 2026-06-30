# Starter guide

This guide walks through the steps required to prepare and host a Darwin Core Data Package for use with the Semantic Data Cloud. There are four main stages:
  1. Converting EML metadata from XML to JSON-LD.
  2. Converting tabular data to Parquet.
  3. Uploading the resulting files to object storage.
  4. Setting an environmental variables file.

---

## Converting EML XML files to JSON-LD

The convention for Ecological Metadata Language ([EML](https://eml.ecoinformatics.org/)) is eXtensible Markup Language ([XML](https://www.w3.org/TR/xml/)). However, despite being highly structured, XML is verbose and less convenient for modern web APIs and database-backed applications than JSON. Therefore, JSON, and more specifically [JSON-LD](https://www.w3.org/TR/json-ld11/), would represent a better serialization of EML (see also [Boettiger (2019)](https://joss.theoj.org/papers/10.21105/joss.01276)). The application considers EML metadata as JSON-LD, using the `.json` extension.

The conversion can be performed quickly using the R packages [EML](https://docs.ropensci.org/EML/) for reading `.xml` files and [jsonlite](https://jeroen.r-universe.dev/jsonlite) for serialising them to `.json` as:

```r
library(EML)
library(jsonlite)

eml_list <- read_eml("eml.xml")
eml_json <- toJSON(eml_list, auto_unbox = TRUE, pretty = TRUE)
write(eml_json, "eml.json")
```

**Note:** The `auto_unbox = TRUE` argument is important, as it ensures that length-1 vectors are converted to JSON strings and numbers instead of arrays.

Here are a few points to watch out for regarding the obtained JSON representation of EML metadata:
  1. There may be some artefacts from XML [entity encoding](https://www.w3.org/TR/xml/#syntax), where special characters such as `&` or `<` are represented by their entity references `&amp;` or `&lt;`.
  2. Depending on how the text was present in the XML document, whitespace escape sequences (e.g. `\n`, `\t`, etc.) might be present.
  3. Some values that are to be semantically interpreted as numeric in the original XML may be represented as character strings in the parsed object (e.g. `"-74.0684"` instead of `-74.0684`) due to type handling in the parsing and serialization process.
  
These may require manual editing of the file. However, any such edits must ensure the output remains valid JSON, as defined in [RFC 8259](https://datatracker.ietf.org/doc/html/rfc8259).

### Required fields

Three fields are required for the application to correctly index a dataset:
  1. **Bounding box**: The `boundingCoordinates` field within `geographicCoverage` must be an object containing four decimal values representing the spatial extent of the dataset, as per [EML standards](https://eml.ecoinformatics.org/schema/eml-coverage_xsd#Coverage_geographicCoverage). The application also allows for strings of decimal values, since the metadata catalog database will attempt to cast the values into the `DOUBLE` datatype.
  2. **Temporal coverage**: The dates within the in the `temporalCoverage` element  can either be a `rangeOfDates` object or a `singleDateTime` object, as per [EML standards](https://eml.ecoinformatics.org/schema/eml-coverage_xsd#Coverage_temporalCoverage). The values in the `calendarDate` leaf elements must be strings of valid ISO 8601 date strings representing the considered dates. The application also supports cases where `temporalCoverage` is an array of `rangeOfDates` objects, though this is not strictly part of the EML standard.
  3. **License**: The `licensed` element must contain the licensing rights for the dataset as specified by [EML standards](https://eml.ecoinformatics.org/schema/eml-resource_xsd#ResourceGroup_licensed). In particular, the `identifier` leaf element must be present and must be a valid [SPDX license identifier](https://spdx.org/licenses/).

### Citation and provenance

As specified by EML standards, additional metadata can be supplied via the [`additionalMetadata`](https://eml.ecoinformatics.org/schema/eml_xsd#eml_additionalMetadata)'s [`metadata`](https://eml.ecoinformatics.org/schema/eml_xsd.html#eml_eml_additionalMetadata_metadata) element.

When dealing with Darwin Core Data Packages, the application extracts the `citation` element from the `gbif` element within `additionalMetadata`. The `citation` element may be either a plain string or an object with a `citation` field and an accompanying `identifier` field. These provide the application with the definitive source representation of the dataset, which is used for attribution in generated citation files.

---

## Converting tables to Parquet

Apache [Parquet](https://github.com/apache/parquet-format) is a columnar file format well suited to biodiversity datasets: once published, the data is read-only, and users often query only a small subset of the available columns. Parquet's columnar layout allows DuckDB to read only the relevant columns directly from object storage, without downloading entire files.

### Column naming convention

Before converting, ensure all column names follow `snake_case`. The application uses a strict `snake_case` naming convention for all column names in Parquet files to maximise portability across operating systems and database systems. For example, the field corresponding to [dwc:scientificName](https://dwc.tdwg.org/list/#dwc_scientificName) must be named `scientific_name`, not `scientificName`.

Here are a few points to be careful when converting to Parquet:
  1. Despite the `.csv` extension, Darwin Core table files are tab-separated (`.tsv`) files. Make sure to set the delimiter accordingly.
  2. Some level of column separation should be done prior to conversion to Parquet. This means that the `occurrence.csv` considered here is not the same as `occurrence.csv` in Darwin Core Archives (which is usually a combination of properties associated with occurrence, events and locations). In the `occurrence.csv` considered here, only fields [considered in the Darwin Core Data Package schema for occurrence](https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas/occurrence.json) are considered.
  3. Be mindful that some properties need additional attention, such as those that begin with numbers (e.g. `mixs:0000066` should be named `_16s_recover_software`), those that begin with capital letters (e.g. `photoshop:Credit` should be named `credit`) or that have numbers within them (e.g. `ggbn:ratioOfAbsorbance260_280` should be named `ratio_of_absorbance_260_280`).

The regular expression in the code below should take care of most cases. Please validate results, column names and data types, before uploading them to S3. If you are unsure about a property's name, you can look for it in the [dwcowl.obda](/ontop/mappings/dwcowl.obda) file and look up its mapping.

### Using PyArrow

[PyArrow](https://arrow.apache.org/docs/python/index.html) provides direct, dependency-light conversion from `.csv` or `.tsv` files to Parquet. This is the recommended approach for large files.

```python
import re
#
import pyarrow.csv as pv
import pyarrow.parquet as pq

def camel_to_snake(name):
    camel_name = re.sub(pattern=r"([A-Z]+)([A-Z][a-z])", repl=r"\1_\2", string=name)
    return re.sub(pattern=r"([a-z\d])([A-Z])", repl=r"\1_\2", string=camel_name).lower()

parse_options = pv.ParseOptions(delimiter="\t")
table = pv.read_csv("occurrence.csv", parse_options=parse_options)

snake_names = [camel_to_snake(col) for col in table.column_names]
table = table.rename_columns(snake_names)

pq.write_table(table, "occurrence.parquet")
```

### Using pandas

If you are already working with [pandas](https://pandas.pydata.org/), the [`to_paquet()`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html#pandas.DataFrame.to_parquet) method offers a familiar alternative. Note that `pyarrow` must still be installed, as it is used as the Parquet backend.

```python
import re
#
import pandas as pd

def camel_to_snake(name):
    camel_name = re.sub(pattern=r"([A-Z]+)([A-Z][a-z])", repl=r"\1_\2", string=name)
    return re.sub(pattern=r"([a-z\d])([A-Z])", repl=r"\1_\2", string=camel_name).lower()

df = pd.read_csv("occurrence.csv", sep="\t")
df.columns = [camel_to_snake(col) for col in df.columns]
df.to_parquet("occurrence.parquet", index=False)
```

**Note:** The `index=False` argument is important, as it prevents pandas from writing its internal row index as an extra column in the Parquet file.

---

## Uploading files to your bucket

Datasets are stored in object storage as directory-like prefixes, where each dataset is represented as a self-contained Darwin Core Data Package in exploded Parquet form. The expected layout is as follows:

```
datasets/
├── dataset_a/
│   ├── eml.json
│   ├── event.parquet
│   ├── identification.parquet
│   ├── occurrence.parquet
│   └── occurrence-assertion.parquet
├── dataset_b/
│   ├── eml.json
│   ├── event.parquet
│   └── material.parquet
└── dataset_c/
    ├── eml.json
    ├── event.parquet
    ├── event-assertion.parquet
    └── occurrence.parquet
```

Each top-level directory under `datasets/` represents a single dataset. It must contain the `eml.json` metadata file alongside all converted `.parquet` table files.

When uploading files, set the canned Access Control List (ACL) to [`public-read`](https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html). This is required for DuckDB to have `READ` access and be able to query the files directly from object storage.

### Using Boto3

[Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) is the AWS SDK for Python and works with any S3-compatible object storage service. The following example uploads all files for a single dataset:

```python
import os
from pathlib import Path
#
import boto3

s3_client = boto3.client(
    service_name="s3",
	  aws_access_key_id=os.getenv("S3_ACCESS_ID"),
	  aws_secret_access_key=os.getenv("S3_ACCESS_SECRET"),
	  endpoint_url=os.getenv("S3_ENDPOINT_URL"),
	  use_ssl=True,
)

bucket = os.getenv("S3_BUCKET_NAME")
dataset_name = "dataset_a"
local_dir = Path("dataset_a")

for file in local_dir.iterdir():
    key = f"datasets/{dataset_name}/{file.name}"
    s3_client.upload_file(
        str(file),
        bucket,
        key,
        ExtraArgs={"ACL": "public-read"},
    )
```

### Using s5cmd

[s5cmd](https://github.com/peak/s5cmd) is a fast, parallel command-line tool for S3-compatible object storage. It is well-suited to uploading entire dataset directories efficiently:

```bash
s5cmd --endpoint-url https://your-object-storage-endpoint \
  cp --acl public-read \
  ./dataset_a/* \
  s3://your_bucket_name/datasets/dataset_a/
```

To upload multiple datasets at once:

```bash
s5cmd --endpoint-url https://your-object-storage-endpoint \
  cp --acl public-read \
  ./datasets/* \
  s3://your_bucket_name/datasets/
```

**Note:** s5cmd uses the official AWS SDK to access S3, which requires credentials to sign requests to AWS. Consequntly, make sure that [your credentials are available to the application](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

---

## Setting up an environment variables file

Create a `.env` file in the project root with the following variables:

```env
OBJECT_STORE_BASE_URL=https://your-public-object-url-base
S3_ACCESS_ID=your_access_key_id
S3_ACCESS_SECRET=your_secret_access_key
S3_BUCKET_NAME=your_bucket_name
S3_ENDPOINT_URL=https://your-object-storage-endpoint
```

Between these variables, `S3_ENDPOINT_URL` is the private endpoint used for authenticated operations such as uploads, while `OBJECT_STORE_BASE_URL` is the public-facing base URL through which DuckDB reads stored objects. These two values may differ depending on your storage provider.
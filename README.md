``` text
███████╗██╗  ██╗ ██████╗███████╗██╗     ██████╗      ██╗███████╗ ██████╗ ███╗   ██╗
██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║     ╚════██╗     ██║██╔════╝██╔═══██╗████╗  ██║
█████╗   ╚███╔╝ ██║     █████╗  ██║      █████╔╝     ██║███████╗██║   ██║██╔██╗ ██║
██╔══╝   ██╔██╗ ██║     ██╔══╝  ██║     ██╔═══╝ ██   ██║╚════██║██║   ██║██║╚██╗██║
███████╗██╔╝ ██╗╚██████╗███████╗███████╗███████╗╚█████╔╝███████║╚██████╔╝██║ ╚████║
╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝╚══════╝ ╚════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
```

# MET-Cleaner
Repo for the metadata excel table clean-up and parsing script

## `Excel2Json.py`

This document contains the ExportJson class which can be used to convert a DRE standard metadata Excel sheet to a JSON list.
The example shows how to perform document export (see also [the example script](example_insert.py)):

``` python
from Excel2Json import ExportJson
from pymongo import MongoClient

file_path = "data.xlsx"
client = MongoClient("mongodb://root:example@mongo/?authMechanism=DEFAULT")

data = ExportJson(
    file=file_path, project_id="aaa", dspace_id="01", mongo_client=client
).run()
```


Here, the *project_id* is the three letter ID allocated to each project and *dspace_id* is two digit number allocated to projects/files based on where the raw data associated to the file is stored (in the case where the metadata has not associated raw data file the value '99' is allocated by default).

For data uploads on to MongoDB, please the following steps after generating the data variable,

``` python
from datetime import datetime

# setup and processing as above

collection = client['name-of-db']['name-of-collection']

for doc in data:
    doc['createdAt'] = datetime.now()
    doc['updatedAt'] = datetime.now()
    doc['updatedBy'] = "your-initails"
    collection.insert_one(doc)
```


## `ValueSync.py`

This document to can be used to update the `persons` and `institutions` collections in DRE MongoDB.

Follow the below directions to perform updates (also see [the example script](example_sync.py)):

**BE SURE TO CHECK CONSISTENCY & CORRECTNESS OF VALUES IN THE METADATA EXCEL SHEET BEFORE PERFORMING THE UPDATES.**

``` python
from pymongo import MongoClient
# import the library
from ValueSync import ValueList

client = MongoClient("mongodb://root:example@mongo/?authMechanism=DEFAULT")

# instantiate class; running example for "persons"-collection
persons = ValueList(
    auth_string=None,
    db_name="db_name",
    col_name="collection_name",
    dev_list="persons",
    client=client,
)

# get distinct values in collection
print("Persons in reference collection:")
print(persons.in_collection())

# get values missing in the MongoDB collection
print("Persons missing in dev collection:")
print(persons.check_missing())

# update collection with missing values
print(persons.synchronise())
```

## CLI wrapper: `cli.py`

This is a CLI wrapper for the "insert" and "sync" operations.

### `cli.py insert`

Run with `python cli.py insert --help` to get an overview for the required arguments.
This command will read the provided Excel file, and sync the data into the specified collection in MongoDB.
The `--dry-run`-flag can be used to test things out, it will not perform any insertion.

#### Example

``` shell
$ python cli.py insert \
    --connection mongodb://root:example@mongo \
    --target projects_metadata_ubt_TEST.sample_project \
    -project-id aaa \
    -dspace-id 01 \
    --dry-run \
    sample.xlsx
```


### `cli.py sync`

Run with `python cli.py insert --help` to get an overview for the required arguments.
This command will read the provided Excel file, and sync the data into the specified collection in MongoDB.
The `--dry-run`-flag can be used to test things out, it will not perform any insertion.

#### Example

``` shell
$ python cli.py sync \
    --connection mongodb://root:example@mongo \
    --from projects_metadata_ubt_TEST.sample_project \
    --target persons \
    --dry-run
```

# LoC Subject Headings

The subjects provided in the Excel sheet are indexed against the LoC subject headings.
The first result for which the `aLabel`-field matches the search term is used; comparison is done on the lower-cased strings.
If none of the results' `aLabel`s match, the original label is retained.

The API is used in `leftanchord`-mode, as opposed to `keyword`-mode (see [the LoC API docs](https://id.loc.gov/techcenter/searching.html)).

The schema for `subject` is documented below in [subject](#subject)

# MongoDB schema

An incomplete schema for documents inside the project-collection.

## `name`

The `name`-key stores names of associated persons (or other actors, e.g., groups and institutions):

``` json-with-comments
{
"name": [                             // list of objects of the following shape
    {
        "name": {
            "label": string|null,     // contains the raw name, if present
            "qualifier": string|null  // an optional qualifier
        }
        "affl": Array<string>|null    // list of affiliations
    }
]
```

## `subject`

All subjects are stored in the following schema in the `subject`-field of the document:

``` json-with-comments
{
 "subject": [                   // list of objects of the following shape
    {
       "uri": string|NaN,       // the LoC URI for the subject heading
       "authority": string|NaN, // the authority URI
       "origLabel": string,     // the raw term, as provided in the data
       "authLabel": string|NaN  // the authoritative label
    }
 ]
}
```

Initially, all authority-dependent keys are set to `np.nan` (`NaN` in JSON).
If an authoritative label exists, the `NaN`-fields are updated accordingly.

## MET-Cleaner
Repo for the metadata excel table clean-up and parsing script

## Description
The following .py files serve the following functions:

- **Excel2Json.py**
This document contains the ExportJson class which can be used to convert a DRE standard metadata Excel sheet to a JSON list. The example shows how to perform document export:

``` python
from Excel2Json import ExportJson
file_path = r"path-to-your-file"
data = ExportJson(file=file_path, project_id='aaa', dspace_id='01').run()
```


Here, the *project_id* is the three letter ID allocated to each project and *dspace_id* is two digit number allocated to projects/files based on where the raw data associated to the file is stored (in the case where the metadata has not associated raw data file the value '99' is allocated by default).

For data uploads on to MongoDB, please the following steps after generating the data variable,

``` python
from pymongo import MongoClient
from datetime import datetime

client = MongoClient('your-personal-mongodb-connection-string')

collection = client['name-of-db']['name-of-collection']
for doc in data:
    doc['createdAt'] = datetime.now()
    doc['updatedAt'] = datetime.now()
    doc['updatedBy'] = "your-initails"
    collection.insert_one(doc)
```


- **ValueSync.py**
This document to can be used to update the *'persons'* and *'institutions'* collections in DRE MongoDB.

Follow the below directions to perform updates.    

**BE SURE TO CHECK CONSISTENCY & CORRECTNESS OF VALUES IN THE METADATA EXCEL SHEET BEFORE PERFORMING THE UPDATES.**

``` python
# import the library
from ValueSync import ValueList 

# instantiate class; running example for "persons"-collection
persons = ValueList(
    'your-personal-mongodb-connection-string',
    'db_name',
    'collection_name',
    'persons'
)

# get distinct values in collection
persons.in_collection()

# get values missing in the MongoDB collection
persons.check_missing()

# update collection with missing values
persons.synchronise()
```

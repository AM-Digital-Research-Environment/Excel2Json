## MET-Cleaner
Repo for the metadata excel table clean-up and parsing script

## Description
The following .py files serve the following functions:

- **Excel2Json.py**  
This document contains ExportJson class which can be used to convert DRE standard metadata Excel sheet to a json list. The example is shows how perform document export:
>*from Excel2Json import ExportJson*
> 
> *file_path = r"path-to-your-file"*  
> *data = ExportJson(file_path=file_path, project_id='aaa', dspace_id='01')*

Here, the *project_id* is the three letter ID allocated to each project and *dspace_id* is two digit number allocated to projects/files based on where the raw data associated to the file is stored (in the case where the metadate has not associated raw data file the value '99' is allocated by default).

For data uploads on to MongoDB, please the following steps after generating the data variable,

>*from pymongo import MongoClient*
>  
>*client = MongoClient('your-personal-mongodb-connection-string')*  
>*collection = client['name-of-db']['name-of-collection']*  
>
>*for doc in data:*   
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*doc['createdAt'] = datetime.now()*  
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*doc['updatedAt'] = datetime.now()*  
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*doc['updatedBy'] = "your-initails"*  
>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*collection.insert_one(doc)*  

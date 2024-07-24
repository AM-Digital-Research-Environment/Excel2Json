from pymongo import MongoClient
from datetime import datetime
from Excel2Json import ExportJson

file_path = "./examples/sample.xls"
client = MongoClient("mongodb://root:example@mongo/?authMechanism=DEFAULT")

data = ExportJson(file=file_path, project_id="aaa", dspace_id="01", mongo_client=client).run()


collection = client["foo"]["bar"]
for doc in data:
    doc["createdAt"] = datetime.now()
    doc["updatedAt"] = datetime.now()
    doc["updatedBy"] = "OB"
    collection.insert_one(doc)

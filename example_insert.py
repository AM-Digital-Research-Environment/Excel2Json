from datetime import datetime

from Excel2Json import ExportJson
from pymongo import MongoClient

file_path = "./examples/sample.xlsx"
client = MongoClient("mongodb://root:example@mongo/?authMechanism=DEFAULT")

data = ExportJson(
    file=file_path, project_id="aaa", dspace_id="01", mongo_client=client
).run()


collection = client["projects_metadata_ubt_TEST"]["sample_project"]
for doc in data:
    doc["createdAt"] = datetime.now()
    doc["updatedAt"] = datetime.now()
    doc["updatedBy"] = "JaneDoe"
    collection.insert_one(doc)

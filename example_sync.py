from pymongo import MongoClient
from ValueSync import ValueList

client = MongoClient("mongodb://root:example@mongo/?authMechanism=DEFAULT")

# instantiate class; running example for "persons"-collection
persons = ValueList(
    auth_string=None,
    db_name="projects_metadata_ubt_TEST",
    col_name="sample_project",
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

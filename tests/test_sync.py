import mongomock
import pymongo
import pytest
import pytest_schema

from Excel2Json import ValueSync


class TestPersonHandling(object):
    def test_persons_are_transformed(self):
        cases = [
            {
                "desc": "Institution, no affiliation",
                "in": [
                    {
                        "name": {"label": "ACME Corp.", "qualifier": "institution"},
                        "affl": [],
                    }
                ],
                "out": [],
            },
            {
                "desc": "Group, no affiliation",
                "in": [
                    {
                        "name": {"label": "Giga Group", "qualifier": "group"},
                        "affl": [],
                    }
                ],
                "out": [],
            },
            {
                "desc": "Institution, single affiliation",
                "in": [
                    {
                        "name": {"label": "ACME Corp.", "qualifier": "institution"},
                        "affl": ["IEEE"],
                    }
                ],
                "out": [],
            },
            {
                "desc": "Group, multiple affiliations",
                "in": [
                    {
                        "name": {"label": "Giga Group", "qualifier": "group"},
                        "affl": ["IEEE", "FooBar"],
                    }
                ],
                "out": [],
            },
            {
                "desc": "Single person, no affiliation",
                "in": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": [],
                    }
                ],
                "out": [{"name": "Doe, Jane", "affiliation": []}],
            },
            {
                "desc": "Single person, single affiliation",
                "in": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["IEEE"],
                    }
                ],
                "out": [{"name": "Doe, Jane", "affiliation": ["IEEE"]}],
            },
            {
                "desc": "Multiple distinct persons, mixed affiliations",
                "in": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["IEEE"],
                    },
                    {
                        "name": {"label": "Doe, John", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                    },
                    {
                        "name": {"label": "Test, Tina", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                    },
                ],
                "out": [
                    {"name": "Doe, Jane", "affiliation": ["IEEE"]},
                    {"name": "Doe, John", "affiliation": ["ACME Corp."]},
                    {"name": "Test, Tina", "affiliation": ["ACME Corp."]},
                ],
            },
            {
                "desc": "Multiple same persons with differing affiliations",
                "in": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["IEEE"],
                    },
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                    },
                    {
                        "name": {"label": "Test, Tina", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                    },
                ],
                "out": [
                    {"name": "Doe, Jane", "affiliation": ["IEEE", "ACME Corp."]},
                    {"name": "Test, Tina", "affiliation": ["ACME Corp."]},
                ],
            },
        ]

        for c in cases:
            want = c["out"]
            have = ValueSync.ValueList.handle_persons(c["in"])

            for w in want:
                w["affiliation"] = sorted(w["affiliation"])
            for h in have:
                h["affiliation"] = sorted(h["affiliation"])

            assert want == have, f"Failed: {c['desc']}"


class TestValuelist(object):
    @mongomock.patch(servers=(("test.com", 27017),))
    def test_it_can_be_initialized_with_an_authString(self):
        with pytest.deprecated_call():
            vl = ValueSync.ValueList(
                "mongodb://test.com:27017",
                "testDatabase",
                "testCollection",
                "testlist",
            )
        assert isinstance(vl, ValueSync.ValueList)

    def test_it_can_be_initialized_with_a_preconfigured_client(self):
        vl = ValueSync.ValueList(
            None, "testDatabase", "testCollection", "testlist", mongomock.MongoClient()
        )
        assert isinstance(vl, ValueSync.ValueList)

    def test_it_cant_be_initialized_with_an_authString_and_a_client(self):
        with pytest.raises(ValueError):
            _ = ValueSync.ValueList(
                "mongodb://test.com:27017",
                "testDatabase",
                "testCollection",
                "testlist",
                mongomock.MongoClient(),
            )

    def test_it_cant_be_initialized_without_authstring_and_client(self):
        with pytest.raises(ValueError):
            _ = ValueSync.ValueList(
                None, "testDatabase", "testCollection", "testlist", None
            )


class TestCollectionChecks(object):
    @mongomock.patch(servers=(("test.com", 27017),))
    def test_collection_check_returns_no_results_when_project_collection_is_empty(self):
        syncer = ValueSync.ValueList(
            None,
            "testDatabase",
            "testProject",
            "persons",
            pymongo.MongoClient("test.com:27017"),
        )

        results = syncer.in_collection()
        assert len(results) == 0

    def test_collection_check_returns_only_items_qualified_with_PERSON(self):
        client = mongomock.MongoClient("test.com:27017")
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "ACME Group", "qualifier": "group"},
                        "affl": [],
                        "role": "Tester",
                    }
                ]
            },
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": [],
                        "role": "Tester",
                    },
                    {
                        "name": {"label": "Doe, John", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        results = syncer.in_collection()

        assert len(results) == 2

        # sort for deterministic retrieval
        results = sorted(results, key=lambda x: x["name"])

        assert results[0]["name"] == "Doe, Jane"
        assert results[0]["affiliation"] == []
        assert results[1]["name"] == "Doe, John"
        assert results[1]["affiliation"] == ["ACME Corp."]


class TestMissingChecks(object):
    def test_empty_dev_collection_and_empty_project_return_no_missing_items(self):
        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", mongomock.MongoClient()
        )

        results = syncer.check_missing()
        assert len(results) == 0

    def test_empty_dev_collection_returns_all_new_items_as_missing(self):
        client = mongomock.MongoClient()
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "ACME Group", "qualifier": "group"},
                        "affl": [],
                        "role": "Tester",
                    }
                ]
            },
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": [],
                        "role": "Tester",
                    },
                    {
                        "name": {"label": "Doe, John", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        results = syncer.check_missing()

        assert len(results) == 2

        # sort for deterministic retrieval
        results = sorted(results, key=lambda x: x["name"])

        assert results[0]["name"] == "Doe, Jane"
        assert results[0]["affiliation"] == []
        assert results[1]["name"] == "Doe, John"
        assert results[1]["affiliation"] == ["ACME Corp."]

    def test_primed_dev_collection_returns_only_new_items_as_missing(self):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": {
                    "name": "Doe, Jane",
                    "affiliation": [],
                }
            },
            {
                "name": {
                    "name": "Doe, John",
                    "affiliation": ["ACME Corp."],
                }
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection with an overlap with persons
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": [],
                        "role": "Tester",
                    },
                    {
                        "name": {"label": "Doe, John", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                        "role": "Tester",
                    },
                ]
            },
            {
                "name": [
                    {
                        "name": {"label": "Test, Test", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        results = syncer.check_missing()

        assert len(results) == 1

        # sort for deterministic retrieval
        results = sorted(results, key=lambda x: x["name"])

        assert results[0]["name"] == "Test, Test"
        assert results[0]["affiliation"] == ["Giga Group"]

    def test_an_existing_person_with_a_new_affiliation_is_marked_as_missing(self):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": {
                    "name": "Doe, Jane",
                    "affiliation": ["ACME Corp."],
                }
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection with an overlap with persons
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        results = syncer.check_missing()

        assert len(results) == 1

        # sort for deterministic retrieval
        results = sorted(results, key=lambda x: x["name"])

        assert results[0]["name"] == "Doe, Jane"
        assert results[0]["affiliation"] == ["Giga Group"]


class TestSynchronisation(object):
    def test_no_missing_entities_return_early(self, capfd):
        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", mongomock.MongoClient()
        )

        # call synchronise() without priming MongoDB
        result = syncer.synchronise()
        captured = capfd.readouterr()
        assert result
        assert "No documents found to insert" in captured.out

    def test_person_schema_in_dev_collection(self):
        client = mongomock.MongoClient()

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        person_result_schema = {
            "_id": mongomock.ObjectId,
            "name": str,
            "affiliation": list,
        }

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())

        assert len(dev_collection) == 1
        assert pytest_schema.exact_schema(person_result_schema) == dev_collection[0]

    def test_missing_person_is_inserted_into_empty_dev_collection(self):
        client = mongomock.MongoClient()

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())
        assert len(dev_collection) == 1
        for item in dev_collection:
            assert item["name"] == "Doe, Jane"
            assert item["affiliation"] == ["Giga Group"]

    def test_missing_person_is_inserted_into_primed_dev_collection(self):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": "Doe, Jane",
                "affiliation": ["ACME Corp."],
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, John", "qualifier": "person"},
                        "affl": [],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())
        # sort for deterministic retrieval
        dev_collection = sorted(dev_collection, key=lambda x: x["name"])

        assert len(dev_collection) == 2

        assert dev_collection[0]["name"] == "Doe, Jane"
        assert dev_collection[0]["affiliation"] == ["ACME Corp."]
        assert dev_collection[1]["name"] == "Doe, John"
        assert dev_collection[1]["affiliation"] == []


class TestAffiliationMerge(object):
    def test_existing_person_is_updated_with_new_affiliations(self, capfd):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": "Doe, Jane",
                "affiliation": ["ACME Corp."],
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())

        captured = capfd.readouterr()
        assert "Existing person found" in captured.out

        assert len(dev_collection) == 1

        assert dev_collection[0]["name"] == "Doe, Jane"
        assert sorted(dev_collection[0]["affiliation"]) == [
            "ACME Corp.",
            "Giga Group",
        ]

    def test_multiple_occurences_of_the_same_person_in_project_collection_is_saved_with_merged_affiliations(
        self,
    ):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": "Doe, Jane",
                "affiliation": ["Foo PLC"],
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())

        # captured = capfd.readouterr()
        # assert "Existing person found" in captured.out

        assert len(dev_collection) == 1

        assert dev_collection[0]["name"] == "Doe, Jane"
        assert sorted(dev_collection[0]["affiliation"]) == [
            "ACME Corp.",
            "Foo PLC",
            "Giga Group",
        ]

    def test_existing_person_with_no_affiliations_is_updated(self):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": "Doe, Jane",
                "affiliation": [],
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())

        # captured = capfd.readouterr()
        # assert "Existing person found" in captured.out

        assert len(dev_collection) == 1

        assert dev_collection[0]["name"] == "Doe, Jane"
        assert sorted(dev_collection[0]["affiliation"]) == [
            "ACME Corp.",
            "Giga Group",
        ]

    def test_existing_person_with_same_affiliation_is_updated(self):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": "Doe, Jane",
                "affiliation": ["ACME Corp."],
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())

        # captured = capfd.readouterr()
        # assert "Existing person found" in captured.out

        assert len(dev_collection) == 1

        assert dev_collection[0]["name"] == "Doe, Jane"
        assert sorted(dev_collection[0]["affiliation"]) == [
            "ACME Corp.",
        ]

    def test_multiple_existing_persons_with_same_affiliation_are_updated(self):
        client = mongomock.MongoClient()

        # prime the dev collection with existing persons
        personCollection = client.dev.persons
        persons = [
            {
                "name": "Doe, Jane",
                "affiliation": ["ACME Corp."],
            },
            {
                "name": "Doe, John",
                "affiliation": ["Giga Group"],
            },
        ]
        for obj in persons:
            obj["_id"] = personCollection.insert_one(obj).inserted_id

        # prime the project collection, dev collection is left empty
        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ["ACME Corp."],
                        "role": "Tester",
                    },
                ]
            },
            {
                "name": [
                    {
                        "name": {"label": "Doe, John", "qualifier": "person"},
                        "affl": ["Giga Group"],
                        "role": "Tester",
                    },
                ]
            },
        ]
        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "persons", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.persons.find())
        assert len(dev_collection) == 2

        # sort for deterministic retrieval
        dev_collection = sorted(dev_collection, key=lambda x: x["name"])

        assert dev_collection[0]["name"] == "Doe, Jane"
        assert dev_collection[0]["affiliation"] == [
            "ACME Corp.",
        ]
        assert dev_collection[1]["name"] == "Doe, John"
        assert dev_collection[1]["affiliation"] == [
            "Giga Group",
        ]

class TestInstitutionSync(object):
    def test_institutions_merge(self):
        client = mongomock.MongoClient()
        institutionCollection = client.dev.institutions
        institutions = [
            {"name": 'University of Lagos African Cluster Centre (LACC) [institution]'}
        ]
        for obj in institutions:
            obj["_id"] = institutionCollection.insert_one(obj).inserted_id

        collection = client.testDatabase.testProject
        objects = [
            {
                "name": [
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ['Department of Arts and Social Science Education, University of Lagos [institution]'],
                        "role": "Tester"
                    },
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ['Department of Urban and Regional Planning, University of Lagos [institution]'],
                        "role": "Tester"
                    },
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ['Rethinking Cities [institution]'],
                        "role": "Tester"
                    },
                    {
                        "name": {"label": "Doe, Jane", "qualifier": "person"},
                        "affl": ['University of Lagos African Cluster Centre (LACC) [institution]'],
                        "role": "Tester"
                    }
                ]
            }
        ]

        for obj in objects:
            obj["_id"] = collection.insert_one(obj).inserted_id

        syncer = ValueSync.ValueList(
            None, "testDatabase", "testProject", "institutions", client
        )

        sync_result = syncer.synchronise()

        assert sync_result

        dev_collection = list(client.dev.institutions.find())
        assert len(dev_collection) == 4

        # assert dev_collection[0]["name"] == "Doe, Jane"
        # assert sorted(dev_collection[0]["affiliation"]) == [
        #     "ACME Corp.",
        # ]

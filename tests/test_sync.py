import mongomock
import pymongo
import pytest

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

        for case in cases:
            left = case["out"]
            right = ValueSync.ValueList.handle_persons(case["in"])

            for l in left:
                l["affiliation"] = sorted(l["affiliation"])
            for r in right:
                r["affiliation"] = sorted(r["affiliation"])

            assert left == right, f"Failed: {case['desc']}"


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

    @mongomock.patch(servers=(("test.com", 27017),))
    def test_it_cant_be_initialized_with_an_authString_and_a_client(self):
        with pytest.raises(ValueError):
            vl = ValueSync.ValueList(
                "mongodb://test.com:27017",
                "testDatabase",
                "testCollection",
                "testlist",
                pymongo.MongoClient("test.com:27017")
            )

    @mongomock.patch(servers=(("test.com", 27017),))
    def test_it_cant_be_a_preconfigured_client(self):
        vl = ValueSync.ValueList(
            None,
            "testDatabase",
            "testCollection",
            "testlist",
            pymongo.MongoClient("test.com:27017")
        )
        assert isinstance(vl, ValueSync.ValueList)

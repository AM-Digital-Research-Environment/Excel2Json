# Libraries
import difflib
import enum
import pprint
import warnings
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

import pandas as pd
import pymongo
from wasabi import Printer

from .types import collection, dictionary


class Qualifiers(enum.Enum):
    INSTITUTION = "institution"
    GROUP = "group"
    PERSON = "person"


class ValueList(object):
    def __init__(
        self,
        auth_string: str | None,
        db_name: str,
        col_name: str,
        dev_list: str,
        client: pymongo.MongoClient | None = None,
    ):

        if auth_string is not None:
            if client is not None:
                raise ValueError(
                    "Cannot specify both 'auth_string' and 'client'. Only pass 'client'."
                )

            warnings.warn(
                "Passing the 'auth_string'-parameter to ValueList() is deprecated. "
                "Pass an authenticated MongoClient in the 'client'-parameter instead",
                DeprecationWarning,
                stacklevel=2,
            )

            self._client: pymongo.MongoClient[dict[str, Any]] = pymongo.MongoClient(
                auth_string
            )

        elif client is None:
            raise ValueError("The 'client'-parameter is required.")
        else:
            self._client = client

        self._dev_list = dev_list
        self._ref_col = self._client[db_name][col_name]
        self._update_col = self._client["dev"][dev_list]
        self._printer = Printer()

    @staticmethod
    def handle_persons(coll: Iterable[collection.Role]) -> list[dictionary.PersonItem]:
        persons: dict[str, set] = defaultdict(set)
        for item in coll:
            if item["name"]["qualifier"] != Qualifiers.PERSON.value:
                continue

            # touch the key so that we can add to the set provided by the default factory
            persons[item["name"]["label"]] = persons[item["name"]["label"]]

            for aff in item["affl"]:
                persons[item["name"]["label"]].add(aff)

        return [
            dictionary.PersonItem(affiliation=list(affil), name=name)
            for name, affil in persons.items()
        ]

    # Persons in reference collection
    def in_collection(self) -> list[Any]:
        match self._dev_list:
            case "persons":
                docs_with_person = self._ref_col.distinct("name")

                return self.handle_persons(docs_with_person)
            case "institutions":
                # First pass: get all proper affiliations
                affiliations_uniq = list(self._ref_col.distinct("name.affl"))
                # Cleaning list
                out = [i.strip() for i in affiliations_uniq if i.strip()]

                # Second pass: get all names containing an "institution qualifier"
                docs_with_institution = self._ref_col.find(
                    {"name.name.qualifier": Qualifiers.INSTITUTION.value},
                    {"name.name.qualifier": True, "name.name.label": True},
                )
                # this collection may still contain embedded documents with the
                # "group" qualifier, so filter those out
                institutions = [
                    name["name"]["label"]
                    for res in docs_with_institution
                    for name in res["name"]
                    if name["name"]["qualifier"] == Qualifiers.INSTITUTION.value
                ]

                out.extend([n.strip() for n in institutions if n.strip()])

                return sorted(set(out))
            case "groups":
                docs_with_group = self._ref_col.find(
                    {"name.name.qualifier": Qualifiers.GROUP.value},
                    {"name.name.qualifier": True, "name.name.label": True},
                )
                # this collection may still contain embedded documents with the
                # "institution" or "person" qualifier, so filter those out
                groups_uniq = set(
                    [
                        name["name"]["label"]
                        for res in docs_with_group
                        for name in res["name"]
                        if name["name"]["qualifier"] == Qualifiers.GROUP.value
                    ]
                )

                return sorted([n.strip() for n in groups_uniq if n.strip()])
            case _:
                return []

    # Function to see to missing values
    def check_missing(self):
        missing_values = []
        update_coll_list = list(self._update_col.distinct("name"))
        for entity_value in self.in_collection():
            if entity_value not in update_coll_list:
                missing_values.append(entity_value)

        missing_values = [val for val in missing_values if not pd.isna(val)]
        if len(missing_values) == 0:
            self._printer.info("No new values to update.")
            return []

        return missing_values

    # Function to synchronise values
    def synchronise(self) -> bool:
        insert = [{"name": val} for val in self.check_missing()]
        if len(insert) == 0:
            self._printer.info("No documents found to insert.")
            return True

        # TODO: this is a hack
        # For persons, differences may be related to the affiliations in
        # name.affiliation, e.g., one new affiliation that is not yet registered.
        # In this case, we need to update the existing person with the new affiliations.
        # Potential improvement: use `update_many(...,upsert=True)`
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.update_many
        if self._dev_list == "persons":
            # hoist each item below the "name"-key into the top level
            insert = [doc["name"] for doc in insert]
            for i, item in enumerate(insert):
                # look up the person by name
                test = self._update_col.find({"name": item["name"]})
                if test is not None:
                    for t in test:
                        self._printer.info("Existing person found:", t["name"])
                        print(compare_dicts(item, t))
                        # update the item with the set-union of affiliations
                        mongo_affils = set(t["affiliation"])
                        project_affils = set(item["affiliation"])
                        # make sure to convert back to list
                        merged_affils = list(mongo_affils | project_affils)
                        # update based on retrieved ID
                        self._update_col.update_one(
                            {"_id": t["_id"]}, {"$set": {"affiliation": merged_affils}}
                        )

                        # delete the current insertable, so that we can still
                        # use `insert_many` for the remaining items
                        insert[i] = {}

        insert = [item for item in insert if len(item) != 0]
        if len(insert) == 0:
            self._printer.good(
                "Successfully Synchronised!",
                "No items to insert, but no news is good news.",
            )
            return True

        insert_all_result = self._update_col.insert_many(insert)

        if len(insert_all_result.inserted_ids) != len(insert):
            self._printer.fail(
                "Not all requested documents were inserted!",
                f"You requested {len(insert)} objects, but I only inserted {len(insert_all_result.inserted_ids)}.",
            )

            return False

        self._printer.good(
            "Successfully Synchronised!",
            f"Inserted {len(insert_all_result.inserted_ids)} objects",
        )
        return True


def compare_dicts(new, existing):
    local_d1 = new.copy()
    local_d2 = existing.copy()

    if "_id" in local_d1:
        del local_d1["_id"]
    if "_id" in local_d2:
        del local_d2["_id"]

    return "\n" + "\n".join(
        difflib.ndiff(
            pprint.pformat(local_d1).splitlines(), pprint.pformat(local_d2).splitlines()
        )
    )

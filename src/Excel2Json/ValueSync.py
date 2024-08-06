# Libraries
from collections import defaultdict
import enum
from typing import Any, Iterable, List
from pymongo import MongoClient
import pandas as pd
import re
from wasabi import Printer
import warnings
from .types import dictionary, collection

class Qualifiers(enum.Enum):
    INSTITUTION = "institution"
    GROUP = "group"

class ValueList(object):
    def __init__(self, auth_string: str | None, db_name: str, col_name: str, dev_list: str, client: MongoClient | None = None):

        if auth_string is not None:
            warnings.warn(
                "Passing the 'auth_string'-parameter to ValueList() is deprecated. "
                "Pass an authenticated MongoClient in the 'client'-parameter instead",
                DeprecationWarning,
                stacklevel=2
            )

            if client is not None:
                raise ValueError("Cannot specify both 'auth_string' and 'client'. Only pass 'client'.")

            self._client = MongoClient(auth_string)

        if client is None:
            raise ValueError("The 'client'-parameter is required.")

        self._client = client

        self._dev_list = dev_list
        self._ref_col = self._client[db_name][col_name]
        self._update_col = self._client['dev'][dev_list]
        self._printer = Printer()


    @staticmethod
    def handle_persons(coll: Iterable[collection.Role]) -> list[dictionary.PersonItem]:
        persons = defaultdict(set)
        for item in coll:
            if item['name']['qualifier'] is not None:
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
    def in_collection(self) -> List[Any]:
        if self._dev_list == 'persons':
            names = self._ref_col.distinct("name")

            return self.handle_persons(names)
        elif self._dev_list == 'institutions':
            # First pass: get all proper affiliations

            institutions = list(self._ref_col.distinct("name.affl"))
            # Cleaning list
            out = []
            for institute in institutions:
                if institute and not pd.isna(institute):
                    names = [n.strip() for n in institute.split(';') if n.strip()]
                    out.extend(names)

            # Second pass: get all names containing an "institution qualifier"
            names = self._ref_col.distinct("name.name")

            qualifier_pattern = re.compile(re.escape(Qualifiers.INSTITUTION.value))
            names_cleaned = [qualifier_pattern.sub('', name).strip() for name in names if qualifier_pattern.search(name)]
            out.extend(names_cleaned)

            return list(set(out))
        elif self._dev_list == 'groups':
            out = []
            names = self._ref_col.distinct("name.name")

            qualifier_pattern = re.compile(re.escape(Qualifiers.GROUP.value))
            names_cleaned = [qualifier_pattern.sub('', name).strip() for name in names if qualifier_pattern.search(name)]
            out.extend(names_cleaned)

            return list(set(out))
        else:
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

        result = self._update_col.insert_many(insert)

        if len(result.inserted_ids) != len(insert):
            self._printer.fail("Not all requested documents were inserted!")
            return False

        self._printer.good("Successfully Synchronised!")
        return True

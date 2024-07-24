# Libraries
from typing import Any, List
from pymongo import MongoClient
import pandas as pd
import re
from wasabi import Printer
import warnings


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
        self._qualifiers = ["[institution]"]
        self._printer = Printer()

    # Persons in reference collection
    def in_collection(self) -> List[Any]:
        if self._dev_list == 'persons':
            return list(self._ref_col.distinct("name.name"))
        elif self._dev_list == 'institutions':
            # First pass: get all proper affiliations

            institutions = list(self._ref_col.distinct("name.affl"))
            # Cleaning list
            out = []
            for institute in institutions:
                if institute and not pd.isna(institute):
                    names = institute.split(';')
                    names = map(lambda x: x.strip(), names)
                    # "None" will remove anything that evaluates to False
                    names = filter(None, names)
                    out.extend(names)

            # Second pass: get all names containing an "institution qualifier"
            names = self._ref_col.distinct("name.name")

            qualifiers_pattern = re.compile('|'.join(map(re.escape, self._qualifiers)))
            names_cleaned = [qualifiers_pattern.sub('', name).strip() for name in names if qualifiers_pattern.search(name)]
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

# Libraries
from typing import Any, List
from pymongo import MongoClient
import pandas as pd


class ValueList(object):
    def __init__(self, auth_string: str, db_name: str, col_name: str, dev_list: str):
        self._dev_list = dev_list
        self._client = MongoClient(auth_string)
        self._ref_col = self._client[db_name][col_name]
        self._update_col = self._client['dev'][dev_list]

    # Persons in reference collection
    def in_collection(self) -> List[Any]:
        if self._dev_list == 'persons':
            return list(self._ref_col.distinct("name.name"))
        elif self._dev_list == 'institutions':
            institutions = list(self._ref_col.distinct("name.affl"))
            # Cleaning list
            institution_list = []
            for institute in range(len(institutions)):
                if institutions[institute] is not None and not pd.isna(institutions[institute]):
                    for name in [x.strip() for x in list(filter(None, institutions[institute].split(';')))]:
                        institution_list.append(name)
                else:
                    return []
            institution_list = [val for val in institution_list if not pd.isna(val)]
            return list(set(institution_list))
        else:
            return []

    # Function to see to missing values
    def check_missing(self):
        missing_value = []
        update_coll_list = list(self._update_col.distinct("name"))
        for entity_value in self.in_collection():
            if entity_value not in update_coll_list:
                missing_value.append(entity_value)
            else:
                pass
        missing_value = [val for val in missing_value if not pd.isna(val)]
        if len(missing_value) == 0:
            return "No new values to update."
        else:
            return missing_value

    # Function to synchronise values
    def synchronise(self):
        for missing_value in self.check_missing():
            self._update_col.insert_one({"name": missing_value})
        return "Successfully Synchronised!"

# Libraries
from pymongo import MongoClient


class ValueList:
    def __init__(self, auth_string, db_name, col_name, dev_list):
        self._dev_list = dev_list
        self._client = MongoClient(auth_string)
        self._ref_col = self._client[db_name][col_name]
        self._update_col = self._client['dev'][dev_list]

    # Persons in reference collection
    def in_collection(self):
        if self._dev_list == 'persons':
            return list(self._ref_col.distinct("name.name"))
        elif self._dev_list == 'institutions':
            institutions = list(self._ref_col.distinct("name.affl"))
            # Cleaning list
            institution_list = []
            for institute in range(len(institutions)):
                for name in [x.strip() for x in list(filter(None, institutions[institute].split(';')))]:
                    institution_list.append(name)
            return list(set(institution_list))
        else:
            pass

    # Function to see to missing values
    def check_missing(self):
        missing_value = []
        update_coll_list = list(self._update_col.distinct("name"))
        for entity_value in self.in_collection():
            if entity_value not in update_coll_list:
                missing_value.append(entity_value)
            else:
                pass
        if len(missing_value) == 0:
            return "No new values to update."
        else:
            return missing_value

    # Function to synchronise values
    def synchronise(self):
        for missing_value in self.check_missing():
            self._update_col.insert_one({"name": missing_value})
        return "Successfully Synchronised!"

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 15:40:25 2023

@author: AfricaMultiple
"""

# Libraries

from pathlib import Path
from typing import Any
from pymongo import MongoClient
from pymongo.collection import Collection as MongoCollection
import json
import pandas as pd
import numpy as np
import re
import os


class MDES_CleanUp(object):
    """Class for cleaning up data and changing the field names."""

    def __init__(self, sheet_path: str | Path, mongo_client: MongoClient | None = None):
        if mongo_client is None:
            self.client = self.mongo_dictCollection_auth()
        else:
            self.client = mongo_client

        tabs_collection = self.dictionaries_collection.find_one({"name": 'Tab Names'})
        if tabs_collection is None:
            raise ValueError("Document 'Tab Names' not found in dictionaries collection.")

        self.tabs = tabs_collection['tabs'].values()

        fields_collection = self.dictionaries_collection.find_one({"name": 'Field Names by Excel Table Tabs'})
        if fields_collection is None:
            raise ValueError("Document 'Field Names by Excel Table Tabs' not found in dictionaries collection.")

        self.fields = pd.DataFrame(fields_collection['tabs'])

        self.sheet_path = sheet_path

    @property
    def dictionaries_collection(self) -> MongoCollection:
        return self.client.dev['dictionaries']

    def _get_sec_level(self, x) -> str | None:
        match = re.search(r'(?<=\[).*?(?=\])', x)
        if match:
            return match[0]
        return None

    def _resource_clean(self, x) -> str:
        return x.split(' (')[0]

    def Sheet_CleanUp(self, tab) -> pd.DataFrame:
        data = pd.read_excel(self.sheet_path, sheet_name=tab, header=None)
        data = data.iloc[data.loc[data.iloc[:,0] == 1].index[0]:,:].reset_index(drop=True)
        data.columns = self.fields[tab].dropna().values
        data = data.drop(columns='slno')
        data = data.dropna(subset='filename')
        return data

    def execute(self):
        iteration = 0
        for tab in self.tabs:
            iteration += 1
            if iteration == 1:
                base = self.Sheet_CleanUp(tab)
            else:
                base = base.merge(self.Sheet_CleanUp(tab), on='filename')
        # Adding additional Columns & recoding
        base['collection'] = base['collection'].replace('No', False).replace('Yes', True)
        base['title_type_main'] = np.repeat('main', len(base))
        base['security_level'] = base['security_level'].copy().apply(self._get_sec_level)
        base['resource_type'] = base['resource_type'].copy().apply(self._resource_clean)
        return base
    
###############################################################################

    # Misc. Functions
    
    def extract_json_data(self, path: str) -> Any:
        with open(path, 'r') as f:
            contents = json.load(f)

        return contents
    
    def mongo_dictCollection_auth(self) -> MongoClient:
        """
        Authenticates a MongoClient given a pre-specified connection string.

        Read a connection string from the specified JSON-file, establish a
        connection to MongoDB, and return the client.

        Returns
        -------
        pymongo.MongoClient
            The client, authenticated using the connection string provided in the JSON-file.

        Raises
        ------
        FileNotFoundError
            If the JSON-file with the connection string does not exist.
        KeyError
            If the 'botConnectionString' is not found in the loaded dictionary.
        pymongo.errors.ConnectionFailure
            If the connection to MongoDB fails.

        .. deprecated::
            Calling this method explicitly is deprecated. Pass an authenticated
            client to the class constructor instead.
        """
        import warnings
        warnings.warn("Don't call this method explicitly. Rather, pass an authenticated client to the class constructor.", DeprecationWarning, stacklevel=2)

        return MongoClient(self.extract_json_data(os.path.join("dictionaries", "mongo_auth.json"))['botConnectionString'])

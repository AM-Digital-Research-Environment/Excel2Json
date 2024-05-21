# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 15:40:25 2023

@author: AfricaMultiple
"""

# Libraries

import pymongo
from pymongo import MongoClient
import json
import pandas as pd
import numpy as np
import re

# Class for cleaning up data and changing the field names

class MDES_CleanUp():

    def __init__(self, sheet_path):
        self.tabs = self.mongo_dictCollection_auth().find_one({"name":'Tab Names'})['tabs'].values()
        self.fields = pd.DataFrame(self.mongo_dictCollection_auth().find_one({"name":'Field Names by Excel Table Tabs'})['tabs'])
        self.sheet_path = sheet_path
        self.get_sec_level = lambda x : re.search('(?<=\[).*?(?=\])', x)[0]
        self.resource_clean = lambda x : x.split(' (')[0] 

    def Sheet_CleanUp(self, tab):
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
        base['security_level'] = base['security_level'].copy().apply(self.get_sec_level)
        base['resource_type'] = base['resource_type'].copy().apply(self.resource_clean)
        return base
    
###############################################################################

    ## Misc. Functions
    
    def extract_json_data(self,path):
        f = open(path)
        contents = json.load(f)
        f.close()
        return contents    
    
    def mongo_dictCollection_auth(self):
        client = MongoClient(self.extract_json_data(r"dictionaries\mongo_auth.json")['botConnectionString'])
        return client.dev['dictionaries']
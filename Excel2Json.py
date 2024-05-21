# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 15:35:34 2023

@author: AfricaMultiple
"""
# Libraries

import pandas as pd
import numpy as np
import re
from datetime import datetime
from ExcelCleaner import MDES_CleanUp

class ExportJson:
    
    def __init__(self, file_path, project_Id, dspace_Id):
        # Input given is project ID, defualt DSpace instance
        self.data = MDES_CleanUp(file_path).execute()
        self.project_Id = project_Id
        self.dspace_Id = dspace_Id
        self.delimiter = ';'
        
    def run(self):
        json_list = []
        for i in range(len(self.data)):
            row = self.data.iloc[i,:].copy()
            
            data_dict = {}
            
            # Internal ID (Format 3-Letter Project ID - DSpace Instance - DSpace Instance/ Storage Location - Index ID)
            data_dict['dre_id'] = self.project_Id + "-" + self.set_default(value = row.user_rights, exception = "No Raw Data", default_value = '99', return_value = self.dspace_Id) + "-" + format(i, '04x')
            
            
            # Filename
            
            data_dict['bitstream'] = row.filename
            
            # Security Level
            
            data_dict['security'] = row['security_level']
            
            # Collection
            
            data_dict['isCollection'] = self.BoolClean(row['collection'])
  
            # Sponsor
            
            data_dict['sponsor'] = self.list_cleanUp(row['sponsor'], [])

            # Title(s)
            
            title_list = []
            all_title = row.filter(regex='title').copy() 
            
            for i in ['main'] + list(range(2,6)):
                title = all_title.filter(regex=f'_{i}')
                title.index = [c.replace(f'_{i}','') for c in title.index]
                if pd.isna(title['title']) != True:
                    title_list.append(title.to_dict())
                else:
                    continue                
            data_dict['titleInfo'] = title_list
            
            # Dates
            
            date_dict = {}
            all_date = row.filter(regex='date_').copy()
            
            for k in all_date.keys():
                if pd.isna(row[k]) == False:
                    date_dict[k.replace('date_','')] = self.dateWrangling(all_date[k])
                else:
                    continue
                
            data_dict['dateInfo'] = date_dict
            
            # Roles
            
            role_list = []
            all_role = row.filter(regex='name_\d+$|role_\d+$|affl_\d+$')
            
            for i in range(1,int(len(all_role.index)/3)+1):
                role = all_role.filter(regex=f'_{i}$')                
                role.index = [c.replace(f'_{i}','') for c in role.index]
                if pd.isna(role['name']) != True:
                    role_list.append(role.to_dict())
                else:
                    continue

            data_dict['name'] = role_list

            # Note
            
            data_dict['note'] = row['note']

            # Subject
            
            data_dict['subject'] =  self.list_cleanUp(row['subject'],[])           
            
            # Related Items
            
            rel_items = {}
            
            for c in row.filter(like='rel_').index:
                if pd.isna(row[c]) != True:
                    rel_items[c] = self.list_cleanUp(row[c], [])
            
            data_dict['relatedItems'] = rel_items
            
            # Identifiers
            
            idetifiers = []
            ids = row.filter(regex='identifier_\d+$|identifier_type_\d+$')
            
            for n in range(1, int(len(ids.index)/2)*1):
                id_n = ids.filter(regex=f'identifier_{n}$|identifier_type_{n}$')
                id_n.index = [c.replace(f'_{n}','') for c in id_n.index]
                if pd.isna(id_n['identifier']) != True:
                    idetifiers.append(id_n.to_dict())
                else:
                    continue
                
            data_dict['identifier'] = idetifiers
            
            # Location 
            
            ## Origin
            
            origin = row.filter(like='loc_')
            origin.index = [col.replace('loc_origin_','') for col in origin.index]
            origin = origin.to_dict()
            
            ## Current Location
            
            current_loc = self.list_cleanUp(row['current_location'],[])
            
            data_dict['location'] = {'origin': origin, 'current': current_loc}
            
            # Access Condition
            
            ## Usage and Distribution License
            
            rights = self.list_cleanUp(row['use_copy_rights'], [])
            
            ## Repository Access Specification
            
            use = {}
            user = row.filter(like='user')
            use['type'] = user.user_rights
            use['admins'] = self.list_cleanUp(user.users, 'All')
            
            data_dict['accessCondition'] = {'rights': rights, 'usage': use}
            
            # Resource Type
            
            data_dict['typeOfResource'] = row['resource_type']
            
            # Genre
            
            genre_type = {}
            
            genre = row.filter(like='genre')
            genre.index = [col.replace('genre_','') for col in genre.index]
            for g in genre.index:
                if pd.isna(genre[g]) != True:
                    genre_type[g] = self.list_cleanUp(genre[g], [])
                else:
                    continue  
            
            data_dict['genre'] = genre_type
            
            # Language
            
            data_dict['language'] = self.list_cleanUp(row.language, [])
            
            # Physical Description
            physical_desc = {}
            physical = row.filter(regex='physical_|dig_')
            physical.index = [re.sub(r'\w+_','',col) for col in physical.index]
            i = 0
            for key in physical.index:
                i += 1
                if i < 3:
                    physical_desc[key] =  physical[key]
                else:
                    physical_desc[key] = self.list_cleanUp(physical[key], [])
            
            data_dict['physicalDescription'] = physical_desc     
            
            # Abstract
            
            data_dict['abstract'] = row.abstract

            # Table of Content
            
            data_dict['tableOfContents'] = row['table_contents']
            
            # Target Audience
            
            data_dict['targetAudience'] = self.list_cleanUp(row['target_aud'], [])
            
            # Tags
            
            data_dict['tags'] = self.list_cleanUp(row['tags'], [])
                
            # Append to dictionary list            
            json_list.append(data_dict)
        
        return json_list
            
###############################################################################        
    def list_cleanUp(self, list_string, exception):
        try:
            return list(filter(None,[l.strip() for l in list_string.split(self.delimiter)]))
        except:
            pass
        try:
            return list(filter(None,list_string))
        except:
            return exception
        
    def set_default(self, value, exception, default_value, return_value):
        if value == exception:
            return default_value
        else:
            return return_value
        
    # Date converter function
    def date_convert(self,date):
        try:
            date = str(date)
            datelen = len(date)
            if datelen == 8:
                return datetime.strptime(date,"%Y%m%d").isoformat()
            elif datelen == 6:
                return datetime.strptime(date,"%Y%m").isoformat()
            elif datelen == 4:
                return datetime.strptime(date,"%Y").isoformat()
        except:
            return np.nan

    # Date Cleanup Function 
    def dateWrangling(self,date_string):
        try:
            date = str.strip(date_string.replace(';',''))
        except:
            date = date_string
        if len(str(date).split('--')) == 2:
            date_start = self.date_convert(str(date).split('--')[0])
            date_end = self.date_convert(str(date).split('--')[1])
        else:
            date_start = np.nan
            try:
                date_end = self.date_convert(date)
            except:
                date_end = np.nan
        return {'start':date_start, 'end':date_end}
    
    # Boolean Handling
    
    def BoolClean(self, x):
        if x == True:
            return 1
        elif x == False:
            return 0
        else:
            return None
            

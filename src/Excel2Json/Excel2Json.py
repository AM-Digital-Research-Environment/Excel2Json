# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 15:35:34 2023

@author: AfricaMultiple
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from pymongo import MongoClient
from wasabi import Printer

from .dev.ExcelCleaner import MDES_CleanUp
from .LocClient import LocClient
from .types import collection
from .ValueSync import Qualifiers


class ExportJson(object):
    # pattern with two capturing groups for 'name' and 'qualifier' part;
    # compiled pattern looks like this: (.*?)\s*\[(foo|bar|quux)\]
    qualifiers_pattern = re.compile(
        r"(?P<name>.*?)\s*\[(?P<qualifier>"
        + "|".join(map(lambda x: x.value, Qualifiers))
        + r")\]"
    )

    # File can be path string or the dataframe object
    def __init__(
        self,
        file: str | Path | pd.DataFrame,
        project_id,
        dspace_id,
        mongo_client: MongoClient | None = None,
    ):
        # Input given is project ID, default DSpace instance
        if isinstance(file, str) or isinstance(file, Path):
            self.data = MDES_CleanUp(file, mongo_client=mongo_client).execute()
        elif isinstance(file, pd.DataFrame):
            self.data = file
        self.project_Id = project_id
        self.dspace_Id = dspace_id
        self.delimiter = ";"
        self.msg = Printer()
        self.loc_client = LocClient()

    def run(self):  # noqa: C901
        json_list = []
        with self.msg.loading("Building data list..."):
            for i in range(len(self.data)):
                row = self.data.iloc[i, :].copy()

                data_dict = {
                    # Internal ID (Format 3-Letter Project ID - DSpace Instance/ Storage Location - Index ID)
                    "dre_id": self.project_Id
                    + "-"
                    + self.set_default(
                        value=row.user_rights,
                        exception="No Raw Data",
                        default_value="99",
                        return_value=self.dspace_Id,
                    )
                    + "-"
                    + format(i, "04x"),
                    # Bitstream
                    "bitstream": self.set_default(
                        value=row.user_rights,
                        exception="No Raw Data",
                        default_value="",
                        return_value=row["filename"],
                    ),
                    # Security Level
                    "security": row["security_level"],
                    # Collection
                    # 'isCollection': self.boolclean(row['collection']),
                    "collection": self.list_cleanup(row["collection"], []),
                    # Sponsor
                    "sponsor": self.list_cleanup(row["sponsor"], []),
                    # Project
                    "project": {"id": row.project_id, "name": row.project_name},
                    # Citation
                    "citation": self.list_cleanup(row["citation"], []),
                    # Url
                    "url": self.list_cleanup(row["url"], []),
                }

                # Title(s)

                title_list = []
                all_title = row.filter(regex="title").copy()

                for tType in ["main"] + list(range(2, 6)):
                    title = all_title.filter(regex=f"_{tType}")
                    title.index = [c.replace(f"_{tType}", "") for c in title.index]
                    if not pd.isna(title["title"]):
                        title["title"] = str(title["title"]).strip()
                        title_list.append(title.to_dict())
                    else:
                        continue
                data_dict["titleInfo"] = title_list

                # Dates

                date_dict = {}
                all_date = row.filter(regex="date_").copy()

                for k in all_date.keys():
                    if not pd.isna(row[k]):
                        date_dict[k.replace("date_", "")] = self.datewrangling(
                            all_date[k]
                        )
                    else:
                        continue

                data_dict["dateInfo"] = date_dict

                # Roles

                role_list = []
                all_role = row.filter(regex=r"name_\d+$|role_\d+$|affl_\d+$")

                for rtype in range(1, int(len(all_role.index) / 3) + 1):
                    role = all_role.filter(regex=f"_{rtype}$")
                    role.index = [c.replace(f"_{rtype}", "") for c in role.index]
                    built = self.build_role(role)
                    if built is None:
                        continue

                    role_list.append(built)

                data_dict["name"] = role_list

                # Note
                data_dict["note"] = row["note"]

                # Subject

                subjects = self.list_cleanup(row["subject"], [])
                data_dict["subject"] = [
                    {
                        "uri": np.nan,
                        "authority": np.nan,
                        "origLabel": s,
                        "authLabel": np.nan,
                    }
                    for s in subjects
                ]

                # Related Items

                rel_items = {}

                for c in row.filter(like="rel_").index:
                    if not pd.isna(row[c]):
                        rel_items[c] = self.list_cleanup(row[c], [])

                data_dict["relatedItems"] = rel_items

                # Identifiers

                identifiers = []
                ids = row.filter(regex=r"identifier_\d+$|identifier_type_\d+$")

                for n in range(1, int(len(ids.index) / 2) * 1):
                    id_n = ids.filter(regex=f"identifier_{n}$|identifier_type_{n}$")
                    id_n.index = [c.replace(f"_{n}", "") for c in id_n.index]
                    if not pd.isna(id_n["identifier"]):
                        identifiers.append(id_n.to_dict())
                    else:
                        continue

                data_dict["identifier"] = identifiers

                # Location

                # Origin
                origin_list = []

                origin = row.filter(like="loc_")
                origin.index = [col.replace("loc_origin_", "") for col in origin.index]
                for f in origin.index:
                    try:
                        origin[f] = list(
                            map(
                                lambda x: x.replace("99", ""),
                                self.list_cleanup(origin[f], []),
                            )
                        )
                    except TypeError:
                        pass
                if range(len(origin["l1"])) == 1:
                    origin_list = [origin.to_dict()]
                else:
                    for n in range(len(origin["l1"])):
                        origin_dict = {
                            "l1": origin["l1"][n],  # country
                            "l2": (
                                origin["l2"][n]
                                if len(origin["l2"]) >= n + 1 and origin["l2"][n] != ""
                                else np.nan
                            ),  # region
                            "l3": (
                                origin["l3"][n]
                                if len(origin["l3"]) >= n + 1 and origin["l3"][n] != ""
                                else np.nan
                            ),
                        }  # subregion
                        origin_list.append(origin_dict)

                # Current Location

                current_loc = self.list_cleanup(row["current_location"], [])

                data_dict["location"] = {"origin": origin_list, "current": current_loc}

                # Access Condition

                # Usage and Distribution License
                rights = self.list_cleanup(row["use_copy_rights"], [])

                # Repository Access Specification

                use = {}
                user = row.filter(like="user")
                use["type"] = user.user_rights
                use["admins"] = self.list_cleanup(user.users, "All")

                data_dict["accessCondition"] = {"rights": rights, "usage": use}

                # Resource Type
                data_dict["typeOfResource"] = row["resource_type"]

                # Genre

                genre_type = {}

                genre = row.filter(like="genre")
                genre.index = [col.replace("genre_", "") for col in genre.index]
                for g in genre.index:
                    if not pd.isna(genre[g]):
                        genre_type[g] = self.list_cleanup(genre[g], [])
                    else:
                        continue

                data_dict["genre"] = genre_type

                # Language
                data_dict["language"] = self.list_cleanup(row.language, [])

                # Physical Description
                physical_desc = {}
                physical = row.filter(regex="physical_|dig_")
                physical.index = [re.sub(r"\w+_", "", col) for col in physical.index]
                i = 0
                for key in physical.index:
                    i += 1
                    if i < 3:
                        physical_desc[key] = physical[key]
                    else:
                        physical_desc[key] = self.list_cleanup(physical[key], [])

                data_dict["physicalDescription"] = physical_desc

                # Abstract
                data_dict["abstract"] = row.abstract

                # Table of Content
                data_dict["tableOfContents"] = row["table_contents"]

                # Target Audience
                data_dict["targetAudience"] = self.list_cleanup(row["target_aud"], [])

                # Tags
                data_dict["tags"] = self.list_cleanup(row["tags"], [])

                # Append to dictionary list
                json_list.append(data_dict)

        self.msg.good("Data built!")

        self.msg.info("Fetching LoC URIs for subject headings")
        for item in json_list:
            for s in item["subject"]:
                res = self.loc_client.get_subject(s["origLabel"])
                if res is None:
                    continue
                label, uri = res
                s["authLabel"] = label
                s["uri"] = uri
                s["authority"] = (
                    "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings"
                )

        self.msg.good("LoC fetch completed!")

        return json_list

    # Auxiliary Functions
    def list_cleanup(self, list_string, exception):
        try:
            return list(
                filter(
                    None, [part.strip() for part in list_string.split(self.delimiter)]
                )
            )
        except:  # noqa: E722
            pass

        try:
            return list(filter(None, list_string))
        except:  # noqa: E722
            return exception

    def set_default(self, value, exception, default_value, return_value):
        if value == exception:
            return default_value
        else:
            return return_value

    # Date converter function
    def date_convert(self, date):
        try:
            date = str(date)
            date_length = len(date)
            if date_length == 8:
                return datetime.strptime(date, "%Y%m%d").isoformat()
            elif date_length == 6:
                return datetime.strptime(date, "%Y%m").isoformat()
            elif date_length == 4:
                return datetime.strptime(date, "%Y").isoformat()
        except:  # noqa: E722
            return np.nan

    # Date Cleanup Function
    def datewrangling(self, date_string):
        try:
            date = date_string.replace(";", "").strip()
        except:  # noqa: E722
            date = date_string
        if len(str(date).split("--")) == 2:
            date_start = self.date_convert(str(date).split("--")[0])
            date_end = self.date_convert(str(date).split("--")[1])
        else:
            date_start = np.nan
            try:
                date_end = self.date_convert(date)
            except:  # noqa
                date_end = np.nan
        return {"start": date_start, "end": date_end}

    # Boolean Handling

    def boolclean(self, x):
        if x:
            return 1
        elif not x:
            return 0
        else:
            return None

    @classmethod
    def build_role(cls, data: dict) -> Optional[collection.Role]:
        if pd.isna(data["name"]):
            return None

        # set the 'person'-qualifier as default; will be overwritten if another
        # qualifier is found
        name = collection.Name(
            label=data["name"].strip(), qualifier=Qualifiers.PERSON.value
        )
        role = collection.Role(name=name, affl=[], role="")

        if "role" in data and not pd.isna(data["role"]):
            role["role"] = data["role"].strip()

        match = cls.qualifiers_pattern.match(role["name"]["label"])
        if match:
            role["name"]["label"] = match.group("name")
            role["name"]["qualifier"] = match.group("qualifier")

        if pd.isna(data["affl"]):
            return role

        role["affl"] = [a.strip() for a in data["affl"].split(";") if a.split()]
        role["affl"] = [cls.qualifiers_pattern.sub(r"\g<name>", item) for item in role["affl"]]

        return role

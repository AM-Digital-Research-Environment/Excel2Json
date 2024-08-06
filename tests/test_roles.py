import numpy as np
import pandas as pd
from Excel2Json import Excel2Json


def test_roles_are_transformed_to_the_correct_schema():
    cases = [
        {
            "desc": "No name",
            "in": {"name": np.nan, "affl": np.nan},
            "out": None,
        },
        {
            "desc": "Name without qualifier, no affiliation",
            "in": {"name": "Doe, Jane", "affl": np.nan},
            "out": {"name": {"label": "Doe, Jane", "qualifier": None}, "affl": None},
        },
        {
            "desc": "Name without qualifier, single affiliation",
            "in": {"name": "Doe, Jane", "affl": "ACME Corp."},
            "out": {
                "name": {"label": "Doe, Jane", "qualifier": None},
                "affl": ["ACME Corp."],
            },
        },
        {
            "desc": "Name without qualifier, single affiliation, trailing semicolon",
            "in": {"name": "Doe, Jane", "affl": "ACME Corp.;"},
            "out": {
                "name": {"label": "Doe, Jane", "qualifier": None},
                "affl": ["ACME Corp."],
            },
        },
        {
            "desc": "Name without qualifier, multiple affiliations",
            "in": {"name": "Doe, Jane", "affl": "ACME Corp.; Giga Corp."},
            "out": {
                "name": {"label": "Doe, Jane", "qualifier": None},
                "affl": ["ACME Corp.", "Giga Corp."],
            },
        },
        {
            "desc": "Name with qualifier, single affiliation",
            "in": {"name": "Int. Conf. on Afr. Economy [group]", "affl": "IEEE"},
            "out": {
                "name": {
                    "label": "Int. Conf. on Afr. Economy",
                    "qualifier": "group",
                },
                "affl": ["IEEE"],
            },
        },
        {
            "desc": "Name with qualifier, no affiliation",
            "in": {"name": "First Anchor Books [institution]", "affl": np.nan},
            "out": {
                "name": {"label": "First Anchor Books", "qualifier": "institution"},
                "affl": None,
            },
        },
    ]

    for case in cases:
        assert case["out"] == Excel2Json.ExportJson.build_role(case["in"]), f"Failed: {case['desc']}"

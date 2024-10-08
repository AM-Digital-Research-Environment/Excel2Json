import numpy as np
from Excel2Json import Excel2Json


def test_roles_are_transformed_to_the_correct_schema():
    cases = [
        {
            "desc": "No name",
            "in": {"role": np.nan, "name": np.nan, "affl": np.nan},
            "out": None,
        },
        {
            "desc": "Name without qualifier, no affiliation",
            "in": {"name": "Doe, Jane", "affl": np.nan, "role": "Researcher "},
            "out": {
                "name": {
                    "label": "Doe, Jane",
                    "qualifier": "person",
                },
                "affl": [],
                "role": "Researcher",
            },
        },
        {
            "desc": "Name without qualifier, single affiliation",
            "in": {"name": "Doe, Jane", "affl": "ACME Corp.", "role": "Researcher"},
            "out": {
                "name": {
                    "label": "Doe, Jane",
                    "qualifier": "person",
                },
                "affl": ["ACME Corp."],
                "role": "Researcher",
            },
        },
        {
            "desc": "Name without qualifier, single affiliation, trailing semicolon",
            "in": {"name": "Doe, Jane", "affl": "ACME Corp.;", "role": "Researcher"},
            "out": {
                "name": {
                    "label": "Doe, Jane",
                    "qualifier": "person",
                },
                "affl": ["ACME Corp."],
                "role": "Researcher",
            },
        },
        {
            "desc": "Name without qualifier, multiple affiliations",
            "in": {
                "name": "Doe, Jane",
                "affl": "ACME Corp.; Giga Corp.",
                "role": "Researcher",
            },
            "out": {
                "name": {"label": "Doe, Jane", "qualifier": "person"},
                "affl": ["ACME Corp.", "Giga Corp."],
                "role": "Researcher",
            },
        },
        {
            "desc": "Name with qualifier, single affiliation",
            "in": {
                "name": "Int. Conf. on Afr. Economy [group]",
                "affl": "IEEE",
                "role": "Researcher",
            },
            "out": {
                "name": {
                    "label": "Int. Conf. on Afr. Economy",
                    "qualifier": "group",
                },
                "affl": ["IEEE"],
                "role": "Researcher",
            },
        },
        {
            "desc": "Name with qualifier, no affiliation",
            "in": {
                "name": "First Anchor Books [institution]",
                "affl": np.nan,
                "role": "Researcher",
            },
            "out": {
                "name": {
                    "label": "First Anchor Books",
                    "qualifier": "institution",
                },
                "affl": [],
                "role": "Researcher",
            },
        },
        {
            "desc": "Name with qualifier with leading spaces",
            "in": {
                "name": "First Anchor Books  [institution]",
                "affl": np.nan,
                "role": "Researcher",
            },
            "out": {
                "name": {
                    "label": "First Anchor Books",
                    "qualifier": "institution",
                },
                "affl": [],
                "role": "Researcher",
            },
        },
        {
            "desc": "Name with qualifier with trailing spaces",
            "in": {
                "name": "First Anchor Books [institution] ",
                "affl": np.nan,
                "role": "Researcher",
            },
            "out": {
                "name": {
                    "label": "First Anchor Books",
                    "qualifier": "institution",
                },
                "affl": [],
                "role": "Researcher",
            },
        },
        {
            "desc": "Affiliation with institution qualifier, qualifier is stripped",
            "in": {
                "name": "Doe, Jane",
                "affl": "ACME Corp.  [institution] ",
                "role": "Researcher",
            },
            "out": {
                "name": {
                    "label": "Doe, Jane",
                    "qualifier": "person",
                },
                "affl": ["ACME Corp."],
                "role": "Researcher",
            },
        },
        {
            "desc": "Affiliation with person qualifier, qualifier is stripped",
            "in": {
                "name": "Doe, Jane",
                "affl": "Foo Bar  [person]  ",
                "role": "Researcher",
            },
            "out": {
                "name": {
                    "label": "Doe, Jane",
                    "qualifier": "person",
                },
                "affl": ["Foo Bar"],
                "role": "Researcher",
            },
        },
        {
            "desc": "Affiliation with group qualifier, qualifier is stripped",
            "in": {
                "name": "Doe, Jane",
                "affl": "Giga Group  [group]  ",
                "role": "Researcher",
            },
            "out": {
                "name": {
                    "label": "Doe, Jane",
                    "qualifier": "person",
                },
                "affl": ["Giga Group"],
                "role": "Researcher",
            },
        },
    ]

    for case in cases:
        left = case["out"]
        right = Excel2Json.ExportJson.build_role(case["in"])

        assert left == right, f"Failed: {case['desc']}"

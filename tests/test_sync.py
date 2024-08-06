from Excel2Json import ValueSync


def test_persons_are_transformed():
    cases = [
        {
            "desc": "Institution, no affiliation",
            "in": [
                {
                    "name": {"label": "ACME Corp.", "qualifier": "institution"},
                    "affl": [],
                }
            ],
            "out": [],
        },
        {
            "desc": "Group, no affiliation",
            "in": [
                {
                    "name": {"label": "Giga Group", "qualifier": "group"},
                    "affl": [],
                }
            ],
            "out": [],
        },
        {
            "desc": "Institution, single affiliation",
            "in": [
                {
                    "name": {"label": "ACME Corp.", "qualifier": "institution"},
                    "affl": ["IEEE"],
                }
            ],
            "out": [],
        },
        {
            "desc": "Group, multiple affiliations",
            "in": [
                {
                    "name": {"label": "Giga Group", "qualifier": "group"},
                    "affl": ["IEEE", "FooBar"],
                }
            ],
            "out": [],
        },
        {
            "desc": "Single person, no affiliation",
            "in": [
                {
                    "name": {"label": "Doe, Jane", "qualifier": None},
                    "affl": [],
                }
            ],
            "out": [{"name": "Doe, Jane", "affiliation": []}],
        },
        {
            "desc": "Single person, single affiliation",
            "in": [
                {
                    "name": {"label": "Doe, Jane", "qualifier": None},
                    "affl": ["IEEE"],
                }
            ],
            "out": [{"name": "Doe, Jane", "affiliation": ["IEEE"]}],
        },
        {
            "desc": "Multiple distinct persons, mixed affiliations",
            "in": [
                {
                    "name": {"label": "Doe, Jane", "qualifier": None},
                    "affl": ["IEEE"],
                },
                {
                    "name": {"label": "Doe, John", "qualifier": None},
                    "affl": ["ACME Corp."],
                },
                {
                    "name": {"label": "Test, Tina", "qualifier": None},
                    "affl": ["ACME Corp."],
                },
            ],
            "out": [
                {"name": "Doe, Jane", "affiliation": ["IEEE"]},
                {"name": "Doe, John", "affiliation": ["ACME Corp."]},
                {"name": "Test, Tina", "affiliation": ["ACME Corp."]},
            ],
        },
        {
            "desc": "Multiple same persons with differing affiliations",
            "in": [
                {
                    "name": {"label": "Doe, Jane", "qualifier": None},
                    "affl": ["IEEE"],
                },
                {
                    "name": {"label": "Doe, Jane", "qualifier": None},
                    "affl": ["ACME Corp."],
                },
                {
                    "name": {"label": "Test, Tina", "qualifier": None},
                    "affl": ["ACME Corp."],
                },
            ],
            "out": [
                {"name": "Doe, Jane", "affiliation": ["IEEE", "ACME Corp."]},
                {"name": "Test, Tina", "affiliation": ["ACME Corp."]},
            ],
        },
    ]

    for case in cases:
        left = case["out"]
        right = ValueSync.ValueList.handle_persons(case["in"])

        for l in left:
            l["affiliation"] = sorted(l["affiliation"])
        for r in right:
            r["affiliation"] = sorted(r["affiliation"])

        assert left == right, f"Failed: {case['desc']}"

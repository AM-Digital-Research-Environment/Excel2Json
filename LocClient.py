from collections import defaultdict
from typing import Tuple
import time

import requests
from wasabi import Printer


class LocClient(object):
    """
    An API client for the LoC suggestion API.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.params = {
            "searchtype": "leftanchord",
            "memberOf": "http://id.loc.gov/authorities/subjects/collection_LCSHAuthorizedHeadings",
            "count": 5,
        }
        self.msg = Printer()
        self.cache = dict()

    def get_subject(self, term: str) -> Tuple[str, str] | None:
        if term in self.cache:
            return self.cache[term]

        response = self.session.get(
            "https://id.loc.gov/authorities/subjects/suggest2", params={"q": term}
        )
        # pause for 200 milliseconds to avoid rate-limiting
        time.sleep(0.2)
        data = response.json()

        if data["count"] == 0:
            self.msg.info(f"No API results for term '{term}'")
            self.cache[term] = None
            return None

        for x in data["hits"]:
            if str(x["aLabel"]).lower() == term.lower():
                res = (x["aLabel"], x["uri"])
                self.cache[term] = res
                return res

        self.msg.info(f"No results with matching aLabel for term '{term}'")
        self.cache[term] = None
        return None

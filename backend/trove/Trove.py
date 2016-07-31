__author__ = 'Benjamin George Roberts <benjamin.roberts@anu.edu.au>'

from backend.settings import TROVE_KEY
from backend.orm import db_context as _db
from backend.orm.models import Trove
from bs4 import BeautifulSoup
from random import shuffle
import requests

TROVE_ZONES = ["picture", "newspaper", "article"] #People have no relevance
TROVE_ROOT = "http://api.trove.nla.gov.au/result"
TROVE_RELEVANCE = "very relevant"
TROVE_ZONE_FILTER = lambda z: z["name"] in TROVE_ZONES
TROVE_RELEVANCE_FILTER = lambda w: w.relevance.text == TROVE_RELEVANCE
TROVE_RECORD_TAKE = 3

if TROVE_KEY is None:
    raise ImportError("can't load Trove module without TROVE_KEY")

class TroveAdapter:
    def __init__(self, abc_content, *args):
        """
        :param abc_content_id: parent abc content instance
        :type abc_content_id: Content
        :return:
        """
        self.content = abc_content
        self.params = {"key": TROVE_KEY}

        if len(args) > 0:
            self.search_terms = args
        else:
            self.search_terms = TroveAdapter.__generate_search_terms__(self.content)

        query = Trove.query.filter_by(abc_id=self.content.id).all()
        self.items = query if len(query) is not 0 else None

    @staticmethod
    def __generate_search_terms__(abc_content, limit=3):
        """
        Generate a list of search terms from a content object
        :param content_id:
        :return: Content
        """
        json_obj = abc_content.get_data()

        if "keywords" not in json_obj:
            return []
        else:
            keywords = json_obj["keywords"].split(", ")
            shuffle(keywords)
            return keywords[:min(limit, len(keywords)-1)]


    def get_items(self, force_update=False):
        """
        Retrieve the data from the external source and returns the entires in a dict
        Is responsible for saving the corresponding models
        :return: dict of items
        :rtype: dict
        """
        if force_update and self.items is not None:
            # clear out the cache
            for item in self.items:
                _db.session.delete(item)

            self.items = None
            _db.session.commit()

        if self.items is None:
            self.items = []
            # Query for each
            for term in self.search_terms:
                for trove_item in self.__trove_query__(term):
                    _db.session.add(trove_item)
                    self.items.append(trove_item)

        _db.session.commit()
        return self.items


    def __trove_query__(self, search_term):

        #initialise local params and copy instance level ones
        params = {}
        for k,v in self.params.items():
            params[k] = v

        # Set query
        params["q"] = search_term

        items = []

        # Do query per zone
        for zone in TROVE_ZONES:
            params["zone"] = zone
            response = requests.get(TROVE_ROOT, params=params)

            # Check correct
            if not response.ok:
                continue

            # Parse xml response
            bss = BeautifulSoup(response.text, features="xml")
            records = bss.find("zone").records

            # Get first 3 relevant results
            for work in list(filter(TROVE_RELEVANCE_FILTER, records))[:TROVE_RECORD_TAKE]:
                cache = Trove(self.content.id, work.title.text,zone,work.troveUrl.text)
                items.append(cache)

        return items



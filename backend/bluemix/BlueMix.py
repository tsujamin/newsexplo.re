# -*- coding: utf-8 -*-
#
#   Copyright (C) 2016 Andrew Donnellan, Benjamin Roberts
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from backend.settings import BLUEMIX_KEY
from backend.orm import db_context as _db
import requests


BLUEMIX_URL = "https://gateway-a.watsonplatform.net/calls/url/URLGetCombinedData"
BLUEMIX_CATEGORIES = ["entities", "keywords"]


if BLUEMIX_KEY is None:
    raise ImportError("can't load Bluemix module without BLUEMIX_KEY")


class BlueMixAdapter:
    """
    Responsible for bluemix entity analysis of Article content for generating graph edges
    """

    def __init__(self, abc_article_content, session=_db):
        self.content = abc_article_content
        self.session = session
        self.args = {
            "apikey": BLUEMIX_KEY,
            "outputMode": "json",
            "extract": ",".join(BLUEMIX_CATEGORIES)
        }

        # bail out on non-articles
        if self.content.docType != "Article":
            raise ValueError("Tried to bluemix a document that wasn't an article")

    def __query_bluemix__(self):
        abc_url = self.content.get_data()["canonicalUrl"] if "canonicalUrl" in self.content.get_data() else None

        if abc_url is None:
            return None

        # Build query params
        query_params = {}
        for k,v in self.args.items():
            query_params[k] = v

        query_params["url"] = abc_url

        response = requests.get(BLUEMIX_URL, params=query_params)

        if(response.status_code is not 200):
            return None

        response = response.json()


        # Keep the 3 most relevant from each request
        results = {category: [] for category in BLUEMIX_CATEGORIES}

        for category in BLUEMIX_CATEGORIES:
            for entity in response[category][:min(3, len(response[category]) - 1 )]:
                results[category].append(entity["text"])

        return results

    def query_and_add_bluemix(self, session=_db.session, commit=False):
        from backend.orm.models import Content, Adjacency, BlueMixCache

        session.merge(BlueMixCache(self.content.id))
        results = self.__query_bluemix__()

        if results is None:
            return

        for category in BLUEMIX_CATEGORIES:
            items = results[category]
            for item in items:
                # Check for existing content item
                content_object = Content.query.filter_by(title=item).limit(1).first()

                # Add if it doesn't exist yet
                if content_object is None:
                    content_object = Content(Content.next_fake_id(), fake_content=True, docType="subject", title=item)
                    session.add(content_object)

                # Add adjacency if required
                session.merge(Adjacency(content_object.id, self.content.id, "subject"))

        if commit:
            session.commit()

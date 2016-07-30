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

from . import db_context
import requests
import json

ABC_API_URL = "https://content-api-govhack.abc-prod.net.au/v1/{}"

_db = db_context


class Content(_db.Model):
    __tablename__ = "content"

    id = _db.Column(_db.Integer, primary_key=True)
    docType = _db.Column( _db.String)
    title = _db.Column(_db.String)
    json = _db.Column(_db.String)

    def __init__(self, _id):
        """Initialise a new Content object, populate it's fields from the ABC API, save any adjacent nodes and commit"""
        self.id = _id
        self._populate_from_abc()

        _db.session.add(self)
        _db.session.commit()

    def _populate_from_abc(self):
        """populates the Content instance's fields from the ABC api
        :returns: true if population was successful
        """
        response = requests.get(ABC_API_URL.format(self.id))

        if response.status_code is not 200:
            raise LookupError("{} does not exist in ABC API".format(self.id))

        self.json_obj = response.json()

        if not ("docType" in self.json_obj and "title" in self.json_obj):
            raise KeyError("{} does not contain all of docType and title")

        self.docType = self.json_obj["docType"]
        self.title = self.json_obj["title"]
        self.json = response.content

    def get_data(self):
        """
        Get the cached dumped json object. Note changes to this are not reflected in the database
        :return: json object
        """
        if "json_obj" not in self.__dict__:
            self.json_obj = json.loads(self.json)

        return self.json_obj


class Adjacency(_db.Model):
    __tablename__ = "adjacency"

    from_node = _db.Column(_db.Integer, primary_key=True)
    to_node = _db.Column(_db.Integer, primary_key=True)


if len(_db.engine.table_names()) is 0:
    _db.create_all()
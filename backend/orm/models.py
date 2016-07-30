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

from backend.orm import db_context
import requests
import json
from sqlalchemy import exists

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
        self.id = int(_id)

        self._populate_from_abc()

        if not self.exists():
            _db.session.add(self)

        self._populate_adjacencies()

        _db.session.commit()

    def exists(self):
        """returns whether object already exists in database"""
        res = Content.query.filter_by(id=self.id).limit(1).first()
        return res is not None

    def _populate_from_abc(self):
        """populates the Content instance's fields from the ABC api
        :returns: true if population was successful
        """
        response = requests.get(ABC_API_URL.format(self.id))

        if response.status_code is not 200:
            _db.session.rollback()
            raise LookupError("{} does not exist in ABC API".format(self.id))

        self.json_obj = response.json()

        if not ("docType" in self.json_obj and "title" in self.json_obj):
            _db.session.rollback()
            raise KeyError("{} does not contain all of docType and title".format(self.id))

        self.docType = self.json_obj["docType"]
        self.title = self.json_obj["title"]
        self.json = json.dumps(self.json_obj)

    def _populate_adjacencies(self):
        """

        :return:
        """
        adjacent_set = set()
        json_obj = self.get_data()

        # Collate adjacent items
        if "relatedItems" in json_obj:
            for related_item in json_obj["relatedItems"]:
                if "id" not in related_item:
                    _db.session.rollback()
                    raise KeyError("{} does not contain id".format(related_item))

                adjacent_set.add((self.id, int(related_item['id']), "related"))

        if "subject" in json_obj:
            for subject in json_obj["subject"]:
                adjacent_set = adjacent_set.union(Content.collate_nested_relationships( self.id,
                                                                                        "subject",
                                                                                        subject))
        if "location" in json_obj:
            for location in json_obj["location"]:
                adjacent_set = adjacent_set.union(Content.collate_nested_relationships( self.id,
                                                                                        "location",
                                                                                        location))
        for (to_node, from_node, relationship) in adjacent_set:
            adjacency = Adjacency(from_node, to_node, relationship)
            if not adjacency.exists():
                _db.session.add(adjacency)

    @staticmethod
    def collate_nested_relationships(child, relationship, object):
        adjacent_set = set()
        if "id" not in object:
            return adjacent_set

        id = int(object["id"])

        adjacent_set.add((child, id, relationship))

        if "parent" in object:
            if type(object["parent"]) is list:
                for parent in object["parent"]:
                    adjacent_set = adjacent_set.union(Content.collate_nested_relationships(id,
                                                                                           relationship,
                                                                                           parent))
            else:
                adjacent_set = adjacent_set.union(Content.collate_nested_relationships( id,
                                                                                        relationship,
                                                                                        object["parent"]))

        return adjacent_set

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
    relationship = _db.Column(_db.String) #"related", "subject", "location"

    def __init__(self, _from_node, _to_node, _relationship):
        self.from_node = _from_node
        self.to_node = _to_node,
        self.relationship = _relationship

    def exists(self):
        """checks if adjacency is already in database"""
        ret = Adjacency.query.filter_by(from_node=self.from_node).filter_by(to_node=self.to_node).limit(1).first()
        return ret is not None

if len(_db.engine.table_names()) is 0:
    _db.create_all()

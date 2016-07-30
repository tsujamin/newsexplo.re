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

_db = db_context


class Content(_db.Model):
    __tablename__ = "content"

    id = _db.Column(_db.Integer, primary_key=True)
    docType = _db.Column( _db.String)
    title = _db.Column(_db.String)
    json = _db.Column(_db.String)


class Adjacency(_db.Model):
    __tablename__ = "adjacency"

    from_node = _db.Column(_db.Integer, primary_key=True)
    to_node = _db.Column(_db.Integer, primary_key=True)


if len(_db.engine.table_names()) is 0:
    _db.create_all()
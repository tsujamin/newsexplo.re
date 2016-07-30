#!/usr/bin/env python3

# api.py - main application

# Copyright (C) 2016 Benjamin Roberts, Andrew Donnellan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import jsonify
from sqlalchemy import or_
from backend import app
from backend.orm.models import Content, Adjacency
from backend.orm import db_context

@app.route('/api/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/content/abc/<int:content_id>')
def content_abc(content_id):
    content = Content(content_id)
    return jsonify(content.get_data()) # TODO inefficient

@app.route('/api/adjacency/<int:from_id>')
def get_adjacency(from_id):
    content = Content.get_or_create(from_id)
    adjacencies = db_context.session.query(Adjacency).filter(
        or_(Adjacency.from_node==from_id, Adjacency.to_node==from_id)).all()
    print(adjacencies)
    result = {'id': from_id, 'docType': content.docType, 'title': content.title}
    result['adjacent_nodes'] = []
    for adjacency in adjacencies:
        try:
            if adjacency.from_node == from_id:
                new_node = Content.get_or_create(adjacency.to_node)
            else:
                new_node = Content.get_or_create(adjacency.from_node)

                result['adjacent_nodes'].append(
                    {'id': new_node.id,
                     'docType': new_node.docType,
                     'title':new_node.title
                    })
        except:
            continue

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1")

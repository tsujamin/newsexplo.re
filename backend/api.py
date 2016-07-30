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

from flask import jsonify, Response, abort
from backend import app
from backend.orm.models import Content, Adjacency
from backend.settings import *

@app.route('/api/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/content/abc/<int:content_id>')
def content_abc(content_id):
    try:
        content = Content.get_or_create(content_id)
    except:
        abort(404)

    return Response(content.json, mimetype="application/json")

@app.route('/api/adjacency/<int:from_id>')
def get_adjacency(from_id):
    try:
        content = Content.get_or_create(from_id)
    except:
        # we only catch 404 here as later Content calls only refer to existing instances
        abort(404)

    adjacencies = content.get_adjacency_sample(BACKEND_ADJACENCY_QUERY_LIMIT)
    result = {'id': from_id, 'docType': content.docType, 'title': content.title}
    result['adjacent_nodes'] = []
    for adjacency in adjacencies:
        if adjacency.from_node == from_id:
            new_node = Content.get_or_create(adjacency.to_node)
        else:
            new_node = Content.get_or_create(adjacency.from_node)

        result['adjacent_nodes'].append(
            {'id': new_node.id,
             'docType': new_node.docType,
             'title':new_node.title
            })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1")

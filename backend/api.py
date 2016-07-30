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

import requests
import json
from flask import jsonify, Response, abort, request, stream_with_context
from backend import app
from backend.orm.models import Content, JustIn
from backend.settings import *

@app.route('/api/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/content/abc/imageproxy/<int:content_id>')
def content_abc_imageproxy(content_id):
    try:
        content = Content.get_or_create(content_id)
    except:
        abort(404)

    if content.docType != "Image" and content.docType != "ImageProxy":
        abort(400)

    try:
        obj = json.loads(content.json)
        url = obj['media'][0]['url']
    except:
        abort(500)

    req = requests.get(url, stream = True)
    return Response(stream_with_context(req.iter_content()),
                    content_type = req.headers['content-type'])

@app.route('/api/content/abc/<int:content_id>')
def content_abc(content_id):
    try:
        content = Content.get_or_create(content_id)
    except:
        abort(404)

    return Response(content.json, mimetype="application/json")

@app.route('/api/content/abc_just_in/')
def content_abc_just_in():
    limit = request.args["limit"] if "limit" in request.args else BACKEND_JUST_IN_QUERY_LIMIT

    return jsonify([content.json for content in JustIn.get_most_recent(limit)])

@app.route('/api/adjacency/<int:from_id>')
def get_adjacency(from_id):
    try:
        content = Content.get_or_create(from_id)
    except:
        # we only catch 404 here as later Content calls only refer to existing instances
        abort(404)

    #params for get_adjacency_sample
    adj_limit = int(request.args["limit"]) if "limit" in request.args else BACKEND_ADJACENCY_QUERY_LIMIT
    adj_doctype = request.args["docType"] if "docType" in request.args else None

    adjacencies = content.get_adjacency_sample(limit=adj_limit, docType=adj_doctype)

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

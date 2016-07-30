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
from . import app
from .orm.models import Content

@app.route('/api/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/content/abc/<int:content_id>')
def content_abc(content_id):
    content = Content(content_id)
    return jsonify(content.get_data()) # TODO inefficient

@app.route('/api/adjacency/<int:from_id>')
def get_adjacency(from_id):
    return jsonify({'apple': 57})

if __name__ == "__main__":
    app.run(host="127.0.0.1")

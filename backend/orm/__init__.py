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

from flask_sqlalchemy import SQLAlchemy
from backend import app

from backend.settings import *

def db_connect():
    '''Connects to the postgres backend'''
    if SQLALCHEMY_PASSWORD is None:
        url = "postgresql://{}@{}:{}/{}".format(SQLALCHEMY_USER, SQLALCHEMY_HOST, SQLALCHEMY_PORT, SQLALCHEMY_DATABASE)
    else:
        url = "postgresql://{}:{}@{}:{}/{}".format(SQLALCHEMY_USER, SQLALCHEMY_PASSWORD, SQLALCHEMY_PORT,
                                                   SQLALCHEMY_DATABASE)

    app.config['SQLALCHEMY_DATABASE_URI'] = url
    app.config['SQLALCHEMY_ECHO'] = True

    return SQLAlchemy(app)

db_context = db_connect()

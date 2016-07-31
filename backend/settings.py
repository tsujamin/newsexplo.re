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
from os import environ


def __from_env_or_default(key, default):
    """
    Check the environment for variable or return default
    :param key: variable to get
    :type: str
    :param default: default value if missing
    :return: value

    """
    if key in environ:
        return environ[key]
    else:
        return default

"""Application configuration variables"""
SQLALCHEMY_USER     = __from_env_or_default("SQLALCHEMY_USER", "govhack")
SQLALCHEMY_DATABASE = __from_env_or_default("SQLALCHEMY_DATABASE", "govhack2016")
SQLALCHEMY_PASSWORD = __from_env_or_default("SQLALCHEMY_PASSWORD", None)
SQLALCHEMY_HOST     = __from_env_or_default("SQLALCHEMY_HOST", "127.0.0.1")
SQLALCHEMY_PORT     = int(__from_env_or_default("SQLALCHEMY_PORT", 5432))

BACKEND_ADJACENCY_QUERY_LIMIT   = int(__from_env_or_default("BACKEND_ADJACENCY_QUERY_LIMIT", 20))
BACKEND_JUST_IN_QUERY_LIMIT     = int(__from_env_or_default("BACKEND_JUST_IN_QUERY_LIMIT", 10))

TROVE_KEY   = __from_env_or_default("TROVE_KEY", None)
BLUEMIX_KEY = __from_env_or_default("BLUEMIX_KEY", None)
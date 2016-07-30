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
from backend.orm.models import JustIn, Content
from datetime import datetime
import feedparser

_db = db_context
FEED_JUSTIN_URL = "http://www.abc.net.au/news/feed/51120/rss.xml"
STRPTIME_FORMAT = "%a, %d %b %Y %H:%M:%S %z"


def update_just_in(print_progress=False):
    """
    Queries the JustIn RSS feed and updates the database
    """
    if print_progress: print("downloading new feed")
    items = download_feed()

    if items is None:
        if print_progress: print("failed to download feed")
        return

    if print_progress: print("updating justin and content tables")
    for item in items:
        # query the content object to build adjacencies etc
        try:
            Content.get_or_create(item.id)
            _db.session.merge(item)
        except LookupError:
            pass

    if print_progress: print("commiting changes")
    _db.session.commit()


def download_feed():
    items = []

    feed = feedparser.parse(FEED_JUSTIN_URL)

    if feed is None:
        return None

    for entry in feed["entries"]:
        _id = int(entry["link"].split("/")[-1])
        items.append(JustIn(_id, datetime.strptime(entry["published"], STRPTIME_FORMAT)))

    return items


if __name__ == '__main__':
    update_just_in(print_progress=True)
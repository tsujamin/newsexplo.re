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
import fileinput
import argparse
import requests

DEFAULT_URL = "https://newsexplo.re/api/"
DEFAULT_INFILE = None


def main():
    args = parse_arguments()
    if args["in"] is None:
        read_function = fileinput.input
    else:
        f = open(args["in"], "r")
        read_function = lambda: f

    for abc_id in read_function():
        print(abc_id.strip())
        requests.get(args["url"] + "content/abc/" + abc_id.strip())


def parse_arguments():
    """
    parses the command line arguments
    :return: dictionary containing the arguments
    :rtype: dict
    """

    parser = argparse.ArgumentParser(description="farms abc documentIDs for their govhack API")
    parser.add_argument("--in", default=DEFAULT_INFILE, help="read ids from file")
    parser.add_argument("--url", default=DEFAULT_URL, help="url of api")

    return vars(parser.parse_args())



if __name__ == '__main__':
    main()

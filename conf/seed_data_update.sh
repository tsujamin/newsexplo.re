#!/bin/sh
pushd /srv/newsexplo.re
source bin/activate
python3 preprocessing/gather_abc_ids.py | python3 preprocessing/query_seed_data.py | sort -n -r -u > preprocessing/ids.txt
popd

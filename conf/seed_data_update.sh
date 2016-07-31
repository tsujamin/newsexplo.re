#!/bin/sh
pushd /srv/newsexplo.re
for line in `cat conf/environment`; do
	eval "export "$line
done
source bin/activate
python3 preprocessing/gather_abc_ids.py | python3 preprocessing/query_seed_data.py | sort -n -r -u > preprocessing/ids.txt
popd

#!/bin/sh
pushd /srv/newsexplo.re
for line in `cat conf/environment`; do
	eval "export "$line
done
source bin/activate
python3 -m backend.abc_live.just_in
popd

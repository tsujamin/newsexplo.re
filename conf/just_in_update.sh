#!/bin/sh
pushd /srv/newsexplo.re
source bin/activate
python3 -m backend.abc_live.just_in
popd

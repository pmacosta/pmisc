#!/bin/bash
# ipath.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

sdir=$(dirname "${BASH_SOURCE[0]}")
# shellcheck disable=SC1090,SC1091
source "${sdir}/functions.sh"
IFS=" ", read -r -a pyvers <<< "$(get_pyvers)"
for pyver in ${pyvers[*]}; do
    pdir="${HOME}/python/python${pyver}/bin"
    if [ -d "${pdir}" ]; then
        export PATH=${pdir}:${PATH}
    fi
done

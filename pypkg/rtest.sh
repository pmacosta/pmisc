#!/bin/bash
# rtest.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

sdir=$(dirname "${BASH_SOURCE[0]}")
# shellcheck disable=SC1090,SC1091,SC2024
source "${sdir}/functions.sh"
opath=${PATH}
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
finish() {
    export PATH=${opath}
}
trap finish EXIT ERR SIGINT
cmd=$(strcat\
    "from __future__ import print_function;" \
    "import multiprocessing;" \
    "print(multiprocessing.cpu_count())" \
)
num_cpus=$(python -c "${cmd}")
IFS=" ", read -r -a pyvers <<< "$(get_pyvers)"
for pyver in ${pyvers[*]}; do
    pdir="${HOME}/python/python${pyver}/bin"
    if [ -d "${pdir}" ]; then
        export PATH=${pdir}:${PATH}
    fi
done
# shellcheck disable=SC2068
PKG_NAME="$(basename "$(dirname "$(readlink -f "${sdir}")")")" tox -- -n "${num_cpus}" $@

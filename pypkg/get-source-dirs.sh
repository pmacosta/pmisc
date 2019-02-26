#!/bin/bash
# get-source-dirs.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

sdir=$(dirname "${BASH_SOURCE[0]}")
# shellcheck disable=SC1090,SC1091,SC2024
source "${sdir}/functions.sh"
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
#
add_to_output() {
    local ret addition
    ret="$1"
    addition="$2"
    if [ "${ret}" != "" ]; then
        ret="${ret} "
    fi
    ret="${ret}${addition}"
    echo "${ret}"
}
repo_dir=$(readlink -f "$1")
source_dir=$(readlink -f "$2")
extra_dir=$(readlink -f "$3")
#
ret=""
if ls "${repo_dir}"/*.py &> /dev/null; then
    ret="$(add_to_output "${ret}" "${repo_dir}/*.py")"
fi
dnames="$(find "${source_dir}" -name "*.py" -printf '%h\n' | sort -u)"
for dname in ${dnames[*]}; do
    ret="$(add_to_output "${ret}" "${dname}")"
done
dnames="$(find "${extra_dir}/tests" -name "*.py" -printf '%h\n' | sort -u)"
for dname in ${dnames[*]}; do
    ret="$(add_to_output "${ret}" "${dname}")"
done
dnames="$(find "${extra_dir}/docs" -name "*.py" -printf '%h\n' | sort -u)"
for dname in ${dnames[*]}; do
    ret="$(add_to_output "${ret}" "${dname}")"
done
echo "${ret}"

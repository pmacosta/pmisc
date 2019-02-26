#!/bin/bash
# make-wheels.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

sdir=$(dirname "${BASH_SOURCE[0]}")
# shellcheck disable=SC1090,SC1091,SC2024
source "${sdir}/functions.sh"
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
#
cwd=${PWD}
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
sbin_dir=${pkg_dir}/pypkg
finish() {
    if [ -f "${pkg_dir}"/setup.py.tmp ]; then
        mv -f "${pkg_dir}"/setup.py.tmp "${pkg_dir}"/setup.py
    fi
    if [ -f "${pkg_dir}"/MANIFEST.in.tmp ]; then
        mv "${pkg_dir}"/MANIFEST.in.tmp "${pkg_dir}"/MANIFEST.in
    fi
    cd "${cwd}" || exit 1
}
trap finish EXIT ERR SIGINT

echo "pkg_dir: ${pkg_dir}"
echo "sbin_dir: ${sbin_dir}"
cd "${pkg_dir}" || exit 1
cp "${pkg_dir}"/MANIFEST.in "${pkg_dir}"/MANIFEST.in.tmp
cd "${sbin_dir}" || exit 1
./gen_pkg_manifest.py wheel
cp -f "${pkg_dir}"/setup.py "${pkg_dir}"/setup.py.tmp
sed -r -i 's/data_files=DATA_FILES,/data_files=None,/g' "${pkg_dir}"/setup.py
IFS=" ", read -r -a pyvers <<< "$(get_pyvers)"
cd "${pkg_dir}" || exit 1
for pyver in ${pyvers[*]}; do
    "${sbin_dir}/cprint.sh" line cyan "Building Python ${pyver} wheel"
    "${HOME}/python/python${pyver}/bin/python${pyver}" \
        setup.py bdist_wheel --python-tag "py${pyver/./}"
done

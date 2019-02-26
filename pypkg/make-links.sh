#!/bin/bash
# make-links.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

sdir=$(dirname "${BASH_SOURCE[0]}")
# shellcheck disable=SC1090,SC1091,SC2024
source "${sdir}/functions.sh"
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
#
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
sbin_dir=${pkg_dir}/pypkg
finish() { : ; }
trap finish EXIT ERR SIGINT

echo "pkg_dir: ${pkg_dir}"
echo "sbin_dir: ${sbin_dir}"
fnames=( \
    .pre-commit-config.yaml \
    .pydocstyle \
    .pylintrc \
    .hooks/pre-commit \
    .hooks/setup-git-hooks.sh \
    Makefile \
    azure-pipelines.yml \
    setup.py \
    tox.ini \
)
for fname in ${fnames[*]}; do
    echo "Linking ${fname}"
    ln -sf "${sbin_dir}/${fname}" "${pkg_dir}/${fname}"
done

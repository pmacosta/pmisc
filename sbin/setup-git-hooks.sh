#!/bin/bash
# setup-git-hooks.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details

# shellcheck disable=SC1090,SC1091
source" $(dirname "${BASH_SOURCE[0]}")/functions.sh"

pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
# shellcheck disable=SC1090,SC1091
source "${pkg_dir}/.hooks/setup-git-hooks.sh"

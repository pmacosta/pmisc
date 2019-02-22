#!/bin/bash
# complete-cloning.sh
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
#
#/ complete-cloning.sh
#/ Usage:
#/   complete-cloning.sh -h
#/   complete-cloning.sh -e -v [VERSION] -d [DIRECTORY]
#/ Options:
#/   -h  show this help message and exit
#/   -e  enforce e-mail check when Git pushing

# shellcheck disable=SC1090,SC1091
source "$(dirname "${BASH_SOURCE[0]}")/functions.sh"
sname=$(basename "$0")
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
### Cleanup
finish() { : ; }
trap finish EXIT ERR SIGINT
### Help message
usage() { grep '^#/' "$0" | cut -c4- ; }
#
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
bin_dir=${pkg_dir}/sbin

check_email=0
# Read command line options
while getopts ":he" opt; do
	case ${opt} in
		h)
			usage
			exit 0
			;;
		e)
			check_email=1
			;;
		\?)
			echo -e "${sname}: invalid option -${OPTARG}\n" >&2
			usage
			exit 1
			;;
	esac
done
shift $((OPTIND - 1))

# Set up pre-commit Git hooks
echo "Installing Git hooks"
# shellcheck disable=SC1090,SC1091
source "${bin_dir}/setup-git-hooks.sh"
msg=$(strcat \
    "#!/bin/bash\n" \
    "# shellcheck disable=SC2034\n" \
    "print=0\n" \
    "non_ascii_file_names=1\n" \
    "trailing_white_space=1\n" \
    "pep8=1\n" \
    "pep257=1\n" \
    "email=${check_email}\n" \
    "personal_repo=1\n" \
    "code_standard=1\n" \
)
mkdir -p .hooks
echo -e "${msg}" > "${pkg_dir}/.hooks/repo-cfg.sh"

# Build documentation
script="${bin_dir}/build_docs.py"
if [ -f "${script}" ]; then
    tox -e py27-repl -- "${script}"
fi

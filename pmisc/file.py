# file.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os
import platform


###
# Functions
###
def make_dir(fname):
    """
    Creates the directory of a fully qualified file name if it does not exist

    :param fname: File name
    :type  fname: string

    Equivalent to these Bash shell commands:

    .. code-block:: bash

        $ dir=$(dirname ${fname})
        $ mkdir -p ${dir}

    :param fname: Fully qualified file name
    :type  fname: string
    """
    file_path, fname = os.path.split(os.path.abspath(fname))
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def normalize_windows_fname(fname, _force=False):
    """
    Fix potential problems with a Microsoft Windows file name. Superfluous
    backslashes are removed and unintended escape sequences are converted
    to their equivalent (presumably correct and intended) representation,
    for example :code:`r'\\\\x07pps'` is transformed to
    :code:`r'\\\\\\\\apps'`. A file name is considered network shares if
    the file does not include a drive letter and they start with a double
    backslash (:code:`'\\\\\\\\'`)

    :param fname: File name
    :type  fname: string

    :rtype: string
    """
    if ((platform.system().lower() != 'windows')
       and (not _force)):   # pragma: no cover
        return fname
    # Replace unintended escape sequences that could be in
    # the file name, like "C:\appdata"
    rchars = {
        '\x07': r'\\a',
        '\x08': r'\\b',
        '\x0C': r'\\f',
        '\x0A': r'\\n',
        '\x0D': r'\\r',
        '\x09': r'\\t',
        '\x0B': r'\\v',
    }
    ret = ''
    for char in os.path.normpath(fname):
        ret = ret+rchars.get(char, char)
    # Remove superfluous double backslashes
    network_share = False
    tmp = None
    network_share = fname.startswith(r'\\')
    while tmp != ret:
        tmp, ret = ret, ret.replace(r'\\\\', r'\\')
    ret = ret.replace(r'\\\\', r'\\')
    # Put back network share if needed
    if network_share:
        ret = r'\\'+ret.lstrip(r'\\')
    return ret

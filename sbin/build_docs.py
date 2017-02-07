#!/usr/bin/env python
# build_docs.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,F0401,R0914,W0141

# Standard library imports
from __future__ import print_function
import argparse
import os
import re
import shutil
import sys
# PyPI imports
from cogapp import Cog
# Intra-package imports
import sbin.functions

###
# Global variables
###
VALID_MODULES = ['pmisc']


###
# Functions
###
def build_pkg_docs(args):
    """ Build documentation """
    # pylint: disable=R0912,R0915
    debug = False
    retcode = 0
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = args.directory
    cog_exe = which('cog.py')
    if not cog_exe:
        raise RuntimeError('cog binary could not be found')
    tracer_dir = os.path.join(pkg_dir, 'docs', 'support')
    os.environ['TRACER_DIR'] = tracer_dir
    # Processing
    if debug:
        print('Python: {0}'.format(sys.executable))
        print('PATH: {0}'.format(os.environ['PATH']))
        print('PYTHONPATH: {0}'.format(os.environ['PYTHONPATH']))
        print('Cog: {0}'.format(cog_exe))
        print('sbin.functions: {0}'.format(sbin.functions.__file__))
        print(
            'sbin.functions.subprocess: {0}'.format(
                sbin.functions.subprocess.__file__
            )
        )
    print('Inserting files into docstrings')
    insert_files_in_docstrings(src_dir, cog_exe)
    insert_files_in_rsts(pkg_dir, cog_exe)
    generate_top_level_readme(pkg_dir)
    print('Generating HTML output')
    shutil.rmtree(os.path.join(pkg_dir, 'docs', '_build'), ignore_errors=True)
    cwd = os.getcwd()
    os.chdir(os.path.join(pkg_dir, 'docs'))
    sbin.functions.shcmd(
        [
            'sphinx-build',
            '-b', 'html',
            '-d', os.path.join('_build', 'doctrees'),
            '-W', '.',
            os.path.join('_build', 'html')
        ],
        'Error building Sphinx documentation',
        async_stdout=True
    )
    # Copy built documentation to its own directory
    # dest_dir = os.path.join(pkg_dir, 'docs', 'html')
    # src_dir = os.path.join(pkg_dir, 'docs', '_build', 'html')
    # shutil.rmtree(dest_dir, ignore_errors=True)
    # shutil.copytree(src_dir, dest_dir)
    os.chdir(cwd)
    return retcode


def copy_file(src, dest):
    """ Copy file (potentially overwriting existing file) """
    try:
        os.remove(dest)
    except OSError:
        pass
    shutil.copy(src, dest)


def del_file(fname):
    """ Delete file """
    try:
        os.remove(fname)
    except OSError:
        pass


def elapsed_time_string(start_time, stop_time):
    """
    Returns a formatted string with the elapsed time between two time points
    """
    delta_time = stop_time-start_time
    tot_seconds = int(
        (
            delta_time.microseconds+
            (delta_time.seconds+delta_time.days*24*3600)*10**6
        )
        /
        10**6
    )
    years, remainder = divmod(tot_seconds, 365*24*60*60)
    months, remainder = divmod(remainder, 30*24*60*60)
    days, remainder = divmod(remainder, 24*60*60)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)
    token_iter = zip(
        [years, months, days, hours, minutes, seconds],
        ['year', 'month', 'day', 'hour', 'minute', 'second']
    )
    ret_list = [
        '{token} {token_name}{plural}'.format(
            token=num,
            token_name=desc,
            plural='s' if num > 1 else ''
        ) for num, desc in token_iter if num > 0
    ]
    if len(ret_list) == 0:
        return 'None'
    elif len(ret_list) == 1:
        return ret_list[0]
    elif len(ret_list) == 2:
        return ret_list[0]+' and '+ret_list[1]
    else:
        return (', '.join(ret_list[0:-1]))+' and '+ret_list[-1]


def insert_files_in_docstrings(src_dir, cog_exe):
    """ Cog-insert source files in docstrings """
    modules = ['ctx']
    for module in modules:
        module_dir = src_dir
        submodules = [module]
        for submodule in submodules:
            smf = os.path.join(module_dir, submodule+'.py')
            print('   Processing module {0}'.format(smf))
            retcode = Cog().main(
                [
                    cog_exe,
                    "--markers==[=cog =]= =[=end=]=",
                    '-e', '-x', '-o', smf+'.tmp', smf
                ],
            )
            if retcode:
                raise RuntimeError(
			        'Error deleting insertion of source files in '
			        'docstrings in module {0}'.format(submodule)
                )
            retcode = Cog().main(
                [
                    cog_exe,
                    "--markers==[=cog =]= =[=end=]=",
                    '-e', '-o', smf+'.tmp', smf
                ]
            )
            if retcode:
                raise RuntimeError(
			        'Error inserting source files in '
			        'docstrings in module {0}'.format(submodule)
                )
            move_file(smf+'.tmp', smf)


def insert_files_in_rsts(pkg_dir, cog_exe):
    """ Cog-insert source files in Sphinx files """
    fnames = [
        os.path.join(pkg_dir, 'docs', 'README.rst'),
    ]
    print('Inserting source files in documentation files')
    for fname in fnames:
        print('   Processing file {0}'.format(fname))
        retcode = Cog().main(
            [
                cog_exe,
                '-e', '-x', '-o', fname+'.tmp', fname
            ]
        )
        if retcode:
            raise RuntimeError(
		        'Error deleting insertion of source files in '
		        'documentation file {0}'.format(fname)
            )
        retcode = Cog().main(
            [
                cog_exe,
                '-e', '-o', fname+'.tmp', fname
            ]
        )
        if retcode:
            raise RuntimeError(
		        'Error inserting source files in '
		        'docstrings in module {0}'.format(fname)
            )
        move_file(fname+'.tmp', fname)


def move_file(src, dest):
    """ Copy file (potentially overwriting existing file) """
    try:
        os.remove(dest)
    except OSError:
        pass
    shutil.move(src, dest)


def pcolor(text, color, indent=0):
    r"""
    Returns a string that once printed is colorized (copied from pmisc)

    :param text: Text to colorize
    :type  text: string

    :param  color: Color to use, one of :code:`'black'`, :code:`'red'`,
                   :code:`'green'`, :code:`'yellow'`, :code:`'blue'`,
                   :code:`'magenta'`, :code:`'cyan'`, :code:`'white'` or
                   :code:`'none'` (case insensitive)
    :type   color: string

    :param indent: Number of spaces to prefix the output with
    :type  indent: integer

    :rtype: string

    :raises:
     * RuntimeError (Argument \`color\` is not valid)

     * RuntimeError (Argument \`indent\` is not valid)

     * RuntimeError (Argument \`text\` is not valid)

     * ValueError (Unknown color *[color]*)
    """
    esc_dict = {
        'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35,
        'cyan':36, 'white':37, 'none':-1
    }
    if not isinstance(text, str):
        raise RuntimeError('Argument `text` is not valid')
    if not isinstance(color, str):
        raise RuntimeError('Argument `color` is not valid')
    if not isinstance(indent, int):
        raise RuntimeError('Argument `indent` is not valid')
    color = color.lower()
    if color not in esc_dict:
        raise ValueError('Unknown color {color}'.format(color=color))
    if esc_dict[color] != -1:
        return (
            '\033[{color_code}m{indent}{text}\033[0m'.format(
                color_code=esc_dict[color],
                indent=' '*indent,
                text=text
            )
        )
    return '{indent}{text}'.format(indent=' '*indent, text=text)


def print_cyan(text):
    """ Print text to STDOUT in cyan color """
    print(pcolor(text, 'cyan'))


def print_green(text):
    """ Print text to STDOUT in green color """
    print(pcolor(text, 'green'))


def print_red(text):
    """ Print text to STDOUT in red color """
    print(pcolor(text, 'red'))


def generate_top_level_readme(pkg_dir):
    """
    Remove Sphinx-specific cross-references from top-level README.rst file,
    they are not rendered by either Bitbucket or GitHub
    """
    # pylint: disable=W0212
    docs_dir = os.path.abspath(os.path.join(pkg_dir, 'docs'))
    fname = os.path.join(docs_dir, 'README.rst')
    print('Generating top-level README.rst file')
    with open(fname, 'r') as fobj:
        lines = [item.rstrip() for item in fobj.readlines()]
    ref_regexp = re.compile('.*:py:mod:`(.+) <pmisc.(.+)>`.*')
    rst_cmd_regexp = re.compile('^\\s*.. \\S+::.*')
    indent_regexp = re.compile('^(\\s*)\\S+')
    ret = []
    autofunction = False
    for line in lines:
        match = ref_regexp.match(line)
        if autofunction:
            match = indent_regexp.match(line)
            if (not match) or (match and len(match.group(1)) == 0):
                autofunction = False
                ret.append(line)
        elif match:
            # Remove cross-references
            label = match.group(1)
            mname = match.group(2)
            line = line.replace(
                ':py:mod:`{label} <pmisc.{mname}>`'.format(
                    label=label, mname=mname
                ),
                label
            )
            ret.append(line)
        elif line.lstrip().startswith('.. include::'):
            # Include files
            base_fname = line.split()[-1].strip()
            fname = os.path.basename(base_fname)
            # Do not include the change log, PyPI adds it at the end
            # of the README.rst file by default and in a hosted Git
            # repository there is a much more detailed built-in change
            # log in the commit message history
            if fname != 'CHANGELOG.rst':
                fname = os.path.join(docs_dir, base_fname)
                for inc_line in sbin.functions._readlines(fname):
                    comment = inc_line.lstrip().startswith('.. ')
                    if ((not comment)
                       or (comment and rst_cmd_regexp.match(inc_line))):
                        ret.append(inc_line.rstrip())
        elif line.lstrip().startswith('.. autofunction::'):
            # Remove auto-functions, PyPI reStructuredText parser
            # does not appear to like it
            autofunction = True
        else:
            ret.append(line)
    fname = os.path.join(pkg_dir, 'README.rst')
    with open(fname, 'w') as fobj:
        fobj.write('\n'.join(ret))
    # Check that generated file produces HTML version without errors
    sbin.functions.shcmd(
        ['rst2html.py', '--exit-status=3', fname],
        'Error validating top-level README.rst HTML conversion',
    )


def valid_dir(value):
    """ Argparse checked for directory argument """
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError(
            'directory {0} does not exist'.format(value)
        )
    return os.path.abspath(value)


def which(name):
    """ Search PATH for executable files with the given name """
    # Inspired by https://twistedmatrix.com/trac/browser/tags/releases/
    # twisted-8.2.0/twisted/python/procutils.py
    result = []
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for pdir in os.environ.get('PATH', '').split(os.pathsep):
        fname = os.path.join(pdir, name)
        if os.path.isfile(fname) and os.access(fname, os.X_OK):
            result.append(fname)
    return result[0] if result else None


if __name__ == "__main__":
    # pylint: disable=E0602
    # Remove -n from arguments
    if '-n' in sys.argv:
        IDX = sys.argv.index('-n')
        sys.argv = sys.argv[:IDX]+sys.argv[IDX+2:]
    PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PARSER = argparse.ArgumentParser(
        description='Build pmisc package documentation'
    )
    PARSER.add_argument(
        '-d', '--directory',
        help='specify source file directory (default ../pmisc)',
        type=valid_dir,
        nargs=1,
        default=[os.path.join(PKG_DIR, 'pmisc')]
    )
    ARGS = PARSER.parse_args()
    ARGS.directory = ARGS.directory[0]
    sys.exit(build_pkg_docs(ARGS))

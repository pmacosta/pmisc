# header.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import datetime
import os
import re

# PyPI imports
from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker


###
# Functions
###
def check_header(node):
    """Check that all files have header line and copyright notice."""
    # pylint: disable=W0702
    basename = os.path.basename(os.path.abspath(node.file))
    year = datetime.datetime.now().year
    header_lines = [
        re.compile("# {0}".format(basename)),
        re.compile(
            r"# Copyright \(c\) (?:{0}|(\d+)-{0}) Pablo Acosta-Serafini".format(year)
        ),
        re.compile("# See LICENSE for details"),
    ]
    with node.stream() as stream:
        for (num, line), ref in zip(content_lines(stream), header_lines):
            match = ref.match(line)
            if not match:
                return num
            groups = match.groups()
            if groups and groups[0]:
                try:
                    if int(groups[0]) >= year:
                        return num
                except:
                    return num
    return 0


def content_lines(stream, comment="#"):
    """Return non-empty lines of a package."""
    skip_lines = ["#!/bin/bash", "#!/usr/bin/env bash", "#!/usr/bin/env python"]
    encoding_dribble = "\xef\xbb\xbf"
    encoded = False
    cregexp = re.compile(r".*{0} -\*- coding: utf-8 -\*-\s*".format(comment))
    for num, line in enumerate(stream):
        line = line.decode().rstrip()
        if (not num) and line.startswith(encoding_dribble):
            line = line[len(encoding_dribble) :]
        coding_line = (num == 0) and (cregexp.match(line) is not None)
        encoded = coding_line if not encoded else encoded
        shebang_line = (num == int(encoded)) and (line in skip_lines)
        if line and (not coding_line) and (not shebang_line):
            yield num + 1, line


###
# Classes
###
class HeaderChecker(BaseChecker):
    """
    Check for header compliance.

    A compliant header includes the name of the file in the first usable line, and
    an up-to-date copyright notice.
    """

    __implements__ = IRawChecker

    NON_COMPLIANT_HEADER = "non-compliant-header"

    name = "header-compliance"
    msgs = {
        "W9900": (
            "Header does not meet code standard",
            NON_COMPLIANT_HEADER,
            (
                "Headers must have the name of th efile in the first usable line, "
                "and an up-to-date copyright notice"
            ),
        )
    }
    options = ()

    def process_module(self, node):
        """Process a module. Content is accessible via node.stream() function."""
        line = check_header(node)
        if line:
            self.add_message(self.NON_COMPLIANT_HEADER, line=line)


def register(linter):
    """Regiester checker."""
    linter.register_checker(HeaderChecker(linter))
.. api.rst
.. Copyright (c) 2013-2017 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: pmisc

###
API
###

****************
Context managers
****************

.. autofunction:: pmisc.ignored
.. autoclass:: pmisc.Timer
	:members: elapsed_time
	:show-inheritance:
.. autoclass:: pmisc.TmpDir
	:show-inheritance:
.. autoclass:: pmisc.TmpFile
	:show-inheritance:

****
File
****

.. autofunction:: pmisc.make_dir
.. autofunction:: pmisc.normalize_windows_fname

**********
Membership
**********

.. autofunction:: pmisc.isalpha
.. autofunction:: pmisc.ishex
.. autofunction:: pmisc.isiterable
.. autofunction:: pmisc.isnumber
.. autofunction:: pmisc.isreal

*************
Miscellaneous
*************

.. autofunction:: pmisc.flatten_list

*******
Numbers
*******

.. autofunction:: pmisc.gcd
.. autofunction:: pmisc.normalize
.. autofunction:: pmisc.per
.. autofunction:: pmisc.pgcd

****************
reStructuredText
****************

.. autofunction:: pmisc.incfile
.. autofunction:: pmisc.ste
.. autofunction:: pmisc.term_echo

*******
Strings
*******

.. autofunction:: pmisc.binary_string_to_octal_string
.. autofunction:: pmisc.char_to_decimal
.. autofunction:: pmisc.elapsed_time_string
.. autofunction:: pmisc.pcolor
.. autofunction:: pmisc.quote_str
.. autofunction:: pmisc.strframe

****
Test
****

.. autofunction:: pmisc.assert_arg_invalid
.. autofunction:: pmisc.assert_exception
.. autofunction:: pmisc.assert_prop
.. autofunction:: pmisc.assert_ro_prop
.. autofunction:: pmisc.compare_strings
.. autofunction:: pmisc.exception_type_str
.. autofunction:: pmisc.get_exmsg

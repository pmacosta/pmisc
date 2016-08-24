.. CHANGELOG.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details

Changelog
=========

* 1.1.5 [2016-08-24]: assert_exception now prints better message when actual
  exception is different than expected exception

* 1.1.4 [2016-08-06]: assert_exception now prints traceback when exception
  raised is different than expected exception

* 1.1.3 [2016-06-09]: assert_exception exception message is now not limited to
  just strings

* 1.1.2 [2016-06-01]: Fixed continuous integration failures in term_echo
  function testing

* 1.1.1 [2016-06-01]: Enhanced TmpFile context manager by allowing positional
  and keyword arguments to be passed to optional write function

* 1.1.0 [2016-05-15]: Added incfile, ste and term_echo functions. These produce
  output marked up in reStructuredText of source files (incfile) or terminal
  commands (ste, term_echo). All can be used to include relevant information in
  docstrings to enhance documentation

* 1.0.5 [2016-05-13]: Minor documentation update

* 1.0.4 [2016-05-02]: Minor documentation and testing enhancements

* 1.0.3 [2016-04-26]: Dependencies fixes

* 1.0.2 [2016-04-26]: Windows continuous integration fixes

* 1.0.1 [2016-04-26]: Removed dependency on Numpy

* 1.0.0 [2016-04-23]: Final release of 1.0.0 branch

* 1.0.0rc1 [2016-04-22]: Initial commit, merges misc and test modules of putil
  PyPI package

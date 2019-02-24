.. README.rst
.. Copyright (c) 2013-2019 Pablo Acosta-Serafini
.. See LICENSE for details

.. image:: https://badge.fury.io/py/pmisc.svg
    :target: https://pypi.org/project/pmisc
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/pmisc.svg
    :target: https://pypi.org/project/pmisc
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pmisc.svg
    :target: https://pypi.org/project/pmisc
    :alt: Python versions supported

.. image:: https://img.shields.io/pypi/format/pmisc.svg
    :target: https://pypi.org/project/pmisc
    :alt: Format

|

.. image::
    https://dev.azure.com/pmasdev/pmisc/_apis/build/status/pmacosta.pmisc?branchName=master
    :target: https://dev.azure.com/pmasdev/pmisc/_build?definitionId=3&_a=summary
    :alt: Continuous integration test status

.. image::
    https://img.shields.io/azure-devops/coverage/pmasdev/pmisc/3.svg
    :target: https://dev.azure.com/pmasdev/pmisc/_build?definitionId=3&_a=summary
    :alt: Continuous integration test coverage

.. image::
    https://readthedocs.org/projects/pip/badge/?version=stable
    :target: https://pip.readthedocs.io/en/stable/?badge=stable
    :alt: Documentation status

|

Description
===========

.. role:: bash(code)
	:language: bash

.. [[[cog
.. import os, sys, pmisc, docs.support.requirements_to_rst
.. file_name = sys.modules['docs.support.requirements_to_rst'].__file__
.. mdir = os.path.join(os.path.realpath(
..    os.path.dirname(os.path.dirname(os.path.dirname(file_name)))), 'sbin'
.. )
.. docs.support.requirements_to_rst.def_links(cog)
.. ]]]
.. _Astroid: https://bitbucket.org/logilab/astroid
.. _Cog: https://nedbatchelder.com/code/cog
.. _Coverage: https://coverage.readthedocs.io
.. _Decorator: https://decorator.readthedocs.io
.. _Docutils: http://docutils.sourceforge.net/docs
.. _Funcsigs: https://pypi.org/project/funcsigs
.. _Mock: https://docs.python.org/3/library/unittest.mock.html
.. _Numpy: http://www.numpy.org
.. _Pylint: https://www.pylint.org
.. _Py.test: http://pytest.org
.. _Pytest-coverage: https://pypi.org/project/pytest-cov
.. _Pytest-xdist: https://pypi.org/project/pytest-xdist
.. _Sphinx: http://sphinx-doc.org
.. _ReadTheDocs Sphinx theme: https://github.com/rtfd/sphinx_rtd_theme
.. _Inline Syntax Highlight Sphinx Extension:
   https://bitbucket.org/klorenz/sphinxcontrib-inlinesyntaxhighlight
.. _Shellcheck Linter Sphinx Extension:
   https://pypi.org/project/sphinxcontrib-shellcheck
.. _Tox: https://tox.readthedocs.io
.. _Virtualenv: https://docs.python-guide.org/dev/virtualenvs
.. [[[end]]]

This module contains miscellaneous utility functions that can be applied in a
variety of circumstances; there are context managers, membership functions
(test if an argument is of a given type), numerical functions, string
functions and functions to aid in the unit testing of modules

`Py.test`_ is the supported test runner

Interpreter
===========

The package has been developed and tested with Python 2.7, 3.5, 3.6 and 3.7
under Linux (Debian, Ubuntu), Apple macOS and Microsoft Windows

Installing
==========

.. code-block:: bash

	$ pip install pmisc

Documentation
=============

Available at `Read the Docs <https://pmisc.readthedocs.io>`_

Contributing
============

1. Abide by the adopted `code of conduct
   <https://www.contributor-covenant.org/version/1/4/code-of-conduct>`_

2. Fork the `repository <https://github.com/pmacosta/pmisc>`_ from
   GitHub and then clone personal copy [#f1]_:

    .. code-block:: bash

        $ github_user=myname
        $ git clone \
              https://github.com/"${github_user}"/pmisc.git
        Cloning into 'pmisc'...
        ...
        $ cd pmisc
        $ export PMISC_DIR=${PWD}

3. Install the project's Git hooks and build the documentation. The pre-commit
   hook does some minor consistency checks, namely trailing whitespace and
   `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance via
   Pylint. Assuming the directory to which the repository was cloned is
   in the :bash:`$PMISC_DIR` shell environment variable:

	.. code-block:: bash

		$ "${PMISC_DIR}"/sbin/complete-cloning.sh
                Installing Git hooks
                Building pmisc package documentation
                ...

4. Ensure that the Python interpreter can find the package modules
   (update the :bash:`$PYTHONPATH` environment variable, or use
   `sys.paths() <https://docs.python.org/3/library/sys.html#sys.path>`_,
   etc.)

	.. code-block:: bash

		$ export PYTHONPATH=${PYTHONPATH}:${PMISC_DIR}

5. Install the dependencies (if needed, done automatically by pip):

    .. [[[cog
    .. import docs.support.requirements_to_rst
    .. docs.support.requirements_to_rst.proc_requirements(cog)
    .. ]]]


    * `Astroid`_ (1.6.0 or newer)

    * `Cog`_ (2.5.1 or newer)

    * `Coverage`_ (4.4.2 or newer)

    * `Decorator`_ (4.2.1 or newer)

    * `Docutils`_ (0.14 or newer)

    * `Funcsigs`_ (1.0.2 or newer)

    * `Inline Syntax Highlight Sphinx Extension`_ (0.2 or newer)

    * `Mock`_ (2.0.0 or newer)

    * `Numpy`_ (1.8.2 or newer)

    * `Py.test`_ (3.4.0 or newer)

    * `Pylint`_ (1.8.1 or newer)

    * `Pytest-coverage`_ (2.5.1 or newer)

    * `Pytest-xdist`_ (optional, 1.22.0 or newer)

    * `ReadTheDocs Sphinx theme`_ (0.1.9 or newer)

    * `Shellcheck Linter Sphinx Extension`_ (1.0.5 or newer)

    * `Sphinx`_ (1.6.6 or newer)

    * `Tox`_ (2.9.1 or newer)

    * `Virtualenv`_ (15.1.0 or newer)

    .. [[[end]]]

6. Implement a new feature or fix a bug

7. Write a unit test which shows that the contributed code works as expected.
   Run the package tests to ensure that the bug fix or new feature does not
   have adverse side effects. If possible achieve 100% code and branch
   coverage of the contribution. Thorough package validation
   can be done via Tox and Py.test:

	.. code-block:: bash

            $ tox
            GLOB sdist-make: .../pmisc/setup.py
            py26-pkg inst-nodeps: .../pmisc/.tox/dist/pmisc-...zip

   `Setuptools <https://bitbucket.org/pypa/setuptools>`_ can also be used
   (Tox is configured as its virtual environment manager):

	.. code-block:: bash

	    $ python setup.py tests
            running tests
            running egg_info
            writing requirements to pmisc.egg-info/requires.txt
            writing pmisc.egg-info/PKG-INFO
            ...

   Tox (or Setuptools via Tox) runs with the following default environments:
   ``py27-pkg``, ``py35-pkg``, ``py36-pkg`` and ``py37-pkg`` [#f3]_. These use
   the 2.7, 3.5, 3.6 and 3.7 interpreters, respectively, to test all code in the
   documentation (both in Sphinx ``*.rst`` source files and in docstrings), run
   all unit tests, measure test coverage and re-build the exceptions
   documentation. To pass arguments to Py.test (the test runner) use a double
   dash (``--``) after all the Tox arguments, for example:

	.. code-block:: bash

	    $ tox -e py27-pkg -- -n 4
            GLOB sdist-make: .../pmisc/setup.py
            py27-pkg inst-nodeps: .../pmisc/.tox/dist/pmisc-...zip
            ...

   Or use the :code:`-a` Setuptools optional argument followed by a quoted
   string with the arguments for Py.test. For example:

	.. code-block:: bash

	    $ python setup.py tests -a "-e py27-pkg -- -n 4"
            running tests
            ...

   There are other convenience environments defined for Tox [#f3]_:

    * ``py27-repl``, ``py35-repl``, ``py36-repl`` and ``py37-repl`` run the 2.7,
      3.5, 3.6 or 3.7 REPL, respectively, in the appropriate virtual
      environment. The ``pmisc`` package is pip-installed by Tox when the
      environments are created.  Arguments to the interpreter can be passed in
      the command line after a double dash (``--``)

    * ``py27-test``, ``py35-test``, ``py36-test`` and ``py37-test`` run py.test
      using the Python 2.7, 3.5, Python 3.6 or Python 3.7 interpreter,
      respectively, in the appropriate virtual environment. Arguments to py.test
      can be passed in the command line after a double dash (``--``) , for
      example:

	.. code-block:: bash

	    $ tox -e py36-test -- -x test_pmisc.py
            GLOB sdist-make: [...]/pmisc/setup.py
            py36-test inst-nodeps: [...]/pmisc/.tox/dist/pmisc-1.1rc1.zip
            py36-test installed: -f file:[...]
            py36-test runtests: PYTHONHASHSEED='1264622266'
            py36-test runtests: commands[0] | [...]py.test -x test_pmisc.py
            ===================== test session starts =====================
            platform linux -- Python 3.6.4, pytest-3.3.1, py-1.5.2, pluggy-0.6.0
            rootdir: [...]/pmisc/.tox/py36/share/pmisc/tests, inifile: pytest.ini
            plugins: xdist-1.21.0, forked-0.2, cov-2.5.1
            collected 414 items
            ...

    * ``py27-cov``, ``py35-cov``, ``py36-cov`` and ``py37-cov`` test code and
      branch coverage using the 2.7, 3.5, 3.6 or 3.7 interpreter, respectively,
      in the appropriate virtual environment. Arguments to py.test can be passed
      in the command line after a double dash (``--``). The report can be found
      in
      :bash:`${pmisc_DIR}/.tox/py[PV]/usr/share/pmisc/tests/htmlcov/index.html`
      where ``[PV]`` stands for ``27``, ``35``, ``36`` or ``37`` depending on
      the interpreter used

8. Verify that continuous integration tests pass. The package has continuous
   integration configured for Linux, Apple macOS and Microsoft Winodws (all via
   `Azure DevOps <https://dev.azure.com/pmasdev>`_) Aggregation/cloud code
   coverage is configured via `Codecov <https://codecov.io>`_. It is assumed
   that the Codecov repository upload token in the build is stored in the
   :bash:`$(codecovToken)` environment variable (securely defined in the
   pipeline settings page).

9. Document the new feature or bug fix (if needed). The script
   :bash:`${PMISC_DIR}/sbin/build_docs.py` re-builds the whole package
   documentation (re-generates images, cogs source files, etc.):

	.. [[[cog pmisc.ste('build_docs.py -h', 0, mdir, cog.out) ]]]

	.. code-block:: bash

	    $ ${PKG_BIN_DIR}/build_docs.py -h
	    usage: build_docs.py [-h] [-d DIRECTORY] [-r]
	                         [-n NUM_CPUS] [-t]

	    Build pmisc package documentation

	    optional arguments:
	      -h, --help            show this help message and exit
	      -d DIRECTORY, --directory DIRECTORY
	                            specify source file directory
	                            (default ../pmisc)
	      -r, --rebuild         rebuild exceptions documentation.
	                            If no module name is given all
	                            modules with auto-generated
	                            exceptions documentation are
	                            rebuilt
	      -n NUM_CPUS, --num-cpus NUM_CPUS
	                            number of CPUs to use (default: 1)
	      -t, --test            diff original and rebuilt file(s)
	                            (exit code 0 indicates file(s) are
	                            identical, exit code 1 indicates
	                            file(s) are different)

	.. [[[end]]]

.. rubric:: Footnotes

.. [#f1] All examples are for the `bash <https://www.gnu.org/software/bash/>`_
   shell

.. [#f2] It is assumed that all the Python interpreters are in the executables
   path. Source code for the interpreters can be downloaded from Python's main
   `site <https://www.python.org/downloads>`_

.. [#f3] Tox configuration largely inspired by
   `Ionel's codelog <https://blog.ionelmc.ro/2015/04/14/
   tox-tricks-and-patterns/>`_

.. include:: ../CHANGELOG.rst

License
=======

.. include:: ../LICENSE

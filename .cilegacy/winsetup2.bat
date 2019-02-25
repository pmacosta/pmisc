REM [START IGNORE]
set PYTHON_MAJOR=2
set INTERP=py27
set PYVER=2.7
REM [STOP IGNORE]
ps: wget https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
python get-pip.py
pip install --upgrade pip wheel
pip install --upgrade --ignore-installed setuptools
which python
which pip
pip --version
ps: Invoke-WebRequest -OutFile .\hunspell.zip -Uri "https://cfhcable.dl.sourceforge.net/project/ezwinports/hunspell-1.3.2-3-w32-bin.zip" -Headers @{"Upgrade-Insecure-Requests"="1"; "DNT"="1"; "User-Agent"="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"; "Accept"="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"; "Referer"="https://sourceforge.net/projects/ezwinports/files/hunspell-1.3.2-3-w32-bin.zip/download"; "Accept-Encoding"="gzip, deflate, br"; "Accept-Language"="en-US,en;q=0.9"; "Cookie"="_ga=GA1.2.960330120.1549548167; _gid=GA1.2.253466023.1549548167; _scp=1549548167671.1888783760; _scs=1549548167673.1210103215; __gads=ID=13f7ab9f14784468:T=1549548167:S=ALNI_MatktSjb46-gGUtEr9aCuvgPeSgLQ"}
7z e -y .\hunspell.zip -o%REPO_DIR%\hunspell
ps: iex (new-object net.webclient).downloadstring('https://get.scoop.sh')
scoop install shellcheck
set PATH=%PATH%;%REPO_DIR%\hunspell;%REPO_DIR%\hunspell\bin;~\scoop\shims;~\scoop\apps\shellcheck\current
dir %REPO_DIR%\hunspell
set LANG=en_US.UTF-8
set DICPATH=%REPO_DIR%\hunspell
hunspell --version
shellcheck --version
python -c "from __future__ import print_function;import os,pip;y=pip.__file__.split(os.sep);print(os.sep.join(y[:y.index('pip')]))" > python_site_packages_dir.txt
set /p PYTHON_SITE_PACKAGES=<python_site_packages_dir.txt
set VIRTUALENV_DIR=C:\Miniconda-x64\envs\%INTERP%
set BIN_DIR=%VIRTUALENV_DIR%\Scripts
set SOURCE_DIR=%PYTHON_SITE_PACKAGES%\%PKG_NAME%
set EXTRA_DIR=%VIRTUALENV_DIR%\share\%PKG_NAME%
set SBIN_DIR=%EXTRA_DIR%\sbin
set PYTHONPATH=%PYTHONPATH%;%PYTHON_SITE_PACKAGES%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
set TRACER_DIR=%EXTRA_DIR%\docs\support
set COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
python -c "from __future__ import print_function;import os;plugin_dir = os.path.join(os.environ.get('REPO_DIR', ''), 'pylint_plugins');print(plugin_dir if os.path.isdir(plugin_dir) else '')" > pylint_plugins_dir.txt
set /p PYLINT_PLUGINS_DIR=<pylint_plugins_dir.txt
python -c "from __future__ import print_function;import glob; import os; sdir = os.environ.get('PYLINT_PLUGINS_DIR', ''); print(','.join([os.path.basename(fname).replace('.py', '') for fname in glob.glob(os.path.join(sdir, '*.py'))]) if sdir else '')" > pylint_plugins_list.txt
set /p PYLINT_PLUGINS_LIST=<pylint_plugins_list.txt
python -c "from __future__ import print_function; import os; svar=os.environ.get('PYLINT_PLUGINS_LIST', ''); print('--load-plugins='+svar if svar else '')" > pylint_cli_append.txt
set /p PYLINT_CLI_APPEND=<pylint_cli_append.txt
set PYTHONPATH=%PYTHONPATH%;%PYLINT_PLUGINS_DIR%;
echo "PYTHON_SITE_PACKAGES=%PYTHON_SITE_PACKAGES%"
echo "VIRTUALENV_DIR=%VIRTUALENV_DIR%"
echo "BIN_DIR=%BINDIR%"
echo "SOURCE_DIR=%SOURCE_DIR%"
echo "EXTRA_DIR=%EXTRA_DIR%"
echo "SBIN_DIR=%SBIN_DIR%"
echo "PYTHONPATH=%PYTHONPATH%"
echo "TRACER_DIR=%TRACER_DIR%"
echo "COV_FILE=%COV_FILE%"
echo "PYLINT_PLUGINS_DIR=%PYLINT_PLUGINS_DIR%"
echo "PYLINT_PLUGINS_LIST=%PYLINT_PLUGINS_LIST%"
echo "PYLINT_CLI_APPEND=%PYLINT_CLI_APPEND%"
REM ###
REM # Install package dependencies
REM ###
set OLD_PTYHON_PATH=%PYTHONPATH%
set PYTHONPATH=%REPO_DIR%;%REPO_DIR%\sbin;%PYTHONPATH%
cd %REPO_DIR%
python %REPO_DIR%\sbin\gen_req_files.py freeze
pip install -r%MAIN_REQUIREMENTS_FILE%
pip install -r%TESTS_REQUIREMENTS_FILE%
pip install -r%DOCS_REQUIREMENTS_FILE%
pip freeze
REM ###
REM # Create directories for reports and artifacts
REM ###
if not exist "%RESULTS_DIR%\\testresults" mkdir %RESULTS_DIR%\testresults
if not exist "%RESULTS_DIR%\\codecoverage" mkdir %RESULTS_DIR%\codecoverage
if not exist "%RESULTS_DIR%\\artifacts" mkdir %RESULTS_DIR%\artifacts

REM build_script:
REM ###
REM # Install package
REM ###
type %REPO_DIR%\MANIFEST.in
REM # Fix Git symbolik links
python .\sbin\fix_windows_symlinks.py
python setup.py sdist --formats=zip
timeout /t 5
REM # Change directory away from repository, otherwise pip does not install package
set PYTHONPATH=%OLD_PTYHON_PATH%
python -c "import os, sys; sys.path.append(os.path.realpath('./'+os.environ['PKG_NAME']));import pkgdata; print(pkgdata.__version__)" > version.txt
set /p PKG_VERSION=<version.txt
echo "PKG_VERSION=%PKG_VERSION%"
cd %PYTHON_SITE_PACKAGES%
pip install --upgrade %REPO_DIR%\dist\%PKG_NAME%-%PKG_VERSION%.zip

REM ###
REM # sbin/wintest.bat file
REM ###
REM # Write coverage configuration file
REM ###
python %SBIN_DIR%\coveragerc_manager.py 'ci' 1 %INTERP% %PYTHON_SITE_PACKAGES%
type %COV_FILE%
REM ###
REM # Change to tests sub-directory to mimic Tox conditions
REM ###
cd %EXTRA_DIR%\tests

REM test_script:
REM ###
REM # Run tests
REM ###
copy %EXTRA_DIR%\.headerrc %SOURCE_DIR%\.headerrc
pylint --rcfile=%EXTRA_DIR%\.pylintrc %PYLINT_CLI_APPEND% -f colorized -r no -s n %SOURCE_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc %PYLINT_CLI_APPEND% -f colorized -r no -s n %SBIN_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc %PYLINT_CLI_APPEND% -f colorized -r no -s n %EXTRA_DIR%\tests
pylint --rcfile=%EXTRA_DIR%\.pylintrc %PYLINT_CLI_APPEND% -f colorized -r no -s n %EXTRA_DIR%\docs\support
set DODOCTEST=1
py.test --collect-only --doctest-glob="*.rst" %EXTRA_DIR%\docs > doctest.log 2>&1 || set DODOCTEST=0
if %DODOCTEST%==1 py.test --doctest-glob="*.rst" %EXTRA_DIR%\docs
py.test --doctest-modules %SOURCE_DIR%
REM # Coverage tests runs all the unit tests, no need to run the non-coverage
REM # tests since the report is not being used
REM # - py.test -s -vv --junitxml=%RESULTS_DIR%\testresults\pytest.xml
py.test --cov-config %COV_FILE% --cov %SOURCE_DIR% --cov-report term
REM # Re-building exceptions auto-documentation takes a long time in Appveyor.
REM # They have (and should be) spot-checked every now and then
REM # - python %SBIN_DIR%\build_docs.py -r -t -d %SOURCE_DIR%

REM on_failure:
7z a %EXTRA_DIR%\artifacts.zip %EXTRA_DIR%\artifacts\*.*
appveyor PushArtifact %EXTRA_DIR%\artifacts.zip

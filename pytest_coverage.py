"""
Write and report coverage data with 'coverage.py'. 

Requires Ned Batchelder's excellent coverage:
http://nedbatchelder.com/code/coverage/
"""
import py

coverage = py.test.importorskip("coverage")
cov = coverage.coverage()

def pytest_addoption(parser):
    group = parser.addgroup('Coverage options')
    group.addoption('--cov-show-missing', action='store', default=None,
            dest='show_missing',
            help='Show missing files')
    group.addoption('--cov-report', action='store', default=None,
            dest='report', type="choice", choices=['report', 'annotate', 'html'],
            help="""
                html: Directory for html output
                report: Output a text report,
                annotate: Annotate your source code for which lines were executed and which were not
            """.strip())
    group.addoption('--cov-directory', action='store', default=None,
            dest='directory', 
            help='Directory for the reports (html / annotate results) defaults to ./coverage')
    group.addoption('--cov-ignore-errors', action='store', default=None,
            dest='ignore_errors', 
            help='Ignore errors')
    group.addoption('--cov-omit', action='store', default=None,
            dest='omit', 
            help='File with coverage files to omit')

def pytest_configure(config):
    cov.use_cache(0) # Do not cache any of the coverage.py stuff
    cov.start()

def pytest_terminal_summary(terminalreporter):
    config = terminalreporter.config
    tw = terminalreporter._tw
    tw.sep('-', 'coverage')
    tw.line('Processing Coverage...')
    cov.stop()
    cov.save()
    
    # Get the configurations
    config = terminalreporter.config
    
    show_missing = config.getvalue('show_missing')
    omit = config.getvalue('omit')
    report = config.getvalue('report') or 'report'
    directory = config.getvalue('directory') or 'coverage'
    
    # Set up the report_args
    report_args = {
        'morfs': [],
        'ignore_errors': config.getvalue('ignore_errors'),
    }
    
    # Handle any omits
    if omit:
        try:
            omit_file = py.path.local(omit)
            omit_prefixes = [line.strip() for line in omit_file.readlines()]
            report_args['omit_prefixes'] = omit_prefixes
        except:
            pass
    
    if report == 'report':
        cov.report(show_missing=show_missing, **report_args)
    if report == 'annotate':
        cov.annotate(directory=directory, **report_args)
    if report == 'html':
        cov.html_report(directory=directory, **report_args)
    
def test_functional(testdir):
    py.test.importorskip("coverage")
    testdir.plugins.append("coverage")
    testdir.makepyfile("""
        def f():    
            x = 42
        def test_whatever():
            pass
        """)
    result = testdir.runpytest()
    assert result.ret == 0
    assert result.stdout.fnmatch_lines([
        '*Processing Coverage*'
        ])
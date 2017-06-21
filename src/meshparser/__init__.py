from pkg_resources import resource_string


version = resource_string(__name__, 'version.txt').strip()
__version__ = version.decode('utf-8')

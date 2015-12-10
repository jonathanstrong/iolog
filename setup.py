try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'route log events from TCP to websocket for streaming log events on a web page.',
    'author': 'Jonathan Strong',
    'url': 'https://github.com/jonathanstrong/log-viewer',
    'download_url':'https://github.com/jonathanstrong/log-viewer',
    'author_email': 'jonathan.strong@gmail.com',
    'version': '0.1',
    'install_requires': ['tornado'],
    'packages': ['iolog'],
    'scripts': [],
    'name': 'iolog'
}

setup(**config)

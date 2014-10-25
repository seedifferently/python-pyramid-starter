import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

install_requires = [
    'pyramid >= 1.5, < 1.6',      # Pyramid web framework
    'waitress',                   # Production-quality pure-Python WSGI server

#    'psycopg2 >= 2.5',            # Python PostgreSQL driver
    'SQLAlchemy >= 0.9, < 0.10',  # A powerful and flexible SQL toolkit and ORM
    'pyramid_tm',                 # These two are for Pyramid's SQLAlchemy
    'zope.sqlalchemy',            # transaction management.

    'pyramid_handlers',           # Support for "Controller"-style view logic
    'pyramid_jinja2',             # Jinja2 template bindings
    'pyramid_mailer',             # Helper module for sending emails
    'pyramid_debugtoolbar',       # Interactive debugging for app development

    'cryptacular',                # Secure user password hashing
    'marshmallow',                # Simplified JSON serialization
    'formencode >= 1.3.0a1',      # Input validation and form generation
    'webhelpers2 >= 2.0rc1',       # Utility functions for web applications
    'paginate_sqlalchemy >= 0.2', # Divides large lists of items into pages
    'html2text',                  # Turn HTML into equivalent Markdown
]

# Packages requirements for testing
tests_require = install_requires[:]
tests_require.extend([
    'nose',
    'coverage',
    'webtest',
    'cssselect',
    'pyquery',
])

# Packages requirements for documentation
docs_require = install_requires[:]
docs_require.extend([
    'sphinx',
])

setup(name='Starter',
      version='0.0',
      description='Pyramid Starter',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={
          'tests': tests_require,
          'docs': docs_require
      },
      entry_points="""\
      [paste.app_factory]
      main = starter:main
      [console_scripts]
      initialize_starter_db = starter.scripts.initializedb:main
      """,
      )

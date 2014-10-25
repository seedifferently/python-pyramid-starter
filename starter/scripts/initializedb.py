# System imports
import os
import sys
import transaction

# 3rd party imports
from sqlalchemy import engine_from_config

# Pyramid imports
from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

# Project imports
from ..models import DBSession, Base, seeds


def usage(argv):
    cmd = os.path.basename(argv[0])
    # TODO: compat
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    # Seed
    seeds.seed_all()


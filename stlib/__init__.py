#  Keep the import order, please

import gevent.monkey

gevent.monkey.patch_all()

from stlib import (logging,
                   config,
                   network,
                   browser,
                   card_farming)

__all__ = ['logger',
           'config',
           'network',
           'browser',
           'card_farming']

logger = logging.get_logger('VERBOSE')

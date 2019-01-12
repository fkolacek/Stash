#
# Author: Frantisek Kolacek <work@kolacek.it>
# Version: 1.0
#


class StashException(Exception):
    pass


class StashConfigException(StashException):
    pass


class StashDatabaseException(StashException):
    pass

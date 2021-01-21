from crispy.apps.core.exceptions import CrispyException


class FeedError(CrispyException):
    pass


class BrokenFeed(CrispyException):
    pass


class TemporaryFeedError(CrispyException):
    pass

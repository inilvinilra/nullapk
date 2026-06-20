class NullApkError(Exception):
    """Base class for all expected nullapk failures."""


class InvalidTargetError(NullApkError):
    """Raised when the supplied URL or package id can't be parsed."""


class DispenserError(NullApkError):
    """Raised when the Aurora dispenser fails to issue an auth token."""


class DownloadError(NullApkError):
    """Raised when apkeep fails to fetch the APK."""


class MissingDependencyError(NullApkError):
    """Raised when a required external binary is not on PATH."""

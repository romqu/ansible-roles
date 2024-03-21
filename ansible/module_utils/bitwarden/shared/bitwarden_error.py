import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class BitwardenError(abc.ABC):
    error_message: str
    exception: Exception | None = None


@dataclass(frozen=True)
class RunCmdError(BitwardenError):
    ...


@dataclass(frozen=True)
class JqError(BitwardenError):
    ...


@dataclass(frozen=True)
class ParseInputError(BitwardenError):
    ...

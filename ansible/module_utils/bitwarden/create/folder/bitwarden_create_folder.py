from dataclasses import dataclass


@dataclass(frozen=True)
class BitwardenCreateFolder:
    name: str

from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from enum import StrEnum, Enum
from uuid import UUID


class BitwardenCmdListType(StrEnum):
    FOLDERS = "folders"


class BitwardenCmdTemplateType(StrEnum):
    FOLDER = "folder"


class BitwardenItemType(Enum):
    LOGIN = 1


@dataclass(frozen=True)
class BitwardenItemLogin:
    username: str
    password: str


@dataclass(frozen=True)
class BitwardenItem:
    id: UUID
    folder_id: UUID
    type: int
    name: str
    login: BitwardenItemLogin


@dataclass(frozen=True)
class BitwardenFolder:
    object: str
    id: str
    name: str

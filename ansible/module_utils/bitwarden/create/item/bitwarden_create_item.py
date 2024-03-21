from dataclasses import dataclass
from uuid import UUID

from ansible.module_utils.bitwarden.shared.bitwarden_model import BitwardenItemLogin


@dataclass(frozen=True)
class BitwardenCreateItem:
    folderId: UUID | None
    type: int
    name: str
    login: BitwardenItemLogin

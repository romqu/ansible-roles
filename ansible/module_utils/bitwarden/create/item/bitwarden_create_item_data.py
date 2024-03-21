from dataclasses import dataclass
from uuid import UUID

from ansible.module_utils.bitwarden.shared.bitwarden_model import BitwardenItem


@dataclass(frozen=True)
class BitwardenCreateItemData:
    name: str
    password: str
    username: str | None
    folder_name: str | None
    folder_id: UUID | None
    existing: BitwardenItem | None = None
    created: BitwardenItem | None = None
    changed: bool = False

from dataclasses import dataclass

from ansible.module_utils.bitwarden.shared.bitwarden_model import BitwardenFolder


@dataclass(frozen=True)
class BitwardenCreateFolderData:
    name: str
    parent: str
    path: str
    splitted: list[str]
    existing: BitwardenFolder | None = None
    created: BitwardenFolder | None = None

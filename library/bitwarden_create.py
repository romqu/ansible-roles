# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import sys
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from ansible.module_utils.basic import _load_params

__metaclass__ = type

from ansible.module_utils.bitwarden.main_create_folder import (
    main_create_folder,
    BitwardenCreateFolderModule,
)

from ansible.module_utils.bitwarden.main_create_item import (
    main_create_item,
    BitwardenCreateItemModule,
)

from ansible.module_utils.bitwarden.shared.bitwarden_cmd import BitwardenCmd

from ansible.module_utils.bitwarden.shared.bitwarden_module import BitwardenModule

from ansible.module_utils.bitwarden.create.item.bitwarden_create_item_service import (
    BitwardenCreateItemService,
)

from ansible.module_utils.bitwarden.create.folder.bitwarden_create_folder_service import (
    BitwardenCreateFolderService,
)

DOCUMENTATION = """"""

RETURN = """"""


class BitwardenCreateType(StrEnum):
    FOLDER = "folder"
    ITEM = "item"


type BitwardenCreateModuleProvider[T: BitwardenModule] = Callable[[], T]


def _module_provider() -> dict[str, BitwardenCreateModuleProvider]:
    module_map: dict[str, BitwardenCreateModuleProvider] = {}
    for create_type in BitwardenCreateType:
        match create_type:
            case BitwardenCreateType.FOLDER:
                module_map[create_type] = lambda: BitwardenCreateFolderModule()
            case BitwardenCreateType.ITEM:
                module_map[create_type] = lambda: BitwardenCreateItemModule()
    return module_map


def run_module():
    bitwarden__cmd = BitwardenCmd()
    params: Any = _load_params()
    create_type_name: str = params["type"]

    match BitwardenCreateType(create_type_name):
        case BitwardenCreateType.FOLDER:
            create_folder_module: BitwardenCreateFolderModule = get_module(
                create_type_name
            )
            fail_when_locked(bitwarden__cmd, create_folder_module)
            main_create_folder(
                BitwardenCreateFolderService(bitwarden__cmd),
                create_folder_module,
            )
        case BitwardenCreateType.ITEM:
            create_item_module: BitwardenCreateItemModule = get_module(create_type_name)
            fail_when_locked(bitwarden__cmd, create_item_module)
            main_create_item(
                BitwardenCreateItemService(bitwarden__cmd),
                create_item_module,
            )


def get_module[T: BitwardenModule](create_type_name: str) -> T:
    module_provider: BitwardenCreateModuleProvider | None = _module_provider().get(
        create_type_name
    )
    if module_provider is not None:
        return module_provider()
    else:
        sys.exit(1)


def fail_when_locked(
    bitwarden__cmd: BitwardenCmd,
    bitwarden__module: BitwardenModule,
):
    if not bitwarden__cmd.is_unlocked():
        bitwarden__module.ansible_module.fail_json(
            msg="Bitwarden Vault locked. Run 'bw unlock'.",
            **bitwarden__module.ansible_result,
        )


def main():
    run_module()


if __name__ == "__main__":
    main()

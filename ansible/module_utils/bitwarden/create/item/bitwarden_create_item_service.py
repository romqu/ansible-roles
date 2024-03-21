from __future__ import absolute_import, division, print_function

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import replace
from typing import Final
from uuid import UUID

from ansible.module_utils.bitwarden.create.item.bitwarden_create_item import (
    BitwardenCreateItem,
)
from ansible.module_utils.bitwarden.create.item.bitwarden_create_item_data import (
    BitwardenCreateItemData,
)
from ansible.module_utils.bitwarden.create.item.bitwarden_create_item_mapper import (
    map_to_bitwarden__create_item,
)
from ansible.module_utils.bitwarden.shared.bitwarden_cmd import BitwardenCmd
from ansible.module_utils.bitwarden.shared.bitwarden_error import BitwardenError
from ansible.module_utils.bitwarden.shared.bitwarden_model import (
    BitwardenFolder,
    BitwardenItemType,
    BitwardenItemLogin,
)
from result import Result, Ok, Err


@dataclass(frozen=True)
class BitwardenCreateItemServiceData:
    create_item_list: list[BitwardenCreateItemData]
    folder_list: list[BitwardenFolder]


class BitwardenCreateItemService:
    cmd: Final[BitwardenCmd]

    def __init__(self, cmd: BitwardenCmd) -> None:
        self.cmd = cmd

    def execute(
        self, input_data: dict[str, str]
    ) -> Result[BitwardenCreateItemData, BitwardenError]:
        return (
            map_to_bitwarden__create_item(input_data)
            .and_then(lambda item: self.cmd.sync().map(lambda _: item))
            .and_then(self._maybe_get_existing_item)
            .and_then(self._get_folder_id)
            .and_then(self._maybe_create_item)
        )

    def _maybe_get_existing_item(
        self, item: BitwardenCreateItemData
    ) -> Result[BitwardenCreateItemData, BitwardenError]:
        return (
            self.cmd.get_item(item.name)
            .or_else(lambda err: self._maybe_get_by_error(err, self.cmd.get_folder))
            .map(lambda existing_item: replace(item, existing=existing_item))
            .or_else(lambda err: self._maybe_continue_if_not_found(err, item))
        )

    @staticmethod
    def _maybe_continue_if_not_found(
        error: BitwardenError, item: BitwardenCreateItemData
    ):
        if "Not found" in error.error_message:
            return Ok(item)
        else:
            return Err(error)

    def _get_folder_id(
        self, item: BitwardenCreateItemData
    ) -> Result[BitwardenCreateItemData, BitwardenError]:
        if item.folder_id:
            return Ok(item)

        return (
            self.cmd.get_folder(str(item.folder_name))
            .or_else(lambda err: self._maybe_get_by_error(err, self.cmd.get_folder))
            .map(lambda folder: replace(item, folder_id=UUID(folder.id)))
        )

    def _maybe_create_item(
        self, item: BitwardenCreateItemData
    ) -> Result[BitwardenCreateItemData, BitwardenError]:
        if item.existing is None:
            username = item.username
            password = item.password
            return self.cmd.create_item(
                BitwardenCreateItem(
                    folderId=item.folder_id,
                    type=BitwardenItemType.LOGIN.value,
                    name=item.name,
                    login=BitwardenItemLogin(
                        username=username if username is not None else "",
                        password=password if password is not None else "",
                    ),
                )
            ).map(lambda created_item: replace(item, created=created_item))
        else:
            username = item.username
            password = item.password
            existing = item.existing
            edit_item = BitwardenCreateItem(
                folderId=item.folder_id,
                type=BitwardenItemType.LOGIN.value,
                name=item.name,
                login=BitwardenItemLogin(
                    username=username if username is not None else existing.username,
                    password=password if password is not None else existing.password,
                ),
            )

            return self.cmd.edit_item(existing.id, edit_item).map(
                lambda edited_item: replace(item, existing=edited_item, changed=True)
            )

    @staticmethod
    def _maybe_get_by_error[T](
        err: BitwardenError, f: Callable[[str], Result[T, BitwardenError]]
    ) -> Result[T, BitwardenError]:
        message = str(err.error_message)
        if "More than one result was found" in message:
            split = message.split("\n")
            folder_id = split[1]
            return f(folder_id)
        else:
            return Err(err)

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Final

from ansible.module_utils.bitwarden.create.folder.bitwarden_create_folder import (
    BitwardenCreateFolder,
)
from ansible.module_utils.bitwarden.create.folder.bitwarden_create_folder_data import (
    BitwardenCreateFolderData,
)
from ansible.module_utils.bitwarden.shared.bitwarden_cmd import BitwardenCmd
from ansible.module_utils.bitwarden.shared.bitwarden_error import BitwardenError
from result import Ok, Err, Result


@dataclass(frozen=True)
class ParseFolderInputError(BitwardenError):
    ...


class BitwardenCreateFolderService:
    cmd: Final[BitwardenCmd]

    def __init__(self, cmd: BitwardenCmd) -> None:
        self.cmd = cmd

    def execute(
        self, input_data: dict[str, str]
    ) -> Result[BitwardenCreateFolderData, BitwardenError]:
        return (
            self.cmd.sync()
            .and_then(lambda _: self._map_from(input_data))
            .map(self._maybe_get_folder)
            .and_then(self._maybe_create_folder)
        )

    # TODO: validate input
    # def validate_input(self):
    #    pass

    @staticmethod
    def _map_from(
        input_data: dict[str, str]
    ) -> Result[BitwardenCreateFolderData, BitwardenError]:
        try:
            name = input_data["name"]
            parent = input_data["parent"]
            path = f"{parent}/{name}"
            splitted: list[str] = parent.split("/") + [name]

            return Ok(
                BitwardenCreateFolderData(
                    name,
                    parent,
                    path=path,
                    splitted=splitted,
                )
            )
        except Exception as err:
            return Err(ParseFolderInputError("Could not parse input.", err))

    def _maybe_get_folder(
        self, data: BitwardenCreateFolderData
    ) -> BitwardenCreateFolderData:
        return self.cmd.get_folder(data.path).map_or(
            default=data, op=lambda folder: replace(data, existing=folder)
        )

    def _maybe_create_folder(
        self, data: BitwardenCreateFolderData
    ) -> Result[BitwardenCreateFolderData, BitwardenError]:
        if data.existing is None:
            acc_folder_name = data.splitted[0]
            acc_result: Result[
                BitwardenCreateFolderData, BitwardenError
            ] = self._get_or_create_folder(acc_folder_name, data)

            if len(data.splitted) == 1:
                return acc_result

            for index, folder_name in enumerate(data.splitted[1:]):
                acc_folder_name += f"/{folder_name}"
                acc_result = acc_result.and_then(
                    lambda _: self._get_or_create_folder(acc_folder_name, data)
                )
            return acc_result
        return Ok(data)

    def _get_or_create_folder(
        self, folder_name: str, data: BitwardenCreateFolderData
    ) -> Result[BitwardenCreateFolderData, BitwardenError]:
        return (
            self.cmd.get_folder(folder_name)
            .or_else(
                lambda err: self._maybe_get_by_error(err, self.cmd.get_folder).or_else(
                    lambda _: self.cmd.create_folder(
                        BitwardenCreateFolder(name=folder_name)
                    )
                )
            )
            .map(lambda folder: replace(data, created=folder))
        )

    @staticmethod
    def _maybe_get_by_error[
        T
    ](err: BitwardenError, f: Callable[[str], Result[T, BitwardenError]]) -> Result[
        T, BitwardenError
    ]:
        message = str(err.error_message)
        if "More than one result was found" in message:
            split = message.split("\n")
            folder_id = split[1]
            return f(folder_id)
        else:
            return Err(err)

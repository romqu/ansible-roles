from __future__ import absolute_import, division, print_function

import json
from types import SimpleNamespace as Namespace
from typing import Any, TypeVar

from ansible.module_utils.bitwarden.create.folder.bitwarden_create_folder import (
    BitwardenCreateFolder,
)
from ansible.module_utils.bitwarden.create.item.bitwarden_create_item import (
    BitwardenCreateItem,
)
from ansible.module_utils.bitwarden.shared.bitwarden_error import BitwardenError
from ansible.module_utils.bitwarden.shared.bitwarden_model import (
    BitwardenItem,
    BitwardenFolder,
    BitwardenCmdTemplateType,
    BitwardenCmdListType,
)
from ansible.module_utils.bitwarden.shared.cmd_run import run_cmd
from ansible.module_utils.bitwarden.shared.encode_util import encode_base_64
from orjson import orjson
from result import Result, Ok, Err


class BitwardenCmd:
    T = TypeVar("T")

    def __init__(self, path: str = "bw"):
        self._cli_path = path

    @property
    def cli_path(self) -> str:
        return self._cli_path

    def is_unlocked(self) -> bool:
        match self.get_status():
            case Ok(value):
                return value["status"] == "unlocked"
            case Err(_):
                return False
        return False

    def get_status(self) -> Result[dict, BitwardenError]:
        result = self._run(["status"])
        return self._decode(result)

    def get_item(self, item_name: str) -> Result[BitwardenItem, BitwardenError]:
        return self._get(["item", item_name])

    def get_folder(self, folder_id: str) -> Result[BitwardenFolder, BitwardenError]:
        return self._get(["folder", folder_id])

    def get_template(
        self, template_type: BitwardenCmdTemplateType
    ) -> Result[Any, BitwardenError]:
        result = self._run(["template", str(template_type.value)])

        return self._decode(result)

    def create_folder(
        self,
        folder: BitwardenCreateFolder,
    ) -> Result[BitwardenFolder, BitwardenError]:
        return self._create(
            ["folder", encode_base_64(json.dumps(folder, default=vars))]
        )

    def create_item(
        self,
        item: BitwardenCreateItem,
    ) -> Result[BitwardenItem, BitwardenError]:
        return self._create(["item", encode_base_64(orjson.dumps(item).decode())])

    def edit_item(
        self,
        id: str,
        item: BitwardenCreateItem,
    ) -> Result[BitwardenItem, BitwardenError]:
        return self._edit (["item", id, encode_base_64(orjson.dumps(item).decode())])

    def list_(
        self, list_type: BitwardenCmdListType, args: list[str] | None = None
    ) -> Result[T, BitwardenError]:
        if args is None:
            args = []
        result = self._run(["list", str(list_type.value)] + args)

        return self._map_to(result)

    def _get(self, args: list[str]) -> Result[T, BitwardenError]:
        result = self._run(["get"] + args)

        return self._map_to(result)

    def _create(self, args: list[str]) -> Result[T, BitwardenError]:
        result = self._run(["create"] + args)

        return self._map_to(result)

    def _edit(self, args: list[str]) -> Result[T, BitwardenError]:
        result = self._run(["edit"] + args)

        return self._map_to(result)

    def sync(self) -> Result[str, BitwardenError]:
        return self._run(["sync"])

    def _run(self, args: list[str]) -> Result[str, BitwardenError]:
        return run_cmd([self.cli_path] + args)

    @staticmethod
    def _decode(result: Result[str, BitwardenError]) -> Result[dict, BitwardenError]:
        return result.map(lambda output: json.loads(output))

    @staticmethod
    def _map_to(result: Result[str, BitwardenError]) -> Result[T, BitwardenError]:
        return result.map(
            lambda output: json.loads(output, object_hook=lambda d: Namespace(**d))
        )

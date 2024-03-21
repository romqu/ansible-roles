# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

from result import Result, Ok, Err

from ansible.module_utils.bitwarden.create.folder.bitwarden_create_folder_service import (
    BitwardenCreateFolderService,
)

from ansible.module_utils.bitwarden.create.folder.bitwarden_create_folder_data import (
    BitwardenCreateFolderData,
)

from ansible.module_utils.bitwarden.shared.bitwarden_error import BitwardenError

from ansible.module_utils.bitwarden.shared.bitwarden_module import BitwardenModule

DOCUMENTATION = """"""

RETURN = """"""


class BitwardenCreateFolderModule(BitwardenModule):
    @property
    def ansible_module(self) -> AnsibleModule:
        return AnsibleModule(
            argument_spec=self.module_args,
            supports_check_mode=False,
        )

    @property
    def module_args(self) -> dict:
        return dict(
            type=dict(type="str", required=False),
            name=dict(type="str", required=True),
            parent=dict(type="str", required=True),
        )

    @property
    def ansible_result(self) -> dict:
        return dict(changed=False, folder_id="")


def main_create_folder(
    bitwarden__service: BitwardenCreateFolderService,
    module: BitwardenCreateFolderModule,
):
    ansible_module = module.ansible_module
    ansible_result = module.ansible_result
    result: Result[
        BitwardenCreateFolderData, BitwardenError
    ] = bitwarden__service.execute(ansible_module.params)

    match result:
        case Ok(value_):
            value: BitwardenCreateFolderData = value_
            folder_id = "folder_id"
            if value.created:
                ansible_result["changed"] = True
                ansible_result[folder_id] = str(value.created.id)
            elif value.existing:
                ansible_result[folder_id] = str(value.existing.id)
            ansible_module.exit_json(**ansible_result)
        case Err(err_):
            err: BitwardenError = err_
            ansible_module.fail_json(msg=err.error_message)

    ansible_module.exit_json(**ansible_result)

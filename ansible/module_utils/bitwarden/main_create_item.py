# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

from result import Result, Ok, Err

from ansible.module_utils.bitwarden.create.item.bitwarden_create_item_service import (
    BitwardenCreateItemService,
)

from ansible.module_utils.bitwarden.create.item.bitwarden_create_item_data import (
    BitwardenCreateItemData,
)

from ansible.module_utils.bitwarden.shared.bitwarden_error import BitwardenError

from ansible.module_utils.bitwarden.shared.bitwarden_module import BitwardenModule

DOCUMENTATION = """"""

RETURN = """"""


class BitwardenCreateItemModule(BitwardenModule):
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
            username=dict(type="str", required=False),
            folder_id=dict(type="str", required=False),
            folder_name=dict(type="str", required=False),
            password=dict(type="str", required=True),
        )

    @property
    def ansible_result(self) -> dict:
        return dict(changed=False, item_id="", item_name="")


def main_create_item(
    bitwarden__service: BitwardenCreateItemService,
    module: BitwardenModule,
):
    ansible_module = module.ansible_module
    ansible_result = module.ansible_result
    result: Result[BitwardenCreateItemData, BitwardenError] = (
        bitwarden__service.execute(ansible_module.params)
    )

    match result:
        case Ok(value_):
            value: BitwardenCreateItemData = value_
            item_id = "item_id"
            if value.changed:
                ansible_result["changed"] = True
                ansible_result[item_id] = (
                    value.existing.id if value.created is None else value.created.id
                )
            elif value.existing:
                ansible_result[item_id] = str(value.existing.id)
            ansible_result["item_name"] = value.name
            ansible_module.exit_json(**ansible_result)
        case Err(err_):
            err: BitwardenError = err_
            ansible_module.fail_json(msg=err.error_message)

    ansible_module.exit_json(**ansible_result)

from uuid import UUID

from ansible.module_utils.bitwarden.create.item.bitwarden_create_item_data import (
    BitwardenCreateItemData,
)
from ansible.module_utils.bitwarden.shared.bitwarden_error import (
    BitwardenError,
    ParseInputError,
)
from result import Result, Ok, Err


def map_to_bitwarden__create_item(
    input_data: dict[str, str]
) -> Result[BitwardenCreateItemData, BitwardenError]:
    result: Result[BitwardenCreateItemData, BitwardenError]
    try:
        folder_name: str | None = input_data["folder_name"]
        folder_id: str | None = input_data["folder_id"]

        if (
            folder_name is None
            and folder_id is None
            and (folder_name and folder_name.strip())
            and (folder_id and folder_id.strip())
        ):
            return Err(
                ParseInputError("Either folder_name or folder_id must be provided")
            )

        item = BitwardenCreateItemData(
            name=input_data["name"],
            username=input_data["username"],
            password=input_data["password"],
            folder_name=folder_name,
            folder_id=UUID(folder_id) if folder_id else None,
        )
        result = Ok(item)
    except Exception as err:
        result = Err(ParseInputError("Could not parse input.", err))
    return result

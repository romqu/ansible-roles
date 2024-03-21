from abc import abstractmethod, ABC

from ansible.module_utils.basic import AnsibleModule


class BitwardenModule(ABC):
    @property
    @abstractmethod
    def module_args(self) -> dict:
        pass

    @property
    @abstractmethod
    def ansible_result(self) -> dict:
        pass

    @property
    @abstractmethod
    def ansible_module(self) -> AnsibleModule:
        pass

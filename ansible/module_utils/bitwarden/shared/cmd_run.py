from subprocess import Popen, PIPE

from ansible.module_utils.bitwarden.shared.bitwarden_error import (
    BitwardenError,
    RunCmdError,
)
from ansible.module_utils.common.text.converters import to_bytes, to_text
from result import Result, Err, Ok


def run_cmd(args: list[str], stdin=None, expected_rc=0) -> Result[str, BitwardenError]:
    p = Popen(args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = p.communicate(to_bytes(stdin))
    rc = p.wait()
    if rc != expected_rc:
        return Err(RunCmdError(err.decode("utf-8"), Exception(err)))
    return Ok(to_text(out, errors="surrogate_or_strict"))

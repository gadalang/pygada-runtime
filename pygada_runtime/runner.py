__all__ = ["run"]
import sys
import os
import asyncio
from typing import Optional, List
from . import stream
from .stream import StreamBase


class Process:
    def __init__(self, proc, *, stdout: StreamBase = None, stderr: StreamBase = None):
        """Process instance.

        :param stdout: output stream (default sys.stdout)
        :param stderr: error stream (default sys.stderr)
        """
        self._proc = proc
        self._stdout = stream.wrap(stdout if stdout is not None else sys.stdout)
        self._stderr = stream.wrap(stderr if stderr is not None else sys.stderr)

        self._task = asyncio.create_task(
            asyncio.wait(
                [
                    asyncio.create_task(stream.feed(proc.stdout, self._stdout)),
                    asyncio.create_task(stream.feed(proc.stderr, self._stderr)),
                    asyncio.create_task(proc.wait()),
                ],
                return_when=asyncio.ALL_COMPLETED,
            )
        )

    @property
    def returncode(self):
        return self._proc.returncode

    async def wait(self):
        """Wait for process to terminate."""
        await self._task


async def run(
    node: str,
    argv: List = None,
    *,
    env: dict = None,
    stdin=None,
    stdout: StreamBase = None,
    stderr: StreamBase = None,
) -> Process:
    """Run a gada node.

    :param node: gada node to run
    :param argv: additional CLI arguments
    :param env: environment variables
    :param stdin: input stream (default sys.stdin)
    :param stdout: output stream (default sys.stdout)
    :param stderr: error stream (default sys.stderr)
    :return: Process instance
    """
    argv = argv if argv is not None else []

    _env = os.environ
    _env.update(env)

    # Spawn a subprocess
    return Process(
        proc=await asyncio.create_subprocess_shell(
            f"gada {node} {' '.join(argv)}",
            env=_env,
            stdin=stdin,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        ),
        stdout=stdout,
        stderr=stderr,
    )

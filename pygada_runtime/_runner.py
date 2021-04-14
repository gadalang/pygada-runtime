""":mod:`pygada_runtime` provides a convenient way to run others gada nodes
and process their output.
"""
__all__ = ["Process", "run"]
import sys
import os
import asyncio
from typing import Optional, List
from ._stream import StreamBase, async_stream, feed
from ._intercom import start_intercom, IntercomServer


class Process:
    """Wrap a subprocess running a gada node.

    The subprocess ``stdout`` and ``stderr`` are redirected to
    :attr:`stdout` and :attr:`stderr` passed in arguments so you can
    read from the subprocess output.

    It is advised to use :meth:`pygada_runtime.run` instead of
    using directly this class.

    :param proc: subprocess instance
    :param stdout: output stream (default is sys.stdout)
    :param stderr: error stream (default is sys.stderr)
    :param intercom: intercom server
    """

    def __init__(
        self,
        proc,
        *,
        stdout: Optional[StreamBase] = None,
        stderr: Optional[StreamBase] = None,
        intercom: Optional[IntercomServer] = None,
    ):
        self._proc = proc
        self._stdout = async_stream(stdout if stdout is not None else sys.stdout)
        self._stderr = async_stream(stderr if stderr is not None else sys.stderr)
        self._intercom = intercom

        self._task = asyncio.create_task(
            asyncio.wait(
                [
                    asyncio.create_task(feed(proc.stdout, self._stdout)),
                    asyncio.create_task(feed(proc.stderr, self._stderr)),
                    asyncio.create_task(proc.wait()),
                ],
                return_when=asyncio.ALL_COMPLETED,
            )
        )

    def __aenter__(self):
        return self

    def __aexit__(self, *args, **kwargs):
        if self._intercom:
            self._intercom.__aexit__(self, *args, **kwargs)
            self._intercom = None

    @property
    def intercom(self) -> IntercomServer:
        """Get intercom server.

        :return: intercom server
        """
        return self._intercom

    @property
    def returncode(self) -> int:
        """Get return code from process.

        :return: return code
        """
        return self._proc.returncode

    async def wait(self):
        """Wait for process to terminate."""
        await self._task


async def run(
    node: str,
    argv: List = None,
    *,
    env: dict = None,
    stdin: Optional[any] = None,
    stdout: Optional[StreamBase] = None,
    stderr: Optional[StreamBase] = None,
    use_intercom: Optional[bool] = None,
    intercom: Optional[IntercomServer] = None,
) -> Process:
    r"""Run a gada node:

    .. code-block:: python

        >>> import asyncio
        >>> import pygada_runtime
        >>>
        >>> async def main():
        ...     with pygada_runtime.PipeStream() as stdout:
        ...         # Run "gada testnodes.hello" in a subprocess
        ...         proc = await pygada_runtime.run('testnodes.hello', ['john'], stdout=stdout)
        ...
        ...         # Wait for completion
        ...         await proc.wait()
        ...
        ...         # Read subprocess output
        ...         output = await stdout.read()
        ...
        ...         # Print output converted to str and remove newline
        ...         print(output.decode().strip())
        >>>
        >>> asyncio.run(main())
        hello john !
        >>>

    :param node: gada node to run
    :param argv: additional CLI arguments
    :param env: environment variables
    :param stdin: input stream (default sys.stdin)
    :param stdout: output stream (default sys.stdout)
    :param stderr: error stream (default sys.stderr)
    :param use_intercom: use intercom
    :param intercom: intercom server
    :return: Process instance
    """
    argv = argv if argv is not None else []
    env = env if env is not None else {}

    _env = os.environ
    _env.update(env)

    # Start intercom server
    if use_intercom or intercom is not None:
        if intercom is None:
            intercom = await start_intercom()
        argv = ["--intercom-port", intercom.port] + argv
    else:
        intercom = None

    # Spawn a subprocess
    return Process(
        proc=await asyncio.create_subprocess_shell(
            f"gada {node} {' '.join(str(_) for _ in argv)}",
            env=_env,
            stdin=stdin,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        ),
        stdout=stdout,
        stderr=stderr,
        intercom=intercom,
    )

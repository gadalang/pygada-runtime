__all__ = ["RunnerTestCase"]
import os
import sys
import io
import asyncio
import unittest
from pygada_runtime.stream import *
from pygada_runtime import runner
from pygada_runtime.test_utils import *
import binaryiotools


def run(node, argv=[], *, stdin=None):
    def wrapper(fun):
        async def worker(
            *args,
            **kwargs,
        ):
            # Create readable stdout and stderr streams
            with PipeStream() as stdout:
                with PipeStream() as stderr:
                    # Run gada node
                    proc = await runner.run(
                        node,
                        argv,
                        env={"PYTHONPATH": os.path.dirname(__file__)},
                        stdin=stdin,
                        stdout=stdout,
                        stderr=stderr,
                    )

                    # Wait for completion
                    await proc.wait()

                    # Call wrapped function
                    await fun(*args, proc=proc, stdout=stdout, stderr=stderr, **kwargs)

        return worker

    return wrapper


class RunnerTestCase(unittest.TestCase):
    @async_test
    @run("testnodes.sum", ["1", "2"])
    async def test_sum_stdout(self, proc, stdout, stderr):
        """Test reading stdout from ``testnodes.sum``."""
        # Check stderr is empty
        self.assertEqual(await stderr.read(), b"")

        # Output on stdout should be "3"
        self.assertEqual(await stdout.read(1), b"3")

    @async_test
    @run("testnodes.sum", ["-h"])
    async def test_sum_help(self, proc, stdout, stderr):
        """Test printing help from ``testnodes.sum``."""
        # Check stderr is empty
        self.assertEqual(await stderr.read(), b"")

        # Check help message is in stdout
        self.assertIn(b"usage: sum [-h]", await stdout.read())

    @async_test
    @run("testnodes.sum", ["1"])
    async def test_sum_stderr(self, proc, stdout, stderr):
        """Test reading stderr from ``testnodes.sum``."""
        # Check stdout is empty
        self.assertEqual(await stdout.read(), b"")

        # Exception should be: "expected at least two int"
        self.assertIn(b"expected at least two int", await stderr.read())

    @async_test
    async def test_sum_chain(self):
        """Test chain mode ``testnodes.sum``."""
        # Create a writable stdin stream
        with PipeStream() as stdin:

            @run(
                node="testnodes.sum",
                argv=["--chain-input", "--chain-output"],
                stdin=stdin.reader,
            )
            async def worker(proc, stdout, stderr):
                # Exception should be: "expected a list of int"
                data = await read_packet(stdout)
                buffer = binaryiotools.IO(data)
                self.assertEqual(buffer.i32, 3)

            # Write a list of int to stdin
            buffer = binaryiotools.IO()
            buffer.i32 = 2
            buffer.i32 = 1
            buffer.i32 = 2
            buffer.index = 0
            await write_packet(stdin, buffer.data)
            stdin.eof()


            # Run gada node
            await worker()


if __name__ == "__main__":
    unittest.main()

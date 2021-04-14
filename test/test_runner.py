__all__ = ["RunnerTestCase"]
import os
import sys
import io
import asyncio
import unittest
import pygada_runtime
from pygada_runtime import (
    PipeStream,
    write_packet,
    read_packet,
    read_json,
    write_json,
    start_intercom,
    test_utils,
)


class RunnerTestCase(unittest.TestCase):
    async def call(
        self,
        node,
        argv=None,
        has_stdout: bool = None,
        has_stderr: bool = None,
        intercom=None,
    ):
        # Run gada node
        stdout, stderr = await test_utils.run(node, argv, intercom=intercom)

        # Check outputs
        if has_stderr is False:
            self.assertEqual(stderr, "", "should have no stderr")
        elif has_stderr is True:
            self.assertNotEqual(stderr, "", "should have stderr")
        if has_stdout is False:
            self.assertEqual(stdout, "", "should have no stdout")
        elif has_stdout is True:
            self.assertNotEqual(stdout, "", "should have stdout")

        return stdout.strip(), stderr.strip()

    @test_utils.async_test
    @test_utils.timeout
    async def test_python_hello(self):
        """Test running ``testnodes.hello``."""
        stdout, stderr = await self.call(
            "testnodes.hello", ["john"], has_stdout=True, has_stderr=False
        )

        self.assertEqual(stdout, "hello john !", "wrong output")

    @test_utils.async_test
    @test_utils.timeout
    async def test_python_hello_stderr(self):
        """Test running ``testnodes.hello`` without arguments => print argparse help."""
        stdout, stderr = await self.call(
            "testnodes.hello", has_stdout=False, has_stderr=True
        )

        self.assertIn("usage: hello [-h]", stderr, "wrong output")

    @test_utils.async_test
    @test_utils.timeout
    async def test_pymodule_hello(self):
        """Test running ``testnodes.pymodule_hello``."""
        stdout, stderr = await self.call(
            "testnodes.pymodule_hello", ["john"], has_stdout=True, has_stderr=False
        )

        self.assertEqual(stdout, "hello john !", "wrong output")

    @test_utils.async_test
    @test_utils.timeout
    async def test_pymodule_hello_stderr(self):
        """Test running ``testnodes.pymodule_hello`` without arguments => print argparse help."""
        stdout, stderr = await self.call(
            "testnodes.pymodule_hello", has_stdout=False, has_stderr=True
        )

        self.assertIn("usage: hello [-h]", stderr, "wrong output")

    @test_utils.async_test
    @test_utils.timeout
    async def test_python_hello_intercom(self):
        """Test running ``testnodes.hello_intercom``."""
        # Manually start intercom server
        intercom = await start_intercom()
        async with intercom:
            # Create a pipe for stdout and stderr
            with PipeStream(rmode="r") as stdout:
                # Start process
                proc = await pygada_runtime.run(
                    "testnodes.hello_intercom",
                    stdout=stdout,
                    stderr=stdout,
                    intercom=intercom,
                )

                # Wait for process to be connected
                await intercom.wait_connected()

                # Send data via intercom
                write_json(intercom.writer, {"name": "john"})

                # Receive data from intercom
                data = await read_json(intercom.reader)
                self.assertEqual(data, {"hello": "john"}, "wrong response")

                # Wait for process to finish
                await proc.wait()

                stdout.eof()
                self.assertEqual(await stdout.read(), "", "should have no output")


if __name__ == "__main__":
    unittest.main()

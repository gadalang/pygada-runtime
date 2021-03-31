__all__ = ["RunnerTestCase"]
import os
import sys
import io
import asyncio
import unittest
import pygada_runtime
from pygada_runtime import PipeStream, write_packet, read_packet, test_utils


class RunnerTestCase(unittest.TestCase):
    async def run(
        self,
        argv
    ):
        # Run gada node
        stdout, stderr = await test_utils.run(argv)

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
    async def test_python_hello(self):
        """Test running ``testnodes.hello``."""
        stdout, stderr = self.run(["testnodes.hello", "john"], has_stdout=True, has_stderr=False)

        self.assertEqual(stdout, "hello john !", 'wrong output')

    @test_utils.async_test
    async def test_python_hello_stderr(self):
        """Test running ``testnodes.hello`` without arguments => print argparse help."""
        stdout, stderr = self.run(["testnodes.hello"], has_stdout=False, has_stderr=True)

        self.assertIn("usage: hello [-h]", stderr, 'wrong output')

    @test_utils.async_test
    async def test_pymodule_hello(self):
        """Test running ``testnodes.pymodule_hello``."""
        stdout, stderr = self.run(["testnodes.pymodule_hello", "john"], has_stdout=True, has_stderr=False)

        self.assertEqual(stdout, "hello john !", 'wrong output')

    @test_utils.async_test
    async def test_pymodule_hello_stderr(self):
        """Test running ``testnodes.pymodule_hello`` without arguments => print argparse help."""
        stdout, stderr = self.run(["testnodespymodule_hello"], has_stdout=False, has_stderr=True)

        self.assertIn("usage: hello [-h]", stderr, 'wrong output')


if __name__ == "__main__":
    unittest.main()

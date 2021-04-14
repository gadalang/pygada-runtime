import os
import sys
import io
import pytest
import asyncio
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


async def run(
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
        assert stderr == "", "should have no stderr"
    elif has_stderr is True:
        assert stderr != "", "should have stderr"
    if has_stdout is False:
        assert stdout == "", "should have no stdout"
    elif has_stdout is True:
        assert stdout != "", "should have stdout"

    return stdout.strip(), stderr.strip()


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_python_hello():
    """Test running ``testnodes.hello``."""
    stdout, stderr = await run(
        "testnodes.hello", ["john"], has_stdout=True, has_stderr=False
    )

    assert stdout == "hello john !", "wrong output"


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_python_hello_stderr():
    """Test running ``testnodes.hello`` without arguments => print argparse help."""
    stdout, stderr = await run("testnodes.hello", has_stdout=False, has_stderr=True)

    assert "usage: hello [-h]" in stderr, "wrong output"


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_pymodule_hello():
    """Test running ``testnodes.pymodule_hello``."""
    stdout, stderr = await run(
        "testnodes.pymodule_hello", ["john"], has_stdout=True, has_stderr=False
    )

    assert stdout == "hello john !", "wrong output"


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_pymodule_hello_stderr():
    """Test running ``testnodes.pymodule_hello`` without arguments => print argparse help."""
    stdout, stderr = await run(
        "testnodes.pymodule_hello", has_stdout=False, has_stderr=True
    )

    assert "usage: hello [-h]" in stderr, "wrong output"


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_python_hello_intercom():
    """Test running ``testnodes.hello_intercom``."""
    # Create a pipe for stdout and stderr
    with PipeStream(rmode="r") as stdout:
        # Start process
        proc = await pygada_runtime.run(
            "testnodes.hello_intercom", stdout=stdout, stderr=stdout, use_intercom=True
        )

        async with proc:
            intercom = proc.intercom

            # Wait for process to be connected
            await intercom.wait_connected()

            # Send data via intercom
            write_json(intercom.writer, {"name": "john"})

            # Receive data from intercom
            data = await read_json(intercom.reader)
            assert data == {"hello": "john"}, "wrong response"

            # Wait for process to finish
            await proc.wait()

            stdout.eof()
            assert (await stdout.read()) == "", "should have no output"

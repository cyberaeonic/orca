import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from opencode_bridge import run_prompt


class BridgeTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, source, prompt="hello", timeout="5"):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "fake-opencode"
            executable.write_text("#!/usr/bin/env python3\n" + source)
            executable.chmod(0o700)
            with patch.dict(os.environ, {
                "OPENCODE_BIN": str(executable), "OPENCODE_WORKDIR": directory,
                "OPENCODE_TIMEOUT_SECONDS": timeout, "DISCORD_TOKEN": "secret",
            }):
                return await run_prompt(prompt)

    async def test_reply_and_literal_prompt(self):
        result = await self.invoke(
            'import json, os, sys\n'
            'assert "DISCORD_TOKEN" not in os.environ\n'
            'assert sys.argv[-2] == "--"\n'
            'print(json.dumps({"type":"text","part":{"text":sys.argv[-1]}}))\n',
            "--help; $(echo no)",
        )
        self.assertEqual(result, "--help; $(echo no)")

    async def test_error_event(self):
        with self.assertRaises(RuntimeError):
            await self.invoke('print(\'{"type":"error"}\')\n')

    async def test_nonzero_exit(self):
        with self.assertRaises(RuntimeError):
            await self.invoke("raise SystemExit(1)\n")

    async def test_timeout(self):
        with self.assertRaises(TimeoutError):
            await self.invoke("import time\ntime.sleep(10)\n", timeout="1")

    async def test_output_limit(self):
        with self.assertRaises(RuntimeError):
            await self.invoke('print("x" * 2_100_000)\n')


if __name__ == "__main__":
    unittest.main()

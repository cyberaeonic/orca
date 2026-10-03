"""Non-interactive OpenCode process adapter for the Discord bot."""
import asyncio
import json
import os
import signal


async def run_prompt(prompt: str) -> str:
    if not prompt.strip():
        raise ValueError("Empty prompt")
    timeout = int(os.getenv("OPENCODE_TIMEOUT_SECONDS", "180"))
    if timeout < 1:
        raise ValueError("Timeout must be positive")
    args = [os.getenv("OPENCODE_BIN", "opencode"), "run", "--format", "json"]
    model = os.getenv("OPENCODE_MODEL", "").strip()
    if model:
        args.extend(["--model", model])
    args.extend(["--", prompt])
    env = dict(os.environ)
    env.pop("DISCORD_TOKEN", None)
    process = await asyncio.create_subprocess_exec(
        *args, cwd=os.getenv("OPENCODE_WORKDIR") or None, env=env,
        stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL, start_new_session=True,
    )

    async def collect():
        output = bytearray()
        while chunk := await process.stdout.read(65536):
            output.extend(chunk)
            if len(output) > 2_000_000:
                raise RuntimeError("OpenCode output limit exceeded")
        await process.wait()
        return output

    try:
        output = await asyncio.wait_for(collect(), timeout=timeout)
    finally:
        # Kill the process group too: tools can leave child processes running.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        await process.wait()
    if process.returncode:
        raise RuntimeError("OpenCode exited unsuccessfully")
    texts = []
    for line in output.decode("utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "error":
            raise RuntimeError("OpenCode reported an error")
        part = event.get("part")
        if event.get("type") == "text" and isinstance(part, dict):
            text = part.get("text")
            if isinstance(text, str):
                texts.append(text)
    return "\n\n".join(texts).strip() or "OpenCode finished without a text reply."

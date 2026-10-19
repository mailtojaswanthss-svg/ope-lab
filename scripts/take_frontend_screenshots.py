"""Automated high-fidelity screenshot capture for OPE Lab React Frontend via Chrome DevTools Protocol."""

import asyncio
import base64
import json
import subprocess
import time
from pathlib import Path

import requests
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = Path(__file__).parent.parent / "screenshots"


def get_ws_url() -> str:
    """Fetches active Chrome DevTools page websocket URL."""
    resp = requests.get("http://127.0.0.1:9222/json", timeout=5)
    pages = resp.json()
    page_target = next(p for p in pages if p.get("type") == "page")
    return str(page_target["webSocketDebuggerUrl"])


async def capture_target(ws_url: str, target_url: str, output_path: Path, wait_sec: float = 3.0) -> None:
    """Navigates to URL, waits for render, and captures full-page screenshot."""
    async with websockets.connect(ws_url, max_size=30_000_000) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
        await ws.recv()

        await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {"url": target_url}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 2:
                break

        await asyncio.sleep(wait_sec)

        await ws.send(json.dumps({"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 3:
                img_data = base64.b64decode(msg["result"]["data"])
                output_path.write_bytes(img_data)
                print(f"Captured: {output_path.name} ({len(img_data):,} bytes)")
                break


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    temp_profile = Path(r"C:\TEMP\chrome_cdp_profile_fe")
    temp_profile.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9222",
        f"--user-data-dir={temp_profile}",
        "--window-size=1440,1100",
        "--hide-scrollbars",
        "about:blank",
    ])

    time.sleep(2.0)

    try:
        ws_url = get_ws_url()
        targets = [
            ("http://localhost:8443/#/home", OUTPUT_DIR / "frontend_home.png", 3.0),
            ("http://localhost:8443/#/story", OUTPUT_DIR / "frontend_story.png", 3.0),
            ("http://localhost:8443/#/estimators", OUTPUT_DIR / "frontend_estimators.png", 3.0),
            ("http://localhost:8443/#/lab", OUTPUT_DIR / "frontend_lab.png", 3.5),
            ("http://localhost:8443/#/studies", OUTPUT_DIR / "frontend_studies.png", 4.0),
            ("http://localhost:8443/#/real-data", OUTPUT_DIR / "frontend_real_data.png", 3.0),
        ]

        for url, path, wait_time in targets:
            asyncio.run(capture_target(ws_url, url, path, wait_sec=wait_time))

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()

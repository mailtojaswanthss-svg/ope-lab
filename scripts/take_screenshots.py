"""Automated high-fidelity screenshot capture for OPE Lab using Chrome DevTools Protocol."""

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
    """Fetches the active Chrome DevTools page websocket URL."""
    resp = requests.get("http://127.0.0.1:9222/json", timeout=5)
    pages = resp.json()
    page_target = next(p for p in pages if p.get("type") == "page")
    return str(page_target["webSocketDebuggerUrl"])


async def capture_target(ws_url: str, target_url: str, output_path: Path, wait_sec: float = 3.5) -> None:
    """Navigates to the target URL, waits for Streamlit rendering, and captures screenshot."""
    async with websockets.connect(ws_url, max_size=25_000_000) as ws:
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
    temp_profile = Path(r"C:\TEMP\chrome_cdp_profile")
    temp_profile.mkdir(parents=True, exist_ok=True)

    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9222",
        f"--user-data-dir={temp_profile}",
        "--window-size=1440,1250",
        "--hide-scrollbars",
        "about:blank",
    ])

    time.sleep(2.0)

    try:
        ws_url = get_ws_url()
        targets = [
            ("http://localhost:8501/?tab=results&preset=easy", OUTPUT_DIR / "results_easy_rct.png", 4.0),
            ("http://localhost:8501/?tab=results&preset=low", OUTPUT_DIR / "results_low_overlap.png", 4.0),
            ("http://localhost:8501/?tab=results&preset=trap", OUTPUT_DIR / "results_confounder_trap.png", 4.0),
            ("http://localhost:8501/?tab=results&preset=trap&theme=light", OUTPUT_DIR / "results_light_mode.png", 4.0),
            ("http://localhost:8501/?tab=overview", OUTPUT_DIR / "overview_hero.png", 3.0),
            ("http://localhost:8501/?tab=failure", OUTPUT_DIR / "failure_study.png", 6.0),
            ("http://localhost:8501/?tab=failure&theme=light", OUTPUT_DIR / "failure_study_light.png", 6.0),
            ("http://localhost:8501/?tab=decision", OUTPUT_DIR / "decision_map.png", 6.0),
            ("http://localhost:8501/?tab=decision&theme=light", OUTPUT_DIR / "decision_map_light.png", 6.0),
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

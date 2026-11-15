"""Slide charts G1-G7 for PPM_Talk_HSG.pptx -> charts/<name>.svg and charts/<name>.png (300 dpi).

The charts are drawn by the frontend page /charts (src/routes/charts/+page.svelte) from
    frontend/src/lib/slides.json         written by slides.py (rerun only if it is missing)
    frontend/src/lib/charts_extra.json   written here: BPIC 2011 test counts (G5),
                                         columns / training cases per encoding (G6),
                                         registration-feature names (G7)
This script writes the extra numbers, starts the dev server if it is not running, saves every
<svg id="G…"> on the page as SVG and as a PNG at placeholder size x 300 dpi, then stops the
server again (only if it started it).

    pip install playwright pillow
    python make_charts.py
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
import warnings
from pathlib import Path

from data import load_dataset, prefix_log
from experiment import encode_prefixes, test_counts

HERE = Path(__file__).parent
FRONTEND = HERE / "frontend"
SLIDES_JSON = FRONTEND / "src" / "lib" / "slides.json"
EXTRA_JSON = FRONTEND / "src" / "lib" / "charts_extra.json"
OUT = HERE / "charts"
URL = "http://localhost:5173/charts"
DPI = 300


def extra_numbers():
    sep = load_dataset("sepsis")
    bpic = load_dataset("bpic2011")
    K = range(1, sep.max_k + 1)

    # G6: vector length and training cases per model, Sepsis without initial data
    train_prefixes = {k: sum(1 for i in prefix_log(sep, k).case_id.unique() if i in sep.train_ids) for k in K}
    all_lengths = sum(train_prefixes.values())   # last state / aggregation: one model over all lengths
    index_overfit = [{
        "k": k,
        "columns": {e: int(encode_prefixes(sep, e, k, initial="none").shape[1])
                    for e in ("last_state", "aggregation", "index")},
        "train_cases": {"last_state": all_lengths, "aggregation": all_lengths, "index": train_prefixes[k]},
    } for k in K]

    return {
        "bpic_test_counts": [{"k": k, "cases": n, "positives": p} for k, (n, p) in test_counts(bpic).items()],
        "index_overfit": index_overfit,
        "registration_features": sep.initial_sets["all"],
    }


def server_up():
    try:
        return urllib.request.urlopen(URL, timeout=3).status == 200
    except Exception:
        return False


def start_server():
    proc = subprocess.Popen("npm run dev -- --port 5173 --strictPort", cwd=FRONTEND, shell=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(90):
        if server_up():
            return proc
        time.sleep(1)
    stop_server(proc)
    raise SystemExit("dev server did not start; run `npm run dev` in frontend/ and try again")


def stop_server(proc):
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        proc.terminate()


def export():
    from PIL import Image
    from playwright.sync_api import sync_playwright

    OUT.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome")
        except Exception:
            browser = pw.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1000, "height": 800}, device_scale_factor=DPI / 96)
        page.goto(URL, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        for svg in page.locator("svg[id^='G']").all():
            name = svg.get_attribute("id")
            # drop the on-screen pixel style so the file keeps its size in inches
            markup = re.sub(r' style="[^"]*"', "", svg.evaluate("el => el.outerHTML"), count=1)
            (OUT / f"{name}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + markup, encoding="utf-8")
            png = OUT / f"{name}.png"
            svg.scroll_into_view_if_needed()
            svg.screenshot(path=str(png))
            # crop sub-pixel rounding to the exact placeholder size and store 300 dpi,
            # so PowerPoint inserts it 1:1 into the placeholder
            w_in, h_in = (float(svg.get_attribute(a).removesuffix("in")) for a in ("width", "height"))
            size = (round(w_in * DPI), round(h_in * DPI))
            with Image.open(png) as im:
                im = im.convert("RGB").crop((0, 0, *size))
            im.save(png, dpi=(DPI, DPI))
            print(f"saved {name}  {size[0]} x {size[1]} px  ({w_in} x {h_in} in)")
        browser.close()


def main():
    warnings.filterwarnings("ignore")
    if not SLIDES_JSON.exists():
        import slides
        slides.main()
    EXTRA_JSON.write_text(json.dumps(extra_numbers(), indent=1))
    proc = None if server_up() else start_server()
    try:
        export()
    finally:
        if proc:
            stop_server(proc)


if __name__ == "__main__":
    main()

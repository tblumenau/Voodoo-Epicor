#!/usr/bin/env python3
import os
import sys
import time

import requests
from requests.auth import HTTPBasicAuth


def epicor_baq_v2_odata(
    base_url: str,
    company: str,
    baq_name: str,
    queue_id: str,
    username: str | None = None,
    password: str | None = None,
    api_key: str | None = None,
    bearer_token: str | None = None,
    timeout_s: int = 30,
) -> list[dict]:
    """
    Query an Epicor BAQ via REST v2 OData:
      GET {base_url}/api/v2/odata/{company}/BaqSvc/{baq_name}/Data?$filter=QueueID eq <queue_id>
    """
    try:
        int(queue_id)
        filter_expr = f"QueueID eq {queue_id}"
    except ValueError:
        filter_expr = f"QueueID eq '{queue_id}'"

    url = f"{base_url.rstrip('/')}/api/v2/odata/{company}/BaqSvc/{baq_name}/Data"
    params = {"$filter": filter_expr}

    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-KEY"] = api_key
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    auth = HTTPBasicAuth(username, password) if (username and password) else None
    r = requests.get(url, headers=headers, params=params, auth=auth, timeout=timeout_s)
    r.raise_for_status()

    payload = r.json()
    return payload.get("value", [])


def voodoo_flash_device(
    base_url: str,
    api_key: str,
    device_id: str,
    *,
    lines: list[str] | None = None,
    seconds: int = 10,
    color: str = "g",
    sound: str = "none",
    barcode: str | None = None,
    quantity: int | None = None,
    qrcode: str | None = None,
    arrow: str | None = None,
    timeout_s: int = 15,
) -> dict:
    """
    Flash a Voodoo device using the REST API pattern:
      POST {base_url}/device/{device_id}/
    with header:
      API-KEY: <key>
    and payload fields like command/seconds/color/sound/line1..line5, etc. :contentReference[oaicite:2]{index=2}
    """
    if not device_id:
        raise ValueError("device_id is blank")

    url = f"{base_url.rstrip('/')}/device/{device_id.strip()}/"

    headers = {
        "API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload: dict = {
        "api": "2.0",
        "command": "flash",
        "seconds": int(seconds),
        "color": color,
        "sound": sound,
    }

    if lines:
        # up to 5 lines
        for idx, line in enumerate(lines[:5], start=1):
            payload[f"line{idx}"] = str(line)

    # Optional “modern” fields
    if barcode:
        payload["barcode"] = barcode
    if quantity is not None:
        payload["quantity"] = int(quantity)
    if qrcode:
        payload["qrcode"] = qrcode
    if arrow:
        payload["arrow"] = arrow

    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    r.raise_for_status()
    # Some deployments return JSON; if not, fall back to text
    try:
        return r.json()
    except Exception:
        return {"status_code": r.status_code, "text": r.text}


def main():
    # Epicor BAQ config
    EPICOR_BASE = os.environ.get(
        "EPICOR_BASE_URL", "https://your-epicor-server/YourInstance"
    )
    EPICOR_COMPANY = os.environ.get("EPICOR_COMPANY", "EPIC06")
    EPICOR_BAQ = os.environ.get("EPICOR_BAQ", "VODOO_PickListByQueueID")

    EPICOR_USER = os.environ.get("EPICOR_USER")
    EPICOR_PASS = os.environ.get("EPICOR_PASS")
    EPICOR_API_KEY = os.environ.get("EPICOR_API_KEY")
    EPICOR_BEARER = os.environ.get("EPICOR_BEARER_TOKEN")

    # Voodoo (Big Block / VoodooDevices) config
    # The docs show the REST API rooted at https://www.voodoodevices.com/api/ :contentReference[oaicite:3]{index=3}
    # For your own server/demo, set VOODOO_BASE_URL accordingly (must end with /api or equivalent).
    VOODOO_BASE = os.environ.get("VOODOO_BASE_URL", "https://www.voodoodevices.com/api")
    VOODOO_API_KEY = os.environ.get("VOODOO_API_KEY")
    if not VOODOO_API_KEY:
        print("ERROR: set VOODOO_API_KEY in your environment")
        return 2

    # Behavior toggles
    DRY_RUN = os.environ.get("DRY_RUN", "0").strip() in ("1", "true", "yes", "on")
    DEFAULT_SECONDS = int(os.environ.get("VOODOO_SECONDS", "20"))
    DEFAULT_COLOR = os.environ.get("VOODOO_COLOR", "g")
    DEFAULT_SOUND = os.environ.get("VOODOO_SOUND", "none")

    if len(sys.argv) >= 2:
        queue_id = sys.argv[1]
    else:
        queue_id = input("Scan/enter Picklist (Queue) ID: ").strip()

    rows = epicor_baq_v2_odata(
        base_url=EPICOR_BASE,
        company=EPICOR_COMPANY,
        baq_name=EPICOR_BAQ,
        queue_id=queue_id,
        username=EPICOR_USER,
        password=EPICOR_PASS,
        api_key=EPICOR_API_KEY,
        bearer_token=EPICOR_BEARER,
    )

    if not rows:
        print(f"No rows found for QueueID={queue_id}")
        return 1

    # Light each row’s device (DeviceID_c from PartBin.DeviceID_c)
    failures = 0
    for i, row in enumerate(rows, start=1):
        part = row.get("PartNum", "")
        desc = row.get("PartDescription", "")
        qty = row.get("RequiredQty", "")
        whse = row.get("FromWhse", "")
        bin_ = row.get("FromBin", "")

        device_id = (
            row.get("DeviceID_c")
            or row.get("PartBin_DeviceID_c")
            or row.get("DeviceID")
            or ""
        ).strip()

        if not device_id:
            failures += 1
            print(f"[{i}] SKIP (no DeviceID_c) {part} qty={qty} loc={whse}:{bin_}")
            continue

        # Keep lines short; devices truncate long lines (per docs). :contentReference[oaicite:4]{index=4}
        lines = [
            f"{part}  x{qty}",
            f"{whse}:{bin_}",
        ]
        if desc:
            lines.append(str(desc)[:26])

        if DRY_RUN:
            print(f"[{i}] DRY_RUN would flash {device_id} -> {lines}")
            continue

        try:
            resp = voodoo_flash_device(
                base_url=VOODOO_BASE,
                api_key=VOODOO_API_KEY,
                device_id=device_id,
                lines=lines,
                seconds=DEFAULT_SECONDS,
                color=DEFAULT_COLOR,
                sound=DEFAULT_SOUND,
                # Optional: barcode=qrcode=arrow=quantity=... if you want
            )
            print(f"[{i}] OK flashed {device_id} ({part} x{qty} @ {whse}:{bin_})")
        except requests.HTTPError as e:
            failures += 1
            body = ""
            try:
                body = e.response.text  # type: ignore[attr-defined]
            except Exception:
                pass
            print(f"[{i}] FAIL flashing {device_id}: {e}\n{body}")
        except Exception as e:
            failures += 1
            print(f"[{i}] FAIL flashing {device_id}: {e}")

        # Gentle pacing so you don’t hammer the API
        time.sleep(0.05)

    if failures:
        print(f"\nDone. Failures/skips: {failures} of {len(rows)}")
        return 3

    print(f"\nDone. Flashed {len(rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Python example: enter/scan ID → fetch lines from Epicor → print them
# Below is a working-style template that supports:
#     • typing/scanning an ID
#     • calling Epicor REST
#     • printing a pickable list
# Option 1: REST v2 OData BAQ (recommended)
# Assumptions:
#     • You created a BAQ named VODOO_PickListByQueueID or use and existing BAQ
#     • It returns columns like: QueueID, PartNum, PartDescription, RequiredQty, FromWhse, FromBin
#     • You filter it using OData $filter=QueueID eq 12345 (or whatever your BAQ outputs)

#!/usr/bin/env python3
import os
import sys
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
    # NOTE: quote QueueID if it is a string key in your BAQ output, e.g. QueueID eq '000123'
    # Here we treat it as numeric when possible.
    try:
        int(queue_id)
        filter_expr = f"QueueID eq {queue_id}"
    except ValueError:
        filter_expr = f"QueueID eq '{queue_id}'"

    url = f"{base_url.rstrip('/')}/api/v2/odata/{company}/BaqSvc/{baq_name}/Data"
    params = {"$filter": filter_expr}

    headers = {"Accept": "application/json"}
    # Many Epicor REST v2 setups use an API key header (commonly X-API-KEY).
    # Your admin/security config determines the exact header name/value.
    if api_key:
        headers["X-API-KEY"] = api_key  # commonly used name in REST v2 connectors
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    auth = HTTPBasicAuth(username, password) if (username and password) else None
    r = requests.get(url, headers=headers, params=params, auth=auth, timeout=timeout_s)
    r.raise_for_status()

    payload = r.json()
    # OData responses usually put rows under "value"
    return payload.get("value", [])

def main():
    # Example env vars so you don't hardcode secrets
    EPICOR_BASE = os.environ.get("EPICOR_BASE_URL", "https://your-epicor-server/YourInstance")
    EPICOR_COMPANY = os.environ.get("EPICOR_COMPANY", "EPIC06")
    EPICOR_BAQ = os.environ.get("EPICOR_BAQ", "VODOO_PickListByQueueID")

    EPICOR_USER = os.environ.get("EPICOR_USER")          # optional if using API key/token only
    EPICOR_PASS = os.environ.get("EPICOR_PASS")          # optional if using API key/token only
    EPICOR_API_KEY = os.environ.get("EPICOR_API_KEY")    # if configured
    EPICOR_BEARER = os.environ.get("EPICOR_BEARER_TOKEN")# if you’re doing token auth

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

    print(f"\nPick List for QueueID {queue_id}\n" + "-" * 60)
    for i, row in enumerate(rows, start=1):
        part = row.get("PartNum", "")
        desc = row.get("PartDescription", "")
        qty  = row.get("RequiredQty", "")
        whse = row.get("FromWhse", "")
        bin_ = row.get("FromBin", "")

        print(f"{i:>3}. {part}  qty={qty}  loc={whse}:{bin_}")
        if desc:
            print(f"     {desc}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

# Why BAQ is the right “integration seam”:
#     • You don’t need to perfectly understand every underlying table/relationship in your Python code.
#     • You can adapt per-customer: some customers want “from bin”, others want “suggested bin”, others want lot/serial rules, etc.
#     • Epicor users explicitly call out BAQSvc as a good integration approach. Epicor User Help Forum+1


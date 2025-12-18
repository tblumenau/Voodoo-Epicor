# Voodoo Pick-To-Light + Epicor Integration Starter

This repository is a lightweight starting point for connecting Voodoo Pick-To-Light devices to Epicor so warehouse and kitting workers can move faster with fewer mistakes. It includes a small Python script that pulls Epicor pick data and drives Voodoo devices through their REST API, plus notes on how to shape your Epicor data so each bin or part/bin has an associated device.

## What Voodoo Pick-To-Light devices do

Voodoo devices mount at bins or workstations and light up with clear, per-task instructions. Typical uses on the floor include:

- **Picking**: A queue or pick list is scanned, the correct bin lights up, and the display shows the part number, quantity, and location so the worker can pick without cross-referencing paper.
- **Kitting**: Assemblers or kitters are guided bin-by-bin, reducing walking time and ensuring the right components are pulled in order.
- **Exception handling**: Color and sound cues make shortages or alternates obvious and give leads an easy way to spot blockers.

When driven directly from Epicor, these devices remove manual lookups and paper lists. The result is faster throughput, fewer mispicks, and a clearer audit trail because the device payloads come straight from Epicor’s material queue data.

## How Epicor fits in

Epicor already tracks which parts and quantities need to be issued and where they should come from. A common pattern is:

1. **Queue-based picking**: Use Epicor’s Material Request Queue / Material Queue so each pick line has a queue ID (often scanned on the floor).
2. **BAQ for pick data**: Build a Business Activity Query that accepts the queue ID and returns the fields the devices need—part number, description, required quantity, warehouse/bin, and a device identifier (for example `DeviceID_c` on `PartBin`).
3. **REST access**: Expose that BAQ over Epicor REST (OData v2 or the DataList pattern) so a lightweight client can read it.

This repository’s sample script follows exactly that flow: it takes a queue ID, calls your BAQ, and flashes each referenced device with the part, quantity, and bin pulled from Epicor.

## Repository layout

- `lightDevices.py` – Minimal Python example that:
  - Calls an Epicor BAQ via REST v2 OData using provided credentials.
  - Iterates the returned rows and flashes each Voodoo device (`/device/<device_id>/` endpoint) with the part, quantity, and location.
  - Supports dry-run mode so you can validate Epicor connectivity before lighting devices.
- `doc/` – Reference notes about Epicor BAQs, adding a `DeviceID` field to `PartBin`, and typical Material Queue workflows.

## Getting started

1. **Create or confirm a BAQ** that accepts a queue ID (or job number) and returns at least `PartNum`, `PartDescription`, `RequiredQty`, `FromWhse`, `FromBin`, and a device identifier such as `DeviceID_c` from `PartBin`.
2. **Expose the BAQ over REST** (Epicor REST help is usually available at `/apps/resthelp/`) and make sure your user/API key can call it.
3. **Configure environment variables** for the sample script:
   - Epicor: `EPICOR_BASE_URL`, `EPICOR_COMPANY`, `EPICOR_BAQ`, and one of (`EPICOR_USER`/`EPICOR_PASS`, `EPICOR_API_KEY`, or `EPICOR_BEARER_TOKEN`).
   - Voodoo: `VOODOO_BASE_URL` (default `https://www.voodoodevices.com/api`) and `VOODOO_API_KEY`.
   - Behavior: `DRY_RUN` (true/false), `VOODOO_SECONDS`, `VOODOO_COLOR`, `VOODOO_SOUND`.
4. **Run the example**:

   ```bash
   python3 lightDevices.py <QueueID>
   ```

   The script fetches the matching Epicor rows and flashes each device. In dry-run mode it prints what it would send without contacting the devices.

## Why this improves speed and accuracy

- **Fewer touches**: No paper pick lists or manual bin lookups—workers scan the Epicor queue ID and follow the lights.
- **Clear per-line guidance**: Part, quantity, and bin are displayed on the device, reducing verbal handoffs and rereads of the screen.
- **Immediate error visibility**: Color and sound cues highlight shortages or wrong-bin attempts so supervisors can intervene quickly.
- **Same-source-of-truth**: Because the payloads come directly from Epicor’s queue/BAQ data, the devices always reflect the current plan (including re-allocations or substitutions).

## Adapting it to your site

- Map your device IDs to bins or part/bin rows in Epicor (for example with a `DeviceID_c` UD field on `PartBin`).
- Adjust the BAQ and payload to include additional fields (barcodes, arrows, or quantities) that your devices support.
- Integrate this script into your existing Epicor automation (e.g., Fulfillment Workbench releases) or wrap it in a small service/daemon for continuous processing.

With these pieces in place, this repo gives you a practical baseline for marrying Voodoo Pick-To-Light hardware with Epicor’s picking and kitting workflows.

## What the kitting worker actually does in the Epicor GUI (typical)

There are a couple variants, but the common pattern looks like:

1.  **Demand is created** (job materials need to be issued to a
    job/assembly).

2.  Epicor creates **Material Queue** records (think: “work to
    pick/issue”).

3.  A warehouse/materials person opens **Material Request Queue / My
    Material Queue** (or similar Kinetic “Material Queue” app) and
    processes lines (pick/issue). <a
    href="https://docs.biscit.com/epicor-kinetic-warehouse/epicor-kinetic-warehouse-user-guide/material-queues-mtl-queues"
    target="_blank">BISCIT+1</a>

4.  In practice, they often **scan the Material Queue sequence/ID** to
    pull up the exact record(s) to process.
    <a href="https://www.epiusers.help/t/how-do-you-pick-an-order/84511"
    target="_blank">Epicor User Help Forum+1</a>

Epicor’s Fulfillment Workbench is commonly used as the
“allocator/releaser” that feeds these queues for Jobs (and Sales Orders
/ Transfers). <a
href="https://www.estesgrp.com/blog/manage-inventory-using-epicor-fulfillment-workbench/"
target="_blank">estesgrp.com</a>

## What this means in the Epicor database (typical)

The data you usually need comes from a join like:

-   **Material Queue** table (often named something like `MtlQueue`)  
    Holds the queue/sequence ID and the demand reference
    (job/assembly/material line), plus “from” location hints
    (warehouse/bin) depending on configuration.

-   **Job material requirement** table (often `JobMtl`)  
    Holds the BOM requirement: part, qty required, qty issued, assembly,
    etc.

-   **Part master** (often `Part`)  
    Description/UOM/etc.

-   **Bin/location inventory** (often `PartBin` and bin/warehouse
    tables)  
    Where it can be picked from; on-hand by bin.

Exact field names vary by version/config, but this is the standard
conceptual model Epicor users build BAQs against (and Epicor even
teaches “how to find/link tables” via field help / relationships). <a
href="https://www.youtube.com/watch?v=Bc-mHYG2Z6g&amp;utm_source=chatgpt.com"
target="_blank">YouTube</a>

## “Pick List” — does it have an ID? Is it stored in a table?

In many Epicor shops, the thing that gets printed and handed to a picker
is effectively a **pick list report** *for* either:

-   a **Job**, or

-   a set of **Material Queue** records

…and the ID you can reliably scan is commonly the **Material Queue
sequence/ID**.
<a href="https://www.epiusers.help/t/how-do-you-pick-an-order/84511"
target="_blank">Epicor User Help Forum+1</a>

So: yes, there’s an ID, but the ID you’ll want to target in your
integration is often **Queue ID / MtlQueueSeq**.

## Does the printout have a barcode?

Often **yes** in real deployments (because scanning is common), but
whether the barcode prints by default depends on:

-   which report they use (Job Pick List vs queue-driven picking),

-   and how the report was customized.

What we *can* say confidently is that scanning the queue sequence/ID is
a normal workflow people mention in Epicor environments.
<a href="https://www.epiusers.help/t/how-do-you-pick-an-order/84511"
target="_blank">Epicor User Help Forum+1</a>

------------------------------------------------------------------------

# The clean integration approach for a Python program

You want: input ID → return lines with **SKU/desc, qty, pick location**.

The most robust way to do this in Epicor is:

1.  **Create a BAQ** (Business Activity Query) that accepts a parameter
    like `QueueID` (or `JobNum`) and returns exactly the columns you
    want.

2.  Call that BAQ via **Epicor REST** from Python.

Epicor folks explicitly recommend BAQSvc as an integration-friendly
“schema-controlled endpoint.”
<a href="https://www.epiusers.help/t/using-rest-in-an-integration/46209"
target="_blank">Epicor User Help Forum</a>

## REST endpoint shape (what you’ll hit)

Two common patterns you’ll see in the wild:

### Pattern A: REST v2 OData BAQ endpoint

Example shared by Epicor users:  
`https://yourserver/.../api/v2/odata/<Company>/BaqSvc/<BAQName>/Data` <a
href="https://www.epiusers.help/t/rest-efx-baq-examples-from-a-python-script/115273"
target="_blank">Epicor User Help Forum</a>

### Pattern B: REST v1 BAQ “DataList\_…” endpoint

Example seen in code in the community:  
`https://.../api/v1/BaqSvc/DataList_<BAQName>/?Param='...'` <a
href="https://www.epiusers.help/t/rest-api-with-single-sign-on/126873"
target="_blank">Epicor User Help Forum</a>

Also: your Epicor instance normally exposes interactive Swagger/help at
a `/apps/resthelp/` style URL. <a
href="https://www.epiusers.help/t/list-of-all-business-objects-rest-api/106542"
target="_blank">Epicor User Help Forum+1</a>

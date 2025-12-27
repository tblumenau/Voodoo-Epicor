### Where “FromBin” in a BAQ usually comes from

In the common **manufacturing pick / issue-to-job** flow in Epicor, the
“from” location is typically sourced from the **material request /
material queue** record (the thing driving the request), and/or from the
**inventory-by-bin** record (the thing proving what’s actually on-hand).

Concretely, in many implementations:

-   **Material Request Queue / Material Queue** holds the *requested*
    “from” location fields (users can pick/adjust a From Bin during
    fulfillment). You’ll often see people discussing “From Bin” in the
    context of the Material Request Queue screen and its backing data.
    <a
    href="https://www.epiusers.help/t/adding-qtyonhand-to-material-request-queue/113302"
    target="_blank">Epicor User Help Forum</a>

-   **PartBin** holds the *actual* on-hand by **Part + Warehouse + Bin**
    (QtyOnHand, etc.), and is frequently joined in BAQs to show
    availability by bin.
    <a href="https://www.epiusers.help/t/total-onhandqty/103538"
    target="_blank">Epicor User Help Forum+1</a>

So: if your BAQ has a field literally called **FromBin**, it’s *very
often* coming from the “request/queue” side; if your BAQ is showing
**BinNum / QtyOnHand** it’s often coming from **PartBin**.

------------------------------------------------------------------------

## Adding `DeviceID` onto `Erp.PartBin` (database enhancement)

> **Don’t have to store it in Epicor:** If you simply need a
> human-readable mapping between bins and device IDs, you can avoid
> adding a UD column entirely by using the **location naming facility in
> Big Block**. Name the bin/location to include the DeviceID and let Big
> Block resolve it—no DeviceID column required in Epicor. If you prefer a
> first-class field in Epicor for reporting/searching, continue with the
> steps below.

### Best-practice Epicor way: add a UD column to PartBin

1.  In **UD Field/Column Maintenance**, add a UD column to the
    **Erp.PartBin** table:

    -   Field name: `DeviceID` (Epicor will surface it as something like
        `DeviceID_c`)

    -   Type: likely `nvarchar`/string (whatever length your Voodoo
        Device IDs need)

2.  Regenerate/rebuild the data model so the new field physically exists
    and becomes bindable in UI datasets (in Epicor Cloud this is often a
    support-requested rebuild; on-prem it’s an admin action + appserver
    recycle). <a
    href="https://www.epiusers.help/t/ud-field-customer-maintenance-on-the-cloud/65358"
    target="_blank">Epicor User Help Forum</a>

3.  Confirm it appears everywhere you need it:

    -   Classic UI EpiBinding fields

    -   Kinetic dataview / layers

That gives you a real field **on the PartBin row**, which is nice
because it’s exactly where a worker thinks about it: “this *bin* has a
*device* assigned.”

------------------------------------------------------------------------

## Enhancing the GUI so workers can edit `DeviceID_c`

### Option A (fastest): Kinetic personalization for specific users/roles

-   If the UD column is in the dataview, users can often add it as a
    column/field via personalization. <a
    href="https://www.epiusers.help/t/kinetic-adding-existing-ud-fields-to-order-entry-screen/121735"
    target="_blank">Epicor User Help Forum</a>  
    Downside: it’s per-user (unless you manage personalization
    deployment carefully).

### Option B (better operationally): Kinetic customization layer so it’s “just there”

1.  Open the relevant Kinetic screen (commonly something like **Bin
    Maintenance**, **Part Bin**, or whatever your team uses
    operationally).

2.  Create a **Customization Layer** that:

    -   Adds a text field labeled **Device ID**

    -   Binds it to `PartBin.DeviceID_c`

    -   Makes it editable

3.  Add basic guardrails:

    -   Only allow edit for the warehouse worker security group

    -   Optional: validate format (length/prefix/checksum) and show an
        error if invalid

    -   Optional: uniqueness rule (one DeviceID can only exist in one
        bin) enforced via BPM/DB constraint

This approach is specifically recommended when you want fields visible
“by default” to everyone who uses that screen, instead of relying on
each user’s personalization. <a
href="https://www.epiusers.help/t/kinetic-adding-existing-ud-fields-to-order-entry-screen/121735"
target="_blank">Epicor User Help Forum</a>

### Option C (often best for the floor): a tiny “Device Assignment” app/dashboard

Instead of exposing PartBin maintenance, make a purpose-built page:

-   Scan **Bin barcode** (or type Warehouse+Bin)

-   Scan/enter **DeviceID**

-   Save (updates PartBin.DeviceID\_c)  
    This is usually done with a **BAQ + Updateable BAQ (UBAQ)** and/or a
    small REST call + BPM validation.

------------------------------------------------------------------------

## One important design decision before you commit to PartBin

Storing DeviceID on **PartBin** means the assignment is per
*Part+Bin+Warehouse*. If your bins contain multiple parts, or your
“device belongs to the physical bin regardless of part,” you may prefer
to store DeviceID against the **Bin master** (if you have one) or a
small UD table keyed by `(WarehouseCode, BinNum)`.

If your operation is “one device mounted to a physical bin location,”
that bin-keyed approach is often cleaner. If your operation is “device
attached to a part/bin pair,” PartBin is fine.

  

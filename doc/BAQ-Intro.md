# Epicor BAQs: Background, Usage, and Creation Guide

## What is a BAQ?

A **BAQ (Business Activity Query)** is Epicor’s built‑in query mechanism
for retrieving, shaping, and exposing business data from the Epicor ERP
database *without writing raw SQL*. A BAQ defines **what data to pull**,
**how tables are joined**, **how data is filtered**, and **how results
are presented**.

Think of a BAQ as:

-   A **safe, supported abstraction layer** over the Epicor database

-   A reusable **data contract** that can be consumed by screens,
    dashboards, reports, BPMs, REST APIs, and external programs

BAQs are central to Epicor’s extensibility story. If you want data *out*
of Epicor in a reliable way, a BAQ is usually the correct first step.

------------------------------------------------------------------------

## Why BAQs Exist (Background)

Epicor runs on a large, highly‑normalized relational database. Allowing
users (or integrations) to run arbitrary SQL directly would:

-   Break upgrades

-   Bypass security rules

-   Risk performance problems

-   Create fragile integrations

BAQs solve this by:

-   Enforcing **Epicor security** (row‑level, company, plant)

-   Remaining **upgrade‑safe**

-   Being **inspectable and supportable** by Epicor admins

-   Acting as a **stable interface** between Epicor and the outside
    world

Because of this, Epicor heavily encourages *all integrations* to be
built on BAQs rather than direct database access.

------------------------------------------------------------------------

## How BAQs Are Used

BAQs are used in many places inside and outside Epicor:

### Inside Epicor

-   Dashboards and grids

-   SSRS and Crystal Reports

-   BPMs (Business Process Management)

-   Data Directives

-   Kinetic UI widgets

### Outside Epicor

-   REST API calls (via `BAQSvc` or OData)

-   Python, Java, C#, or Node integrations

-   Warehouse systems (WMS)

-   MES systems

-   BI / analytics pipelines

In integrations (like Voodoo ↔ Epicor), a BAQ becomes a **query
endpoint** that external code can safely call to retrieve structured
data such as:

-   Pick lists

-   Job materials

-   Inventory locations

-   Order lines

------------------------------------------------------------------------

## Types of BAQs

Epicor supports several BAQ types, but the most common are:

### 1. Simple BAQs

-   Read‑only

-   Query one or more tables

-   Used for reporting or data extraction

### 2. Parameterized BAQs

-   Accept input parameters (e.g., JobNum, PickListID)

-   Ideal for integrations and user‑driven queries

### 3. Updatable BAQs (Advanced)

-   Allow controlled updates back into Epicor tables

-   Require careful setup and permissions

-   Often used with BPMs

For most integrations, **parameterized, read‑only BAQs** are the correct
choice.

------------------------------------------------------------------------

## Core Concepts You Must Understand

### Tables

Epicor exposes business entities as tables (e.g., `JobHead`, `JobMtl`,
`Part`, `WhseBin`). BAQs are built by selecting and joining these
tables.

### Joins

You explicitly define how tables relate (inner join, left join, etc.).
Incorrect joins are the \#1 source of bad BAQs.

### Filters

Filters restrict rows (e.g., only open jobs, only a specific pick list).

### Display Fields

You choose which fields appear in the result set and how they are
labeled.

### Calculated Fields

You can add derived fields using Epicor’s expression language.

### Parameters

Parameters allow external callers or users to inject values at runtime.

------------------------------------------------------------------------

## Step‑by‑Step: Creating a BAQ

### Step 1: Open the BAQ Designer

In Epicor:

System Management → Business Activity Queries

Create a **New Query** and give it a meaningful ID, e.g.:

Voodoo\_PickListDetail

------------------------------------------------------------------------

### Step 2: Add Tables

1.  Go to the **Query Builder** tab

2.  Add your primary table (e.g., `JobMtl`)

3.  Add related tables (e.g., `Part`, `WhseBin`)

Be intentional: only add tables you actually need.

------------------------------------------------------------------------

### Step 3: Define Joins

Explicitly define joins between tables:

-   Match on Company

-   Match on key fields (e.g., `JobNum`, `PartNum`)

Use **left joins** when related data may not exist.

------------------------------------------------------------------------

### Step 4: Select Display Fields

Choose fields to expose:

-   Identifiers (JobNum, PartNum)

-   Descriptions

-   Quantities

-   Locations

Rename columns to be integration‑friendly:

Part\_PartNum → PartNum

WhseBin\_BinNum → Bin

------------------------------------------------------------------------

### Step 5: Add Filters

Filters restrict rows, for example:

-   Only open jobs

-   Only material lines with quantity remaining

Avoid hard‑coding values when parameters make more sense.

------------------------------------------------------------------------

### Step 6: Add Parameters (Very Important)

Parameters make the BAQ reusable.

Example parameter:

Parameter Name: pJobNum

Type: String

Then reference it in filters:

JobMtl.JobNum = @pJobNum

This allows external programs to pass values dynamically.

------------------------------------------------------------------------

### Step 7: Test the BAQ

Use the **Analyze** or **Test** function:

-   Enter parameter values

-   Verify row counts

-   Check performance

If it’s slow here, it will be slow in production.

------------------------------------------------------------------------

### Step 8: Secure the BAQ

Assign:

-   User security

-   Group security

Remember: integrations run as *users*. If the user cannot run the BAQ,
neither can your program.

------------------------------------------------------------------------

## Using BAQs from External Code

Once saved, BAQs can be accessed via:

-   Epicor REST (`/BAQSvc`)

-   OData endpoints

External code typically:

1.  Authenticates to Epicor

2.  Calls the BAQ by ID

3.  Passes parameters

4.  Receives JSON or XML

This is how Epicor integrations should be built.

------------------------------------------------------------------------

## Common Mistakes

-   Too many tables (over‑joining)

-   Missing Company joins

-   Hard‑coded filters instead of parameters

-   Returning far more columns than needed

-   Not testing with realistic data volume

------------------------------------------------------------------------

## Best Practices

-   Treat BAQs as **APIs**, not ad‑hoc queries

-   Keep them narrowly focused

-   Use parameters liberally

-   Version them carefully

-   Document their intent

------------------------------------------------------------------------

## Summary

BAQs are the **foundation of safe, upgrade‑proof Epicor integrations**.
They define a clean contract between Epicor’s internal data model and
the outside world. If you design good BAQs, everything built on top of
them becomes simpler, faster, and more reliable.

If you remember one thing:

> *In Epicor, integrations start with BAQs.*

  

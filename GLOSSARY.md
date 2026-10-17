# DocFlow

Turns vendor invoices and bank statements into structured data that an auditor can vouch for, with every value traceable to its source.

## Language

### Documents

**Source Document**:
The original invoice or bank statement file (PDF or scan) as received from the client.
_Avoid_: File, upload, input

**Tax Invoice**:
A B2B GST invoice issued by a Supplier to a Recipient, each identified by a GSTIN.
_Avoid_: Bill, receipt

**Bank Statement**:
A bank's record of an account's transactions over a period, with opening and closing balances.

**Statement Line**:
One transaction row on a Bank Statement.
_Avoid_: Entry, row, txn

### Extraction

**Field**:
A named value extracted from a Source Document (e.g. invoice number, taxable value).

**Evidence**:
The location in the Source Document (page and region) from which a Field's value was read.
_Avoid_: Citation, source, bbox

### Assurance

**Check**:
A deterministic rule applied to extracted Fields that either passes or raises a Flag.
_Avoid_: Validation, rule, test

**Flag**:
A failed Check or low-confidence Field that blocks a document from bulk approval.
_Avoid_: Error, warning, alert

**Review**:
The step where an auditor confirms or corrects a document's Fields.

**Approval**:
An auditor's sign-off on a reviewed document; only a human gives it.
_Avoid_: Verification, certification

# Contracts

`contracts/` is the interface-contract layer for this repository.

Before implementation relies on a new endpoint, database object, API field,
enum, or generated model, update the relevant local contract first:

- `openapi.yaml`
- `database.sql`
- `enums.md`

Implementation follows contracts. Contracts do not follow implementation.

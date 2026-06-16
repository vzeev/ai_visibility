# OpenSpec

`openspec/` is the behavior-spec layer for this repository.

## Folder Roles

- `changes/`
  - proposed or in-progress changes
  - each change can contain `proposal.md`, `design.md`, `tasks.md`, and
    change-local specs

- `specs/`
  - accepted, durable baseline behavior specs
  - this should describe what the system currently supports, not what is only
    planned

## Practical Rule

- If behavior is proposed or still changing, keep it in `changes/`.
- If behavior is accepted and implemented, promote it into `specs/`.

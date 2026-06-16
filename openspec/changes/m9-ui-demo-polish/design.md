# M9 Design

## Product Direction

Keep the current operational dashboard structure. Improve demo clarity by surfacing live status and evidence instead of adding marketing or instructional text.

## Frontend Changes

- Add a compact overview band below the top bar with:
  - active Brandlight config status
  - queue activity and latest run state
  - raw response count
  - insight summary count and latest mention counts
- Add Config tab emphasis for the active Brandlight setup and enabled models.
- Add Visibility detail fields for raw response ID, run item ID, idempotency key, model, provider response, usage, raw request, and raw response.
- Add Insights tab action:
  - discover latest succeeded run from visibility-service
  - call `POST /api/v1/extractions/run-batches/{run_batch_id}`
  - reload summaries after completion
  - report inline success/error state

## Styling

Use existing restrained Brandlight-inspired palette and 6-8px radii. Avoid nested cards and marketing hero treatment. Ensure compact panels remain readable on mobile.

## Verification

Run static checks and browser validation against local services seeded by M8 `demo-e2e`.

# Developer Output

## Scope Implemented

- Added `PATCH /api/v1/models/{model_registry_id}/visibility`.
- Added config repository support for toggling `enabled_for_visibility`.
- Blocked enabling unavailable model rows.
- Added frontend API client method for model visibility updates.
- Added Config tab enable/disable controls for every model row.
- Updated Cypress fixture to exercise the model visibility toggle.

## Key Decisions

- Used a narrow visibility-toggle route instead of a broad model-edit endpoint.
- Kept model deletion and bulk enablement out of scope.
- Used the same control path for fake and OpenAI models so the operator can disable fake rows without special-case cleanup.

## Verification

- `poetry run python -m pytest tests/services/test_config_service_api.py`: passed.
- `npm run build`: passed.
- `poetry run web-check`: passed.
- `poetry run web-e2e`: passed with Cypress cache escalation.

## Risks

- Running Docker services must be rebuilt/restarted before the new endpoint is available.
- Existing fake raw responses remain visible until filtered/search-cleared or superseded by a new real-model run.

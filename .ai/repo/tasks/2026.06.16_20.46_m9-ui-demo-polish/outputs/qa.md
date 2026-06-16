# QA Output - M9 UI Demo Polish

## Executed Checks

- `poetry run web-check`: passed
- `poetry run check-skeleton`: passed
- `poetry run precommit`: passed
- `npm run build`: passed
- `poetry run test-service`: passed, 17 tests
- `poetry run demo-e2e`: passed, 2 raw responses, 2 extraction runs, 6 mentions, 2 citations
- HTTP smoke:
  - `GET http://127.0.0.1:5173`: 200
  - `GET http://127.0.0.1:8001/api/v1/brands`: 200
  - `GET http://127.0.0.1:8002/api/v1/runs`: 200
  - `GET http://127.0.0.1:8002/api/v1/raw-responses?limit=1`: 200
  - `GET http://127.0.0.1:8003/api/v1/summaries`: 200
  - `POST http://127.0.0.1:8003/api/v1/extractions/run-batches/{id}`: 200

## Blocker

Browser validation could not run. The in-app browser runtime failed before tab creation with `failed to write kernel assets: The system cannot find the path specified. (os error 3)`.


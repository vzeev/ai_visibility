# M10 Design

## Product Direction

Keep Config as an operational setup surface. Add compact authoring panels beside the existing lists so demo users can configure the system without turning the page into an admin console.

## Frontend Changes

- Extend `configApi` with POST methods for existing backend contracts.
- Add a single authoring panel to Config with sections for:
  - provider credential creation
  - prompt creation
  - prompt version creation
  - rate-limit policy creation
- Reset secret input fields after successful credential creation.
- Reload config data after each successful write.
- Show inline success/error state per authoring section.

## Security Constraints

- Token input is write-only.
- Token value is not displayed in success messages.
- Credential list continues to show only redacted backend metadata.

## Verification

Run static web checks, production build, precommit hooks, and service tests. Browser validation is desirable but may remain blocked by the local Browser plugin runtime.

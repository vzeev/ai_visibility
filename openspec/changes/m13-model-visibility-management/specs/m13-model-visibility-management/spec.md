# M13 Model Visibility Management Spec

## Requirements

### Requirement: Explicit Model Visibility Enablement

The config service SHALL let an operator update whether an existing model registry row is enabled for visibility runs.

#### Scenario: Enable available model

- GIVEN a model registry row exists and is available
- WHEN a client updates model visibility to enabled
- THEN config-service persists `enabled_for_visibility = true`
- AND subsequent reads return the enabled state.

#### Scenario: Disable model

- GIVEN a model registry row exists
- WHEN a client updates model visibility to disabled
- THEN config-service persists `enabled_for_visibility = false`
- AND subsequent visibility runs no longer snapshot that model.

#### Scenario: Block enabling unavailable model

- GIVEN a model registry row exists but `is_available = false`
- WHEN a client attempts to enable it
- THEN config-service rejects the request.

### Requirement: UI Model Selection Controls

The Config tab SHALL let an operator enable or disable individual model rows from the provider/model setup area.

#### Scenario: Toggle model from Config tab

- GIVEN models are visible in the Config tab
- WHEN the operator clicks the visibility control for a model
- THEN the UI calls the config-service visibility update API
- AND refreshes model state and enabled-model counts.

# M12 Demo E2E Validation Spec

## ADDED Requirements

### Requirement: Browser E2E Demo Validation

The web workspace SHALL include Cypress-based E2E tests for the interview demo
journey.

#### Scenario: Deterministic UI journey

- **WHEN** Cypress runs the main demo spec with mocked service APIs
- **THEN** it validates the Overview, Config, Queue, Visibility, and Insights
  user-facing workflow
- **AND** it must not require real OpenAI calls
- **AND** it must use stable selectors rather than incidental layout structure

### Requirement: Demo Walkthrough Documentation

The repository SHALL include demo walkthrough docs under `docs/demo/`.

#### Scenario: Interview operator prepares demo

- **WHEN** the operator opens the demo docs
- **THEN** they can follow architecture, technical implementation, and main flow
  talking points
- **AND** the docs distinguish current deterministic extraction from future or
  optional AI-assisted extraction.

### Requirement: Root Demo Validation Commands

The repository SHALL expose root commands for demo validation.

#### Scenario: Operator validates demo readiness

- **WHEN** the operator runs the root demo validation command
- **THEN** it checks repo-local prerequisites and prints the intended
  walkthrough commands without exposing secrets.

### Requirement: Demo Evidence UI

The UI SHALL expose the core demo evidence points without source-code browsing.

#### Scenario: Operator explains raw-to-insight lineage

- **WHEN** the operator views Queue, Visibility, and Insights
- **THEN** run expansion, raw evidence identifiers, idempotency keys, summary
  metrics, and extraction evidence are visible enough to narrate the system.

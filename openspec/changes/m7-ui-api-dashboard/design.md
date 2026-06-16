# M7 Design

## Runtime Shape

```text
React/Vite UI
  -> frontend API client
  -> config-service http://localhost:8001
  -> visibility-service http://localhost:8002
  -> insights-service http://localhost:8003
```

## Key Decisions

- Use plain React hooks and `fetch`; no extra runtime dependency.
- Configure service base URLs with Vite env variables and sensible localhost
  defaults.
- Keep each tab self-contained but share loading/error/empty primitives and API
  DTO types.
- Use compact enterprise dashboard layouts: tables, metrics, detail panels,
  refresh controls, and constrained cards.
- Use Brandlight-inspired palette and density, not copied assets.

## Verification

- TypeScript build/typecheck.
- Vite production build.
- Pre-commit and aggregate checks.
- Browser screenshot validation against the local dev server.

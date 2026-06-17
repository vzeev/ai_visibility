# M7 UI API Dashboard

## Summary

Connect the React/Vite dashboard to the local config, visibility, and insights
service APIs so the four planned tabs become operational instead of static
mockups.

## Goals

- Add a typed frontend API client for config-service, visibility-service, and
  insights-service.
- Replace static tab data with API-backed views for Config, Queue, Visibility,
  and Insights.
- Provide loading, empty, error, refresh, search, pagination, and detail states.
- Keep visual styling aligned with Brandlight's public enterprise dashboard
  feel without copying proprietary assets.
- Preserve backend behavior except minimal API ergonomics if needed.

## Non-Goals

- No authentication or production deployment hardening.
- No new backend extraction/worker behavior beyond already implemented M6.
- No proprietary Brandlight asset copying.
- No large frontend framework or state-management dependency.

## References

- `apps/web/src/app/App.tsx`
- `apps/config_service/app/api/routes.py`
- `apps/visibility_service/app/api/routes.py`
- `apps/insights_service/app/api/routes.py`
- `https://www.brandlight.ai/`

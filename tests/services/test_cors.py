from __future__ import annotations

import unittest
from collections.abc import Callable
from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from apps.config_service.app.main import create_app as create_config_app
from apps.insights_service.app.main import create_app as create_insights_app
from apps.visibility_service.app.main import create_app as create_visibility_app


class CorsTests(unittest.TestCase):
    def test_local_vite_origin_is_allowed_for_backend_services(self) -> None:
        app_factories: dict[str, Callable[[], FastAPI]] = {
            "config": create_config_app,
            "visibility": create_visibility_app,
            "insights": create_insights_app,
        }
        for service_name, app_factory in app_factories.items():
            with self.subTest(service=service_name):
                client: Any = TestClient(app_factory())
                try:
                    response = cast(
                        Response,
                        client.options(
                            "/healthz",
                            headers={
                                "Origin": "http://localhost:5173",
                                "Access-Control-Request-Method": "GET",
                            },
                        ),
                    )
                finally:
                    client.close()

                self.assertEqual(200, response.status_code)
                self.assertEqual(
                    "http://localhost:5173",
                    response.headers.get("access-control-allow-origin"),
                )

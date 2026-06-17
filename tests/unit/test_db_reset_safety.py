from __future__ import annotations

import os
import unittest

from tests.integration.db_helpers import ALLOW_DB_RESET_ENV, assert_safe_reset_database_url


class DbResetSafetyTests(unittest.TestCase):
    def test_refuses_reset_without_explicit_guard(self) -> None:
        original_guard = os.environ.get(ALLOW_DB_RESET_ENV)
        try:
            os.environ.pop(ALLOW_DB_RESET_ENV, None)

            with self.assertRaisesRegex(RuntimeError, ALLOW_DB_RESET_ENV):
                assert_safe_reset_database_url(
                    "postgresql+psycopg://ai_visibility:ai_visibility_local@localhost:55432/ai_visibility_test"
                )
        finally:
            _restore_env(ALLOW_DB_RESET_ENV, original_guard)

    def test_refuses_non_local_database_url_even_with_guard(self) -> None:
        original_guard = os.environ.get(ALLOW_DB_RESET_ENV)
        try:
            os.environ[ALLOW_DB_RESET_ENV] = "true"

            with self.assertRaisesRegex(RuntimeError, "local PostgreSQL hosts"):
                assert_safe_reset_database_url(
                    "postgresql+psycopg://ai_visibility:ai_visibility_local@db.example.com:5432/ai_visibility_test"
                )
        finally:
            _restore_env(ALLOW_DB_RESET_ENV, original_guard)

    def test_refuses_non_test_database_url_even_with_guard(self) -> None:
        original_guard = os.environ.get(ALLOW_DB_RESET_ENV)
        try:
            os.environ[ALLOW_DB_RESET_ENV] = "true"

            with self.assertRaisesRegex(RuntimeError, "test databases"):
                assert_safe_reset_database_url(
                    "postgresql+psycopg://ai_visibility:ai_visibility_local@localhost:5432/ai_visibility"
                )
        finally:
            _restore_env(ALLOW_DB_RESET_ENV, original_guard)

    def test_accepts_explicitly_guarded_local_test_database_url(self) -> None:
        original_guard = os.environ.get(ALLOW_DB_RESET_ENV)
        try:
            os.environ[ALLOW_DB_RESET_ENV] = "true"

            assert_safe_reset_database_url(
                "postgresql+psycopg://ai_visibility:ai_visibility_local@localhost:55432/ai_visibility_test"
            )
        finally:
            _restore_env(ALLOW_DB_RESET_ENV, original_guard)


def _restore_env(key: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value

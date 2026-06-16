import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ContractFileTests(unittest.TestCase):
    def test_openapi_marks_provider_token_write_only(self) -> None:
        text = (ROOT / "contracts/openapi.yaml").read_text(encoding="utf-8")

        self.assertIn("/api/v1/provider-credentials:", text)
        self.assertIn("writeOnly: true", text)

    def test_database_contract_has_raw_response_idempotency(self) -> None:
        text = (ROOT / "contracts/database.sql").read_text(encoding="utf-8")

        self.assertIn("CREATE TABLE visibility.raw_responses", text)
        self.assertIn("idempotency_key text NOT NULL UNIQUE", text)
        self.assertIn("CREATE TABLE config.rate_limit_policies", text)

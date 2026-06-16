import unittest

from apps.shared.ai.secrets import redacted_fingerprint


class SecretTests(unittest.TestCase):
    def test_redacted_fingerprint_does_not_expose_secret(self) -> None:
        fingerprint = redacted_fingerprint("sk-live-secret")

        self.assertTrue(fingerprint.startswith("sha256:"))
        self.assertNotIn("sk-live-secret", fingerprint)

    def test_redacted_fingerprint_rejects_empty_secret(self) -> None:
        with self.assertRaisesRegex(ValueError, "secret"):
            redacted_fingerprint("")

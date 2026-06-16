from __future__ import annotations

import unittest

from apps.insights_service.app.domain.extractor import (
    DeterministicInsightExtractor,
    EntityAliases,
)


class DeterministicInsightExtractorTests(unittest.TestCase):
    def test_extracts_mentions_with_sentiment_and_word_boundaries(self) -> None:
        extractor = DeterministicInsightExtractor()

        result = extractor.extract(
            output_text=(
                "Brandlight is a strong AI visibility platform. "
                "AcmeRank is not recommended. Brandlighting is a different word."
            ),
            entities=(
                EntityAliases("brand", "Brandlight", ("Brandlight",)),
                EntityAliases("competitor", "AcmeRank", ("AcmeRank",)),
            ),
        )

        self.assertEqual(2, len(result.mentions))
        self.assertEqual("Brandlight", result.mentions[0].mention_text)
        self.assertEqual("positive", result.mentions[0].sentiment_label)
        self.assertEqual("AcmeRank", result.mentions[1].mention_text)
        self.assertEqual("negative", result.mentions[1].sentiment_label)

    def test_extracts_normalized_unique_citations(self) -> None:
        extractor = DeterministicInsightExtractor()

        result = extractor.extract(
            output_text=(
                "Read https://www.brandlight.ai/docs, then https://www.brandlight.ai/docs."
            ),
            entities=(),
        )

        self.assertEqual(1, len(result.citations))
        self.assertEqual("https://www.brandlight.ai/docs", result.citations[0].url)
        self.assertEqual("brandlight.ai", result.citations[0].domain)
        self.assertGreaterEqual(result.citations[0].end_index, result.citations[0].start_index)


if __name__ == "__main__":
    unittest.main()

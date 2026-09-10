"""Dependency-free local similarity baseline for Demo retrieval."""

import math
import re
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VectorDocument:
    vector_id: str
    form_id: str
    content_type: str
    content: str


@dataclass(frozen=True, slots=True)
class VectorMatch:
    document: VectorDocument
    score: float


class LocalVectorIndex:
    def __init__(self) -> None:
        self._documents: dict[str, VectorDocument] = {}

    def add(self, document: VectorDocument) -> None:
        self._documents[document.vector_id] = document

    def search(self, query: str, *, limit: int = 10) -> list[VectorMatch]:
        if limit <= 0:
            return []
        query_terms = self._terms(query)
        matches = [
            VectorMatch(
                document=document, score=self._cosine(query_terms, self._terms(document.content))
            )
            for document in self._documents.values()
        ]
        return sorted(
            (match for match in matches if match.score > 0),
            key=lambda match: (-match.score, match.document.vector_id),
        )[:limit]

    @staticmethod
    def _terms(text: str) -> Counter[str]:
        normalized = re.sub(r"\s+", "", text.lower())
        characters = [character for character in normalized if not character.isspace()]
        bigrams = ["".join(characters[index : index + 2]) for index in range(len(characters) - 1)]
        words = re.findall(r"[a-z0-9_]+", text.lower())
        return Counter([*characters, *bigrams, *words])

    @staticmethod
    def _cosine(left: Counter[str], right: Counter[str]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(value * right.get(term, 0) for term, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0

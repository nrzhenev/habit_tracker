from app.entry.entry_classification.client import LLMClassifier


def get_classifier() -> LLMClassifier:
    return LLMClassifier()

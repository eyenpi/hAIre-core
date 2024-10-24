import random
import re
from transformers import pipeline
import uuid


# Class for entity recognition using transformers
class EntityRecognizer:
    def __init__(self, model_name="dslim/bert-base-NER-uncased"):
        self.ner_pipeline = pipeline(
            "ner", model=model_name, aggregation_strategy="simple"
        )

    def identify_entities(self, text):
        entities = self.ner_pipeline(text)
        entity_dict = {}
        for entity in entities:
            entity_text = text[
                entity["start"] : entity["end"]
            ]  # Extract full entity based on start and end positions
            entity_type = entity[
                "entity_group"
            ]  # Extract the entity type (e.g., PER, ORG, LOC)
            if entity_type in ["PER", "ORG", "LOC"]:  # Only store sensitive types
                entity_dict[entity_text] = entity_type  # Store both entity and its type
        return entity_dict


class AnonymizationProcessor:
    def __init__(self, entity_recognizer: EntityRecognizer):
        self.entity_recognizer = entity_recognizer
        self.entity_map = {}  # Store mappings for reversal

    def anonymize_text(self, text: str) -> str:
        entities = self.entity_recognizer.identify_entities(text)

        # Sort entities by length in descending order
        sorted_entities = sorted(
            entities.items(), key=lambda x: len(x[0]), reverse=True
        )

        anonymized_text = text
        for entity, entity_type in sorted_entities:
            pseudonym = self.generate_pseudonym(entity_type)
            self.entity_map[pseudonym] = entity  # Store mapping for reversal

            # Use regex to replace only whole words and avoid partial matches
            anonymized_text = re.sub(
                rf"\b{re.escape(entity)}\b", pseudonym, anonymized_text
            )
        return anonymized_text

    def reverse_anonymization(self, anonymized_text: str) -> str:
        original_text = anonymized_text
        for pseudonym, entity in self.entity_map.items():
            # Use regex to ensure full word match for replacement
            original_text = re.sub(
                rf"\b{re.escape(pseudonym)}\b", entity, original_text
            )
        return original_text

    def generate_pseudonym(self, entity_type: str) -> str:
        """Generate more readable and relevant pseudonyms based on entity type"""
        pseudonym_map = {
            "PER": lambda: f"Person_{uuid.uuid4().hex[:8]}",  # You can replace this with funny names
            "ORG": lambda: f"Company_{uuid.uuid4().hex[:8]}",  # Add predefined company names if needed
            "LOC": lambda: f"Location_{uuid.uuid4().hex[:8]}",  # Add predefined locations if needed
        }
        return pseudonym_map.get(entity_type, lambda: "Unknown")()

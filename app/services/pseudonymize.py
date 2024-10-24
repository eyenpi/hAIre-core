from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Dict, Any
import random
import re
from transformers import pipeline


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
            entity_text = entity["word"]
            entity_type = entity[
                "entity_group"
            ]  # Extract the entity type (e.g., PER, ORG, LOC)
            if entity_type in ["PER", "ORG", "LOC"]:  # Only store sensitive types
                entity_dict[entity_text] = entity_type  # Store both entity and its type
        return entity_dict


# Class for pseudonymization using funny names
class Pseudonymizer:
    def __init__(self):
        self.person_names = [
            "Lord Voldemort",
            "Hermione Granger",
            "Yoda",
            "Frodo Baggins",
            "Chewbacca",
            "Darth Vader",
            "Gandalf the Grey",
            "Indiana Jones",
            "Willy Wonka",
            "Sherlock Holmes",
            "Tony Stark",
            "Bruce Wayne",
            "James Bond",
            "Jack Sparrow",
            "Optimus Prime",
            "Rick Sanchez",
            "Homer Simpson",
            "SpongeBob SquarePants",
            "Scooby-Doo",
            "Bart Simpson",
            "Shrek",
            "Walter White",
            "Bilbo Baggins",
            "Jon Snow",
            "Lara Croft",
            "Mario",
            "Luigi",
            "Link",
            "Princess Leia",
            "Han Solo",
            "Boba Fett",
            "Doctor Who",
            "Marty McFly",
            "Tyler Durden",
            "Katniss Everdeen",
            "Neo",
            "Trinity",
            "John Wick",
            "Buzz Lightyear",
            "Woody",
            "Elsa",
            "Dory",
            "Mulan",
            "Ariel",
            "Thor",
            "Deadpool",
            "Black Panther",
            "Spock",
            "Wolverine",
            "Magneto",
            "Charlie Brown",
            "Pikachu",
        ]

        self.company_names = [
            "Stark Industries",
            "Wayne Enterprises",
            "Wonka Industries",
            "Umbrella Corp",
            "Cyberdyne Systems",
            "Initech",
            "ACME Corporation",
            "Pied Piper",
            "Monsters, Inc.",
            "Oscorp",
            "Dunder Mifflin",
            "Gringotts Bank",
            "Xanatos Enterprises",
            "Weyland-Yutani",
            "Gekko & Co.",
            "Bubba Gump Shrimp",
            "Duff Beer",
            "Krusty Krab",
            "Planet Express",
            "Aperture Science",
            "Black Mesa",
            "Buy n Large",
            "Vandelay Industries",
            "Tyrell Corporation",
            "LexCorp",
            "Soylent Corporation",
            "Virtucon",
            "OCP (Omni Consumer Products)",
            "Yoyodyne Propulsion Systems",
            "Globex Corporation",
            "Genco Pura Olive Oil Company",
            "Prestige Worldwide",
            "Cyberdyne",
            "Dinoco",
            "SpaceX",
            "Delos Destinations",
            "Roxxon Corporation",
        ]

        self.location_names = [
            "Hogwarts",
            "Narnia",
            "Westeros",
            "Middle-Earth",
            "Asgard",
            "The Shire",
            "Gotham City",
            "Metropolis",
            "Springfield",
            "Bikini Bottom",
            "Pandora",
            "Azkaban",
            "Mordor",
            "Rivendell",
            "Tatooine",
            "Vulcan",
            "Hyrule",
            "Skyrim",
            "Atlantis",
            "Jurassic Park",
            "Neverland",
            "Emerald City",
            "Cloud City",
            "Endor",
            "Gallifrey",
            "King's Landing",
            "Vice City",
            "Liberty City",
            "Silent Hill",
            "Raccoon City",
            "Zion",
            "The Death Star",
            "Agrabah",
            "Duckburg",
            "Elbonia",
            "Genosha",
            "Kamino",
            "New New York",
            "Sokovia",
            "Wakanda",
            "Themyscira",
        ]
        self.token_map = {}  # Maps original values to pseudonyms
        self.reverse_map = {}  # Maps pseudonyms back to original values

    def pseudonymize(self, data, entity_type):
        """Pseudonymize the given data using the correct entity type list, ensuring uniqueness."""
        if data not in self.token_map:
            if entity_type == "PER":
                base_token = random.choice(self.person_names)
            elif entity_type == "ORG":
                base_token = random.choice(self.company_names)
            elif entity_type == "LOC":
                base_token = random.choice(self.location_names)
            else:
                base_token = data  # fallback in case the entity type is not known

            # Ensure uniqueness by adding an index if the base token already exists
            unique_token = base_token
            count = 1
            while unique_token in self.token_map.values():
                unique_token = f"{base_token}_{count}"
                count += 1

            self.token_map[data] = unique_token
            self.reverse_map[unique_token] = data
        return self.token_map[data]

    def depseudonymize(self, token):
        """Retrieve original data from the pseudonym."""
        return self.reverse_map.get(token, token)


# Main class that uses both EntityRecognizer and Pseudonymizer
class DataProcessor:
    def __init__(self):
        self.entity_recognizer = EntityRecognizer()
        self.pseudonymizer = Pseudonymizer()

    def process_text(self, text):
        text = text.lower()
        # Step 1: Identify entities
        entity_dict = self.entity_recognizer.identify_entities(text)

        # Step 2: Pseudonymize the identified entities
        pseudonymized_entity_dict = self.pseudonymize_entities(entity_dict)

        # Step 3: Replace entities with pseudonymized tokens in the text
        pseudonymized_text = self.replace_entities_with_tokens(
            text, pseudonymized_entity_dict
        )

        return pseudonymized_text, pseudonymized_entity_dict

    def pseudonymize_entities(self, entity_dict):
        pseudonymized_entity_dict = {}
        for entity, entity_type in entity_dict.items():
            pseudonymized_entity_dict[entity] = self.pseudonymizer.pseudonymize(
                entity, entity_type
            )
        return pseudonymized_entity_dict

    def replace_entities_with_tokens(self, text, entity_dict):
        pseudonymized_text = text
        for entity, pseudonym in entity_dict.items():
            pseudonymized_text = re.sub(rf"\b{entity}\b", pseudonym, pseudonymized_text)
        return pseudonymized_text

    def depseudonymize_text(self, text, pseudonymized_entity_dict):
        depseudonymized_text = text
        for entity, pseudonym in pseudonymized_entity_dict.items():
            original_value = self.pseudonymizer.depseudonymize(pseudonym)
            depseudonymized_text = depseudonymized_text.replace(
                pseudonym, original_value
            )
        return depseudonymized_text

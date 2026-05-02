import os
import json
import re
import logging
from groq import Groq
from config import GROQ_API_KEY

logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

EXTRACTION_PROMPT = """
You are a knowledge graph extractor. Given a text, extract:
1. ENTITIES: people, organizations, products, concepts, places, events
2. RELATIONSHIPS: directed connections between entities

Return ONLY valid JSON in this exact format:
{
  "entities": [
    {"id": "e1", "name": "Entity Name", "type": "Person|Organization|Product|Concept|Place|Event"}
  ],
  "relationships": [
    {"source": "e1", "target": "e2", "relation": "RELATION_TYPE"}
  ]
}

Rules:
- Entity IDs must be short strings like e1, e2, e3
- Relation types must be UPPER_SNAKE_CASE (e.g., WORKS_AT, CREATED, ACQUIRED)
- Extract ALL meaningful entities and relationships
- Do not include any text outside the JSON
"""


def extract_graph_from_text(text: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": f"Extract graph from this text:\n\n{text}"}
        ],
        temperature=0
    )
    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if the model adds them
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {"entities": [], "relationships": []}


def extract_from_folder(folder_path: str) -> dict:
    all_entities = {}
    all_relationships = []

    if not os.path.exists(folder_path):
        return {"entities": [], "relationships": []}

    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    for filename in txt_files:
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        result = extract_graph_from_text(text)

        # Deduplicate entities by name
        for entity in result["entities"]:
            key = entity["name"].lower()
            if key not in all_entities:
                all_entities[key] = entity

        all_relationships.extend(result["relationships"])

    return {"entities": list(all_entities.values()), "relationships": all_relationships}

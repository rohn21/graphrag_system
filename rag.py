import logging
import json
import re
from groq import Groq
from graph_db import get_driver, get_subgraph, get_full_graph
from config import GROQ_API_KEY

logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)


def extract_entities_from_question(question: str, known_entities: list) -> list:
    # Pass a sample of known entities to help the LLM match them exactly
    entity_list = ", ".join(known_entities[:100])

    prompt = f"""Given this question: "{question}"
And this list of known graph entities: {entity_list}

Return ONLY a JSON array of entity names from the list that are relevant to answering the question.
Example: ["OpenAI", "Sam Altman"]
Return [] if none match."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"```$", "", raw)

    try:
        return json.loads(raw)
    except Exception:
        return []


def query_graph(question: str) -> str:
    driver = get_driver()
    full = get_full_graph(driver)
    known_entities = [n["name"] for n in full["nodes"]]

    if not known_entities:
        driver.close()
        return "The knowledge graph is empty. Please ingest documents first."

    matched_entities = extract_entities_from_question(question, known_entities)

    logger.debug(f"Question: {question}")
    logger.debug(f"Matched Entities: {matched_entities}")

    if matched_entities:
        subgraph = get_subgraph(driver, matched_entities)
        context_rels = subgraph.get("relationships", [])
    else:
        # Fallback to general graph links if no specific entity matched
        context_rels = full.get("links", [])[:30]

    # Format context as "Source --RELATION--> Target"
    if context_rels:
        context = "\n".join([f"- {r['source']} --{r['relation']}--> {r['target']}" for r in context_rels])
    else:
        context = "No direct relationships found."

    logger.debug(f"Context passed to LLM:\n{context}")

    answer_prompt = f"""You are a helpful assistant answering questions based on a knowledge graph.

Graph context (connections related to the question):
{context}

Question: {question}

Answer using ONLY the information in the graph context above. Be specific and concise."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": answer_prompt}],
        temperature=0
    )

    driver.close()
    return response.choices[0].message.content.strip()
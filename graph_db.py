from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

URI = NEO4J_URI
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)


def get_driver():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()
    return driver


def clear_graph(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


def create_entity_node(driver, entity: dict):
    with driver.session() as session:
        session.run(
            """
            MERGE (n:Entity {name: $name})
            SET n.type = $type, n.entity_id = $entity_id
            """,
            name=entity["name"],
            type=entity.get("type", "Unknown"),
            entity_id=entity.get("id", "")
        )


def create_relationship(driver, relationship: dict, entity_map: dict):
    source_name = entity_map.get(relationship.get("source"))
    target_name = entity_map.get(relationship.get("target"))
    relation_type = relationship.get("relation", "RELATED_TO")

    if not source_name or not target_name:
        return

    # Sanitize dynamic relationship type to prevent Cypher injection
    safe_relation = "".join(c for c in relation_type if c.isalnum() or c == "_")
    if not safe_relation:
        safe_relation = "RELATED_TO"

    with driver.session() as session:
        session.run(
            f"""
            MATCH (a:Entity {{name: $source_name}})
            MATCH (b:Entity {{name: $target_name}})
            MERGE (a)-[:{safe_relation}]->(b)
            """,
            source_name=source_name,
            target_name=target_name
        )


def load_graph(extracted_data: dict):
    driver = get_driver()
    entities = extracted_data["entities"]
    relationships = extracted_data["relationships"]
    entity_map = {e["id"]: e["name"] for e in entities if "id" in e}

    for entity in entities:
        create_entity_node(driver, entity)

    for rel in relationships:
        create_relationship(driver, rel, entity_map)

    driver.close()


def get_full_graph(driver) -> dict:
    with driver.session() as session:
        nodes = [
            {"id": rec["name"], "name": rec["name"], "type": rec["type"] or "Unknown"}
            for rec in session.run("MATCH (n:Entity) RETURN n.name AS name, n.type AS type")
        ]
        links = [
            {"source": rec["source"], "target": rec["target"], "relation": rec["relation"]}
            for rec in session.run(
                "MATCH (a:Entity)-[r]->(b:Entity) RETURN a.name AS source, b.name AS target, type(r) AS relation")
        ]
    return {"nodes": nodes, "links": links}


def get_subgraph(driver, entity_names: list) -> dict:
    with driver.session() as session:
        result = session.run(
            """
            MATCH (start:Entity)
            WHERE start.name IN $names
            MATCH path = (start)-[*1..2]-(connected)
            UNWIND relationships(path) AS r
            RETURN DISTINCT startNode(r).name AS source, type(r) AS relation, endNode(r).name AS target
            """,
            names=entity_names
        )
        relationships = []
        for record in result:
            relationships.append({
                "source": record["source"],
                "relation": record["relation"],
                "target": record["target"]
            })
    return {"relationships": relationships}

# GraphRAG

## Project overview

This project builds a GraphRAG system that extracts entities and relationships from text files, stores them in Neo4j AuraDB, answers questions using graph context, and exposes the result through a FastAPI backend and a React + Vite frontend.

## Functionality

- Reads plain text documents from a local `documents/` folder.
- Uses Groq to extract entities and relationships from each document.
- Stores the extracted knowledge as a graph in Neo4j AuraDB.
- Answers user questions by querying the graph for relevant subgraphs.
- Returns graph data through FastAPI endpoints.
- Visualizes the graph and provides a chat interface in the frontend.

## Technology stack

- Python
- FastAPI
- Groq API
- Neo4j AuraDB
- React
- Vite
- `uv`
- python-dotenv

## File details

| File / Folder | Purpose |
|---|---|
| `documents/` | Input text files used to build the knowledge graph. |
| `extract.py` | Extracts entities and relationships from text. |
| `graph_db.py` | Connects to Neo4j and writes graph data. |
| `rag.py` | Handles GraphRAG query logic. |
| `main.py` | FastAPI backend entry point. |
| `frontend/` | React + Vite user interface. |
| `frontend/src/GraphView.jsx` | Graph visualization component. |
| `frontend/src/ChatPanel.jsx` | Chat interface component. |
| `frontend/src/App.jsx` | Main frontend app component. |

## Setup steps

### 1. Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create the project

```bash
uv init graphrag-project
cd graphrag-project
```

### 3. Install backend dependencies

```bash
uv add fastapi uvicorn neo4j groq python-dotenv
```

### 4. Create the `.env` file

Add your credentials to the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
```

### 5. Add `.env` to `.gitignore`

```bash
echo ".env" >> .gitignore
```

### 6. Create a Neo4j AuraDB free instance

- Go to Neo4j AuraDB.
- Create a free instance.
- Download the credentials immediately after creation.
- Save the URI, username, and password in `.env`.

### 7. Prepare the input documents

Place your source `.txt` files inside the `documents/` folder.

### 8. Run entity extraction

Run the extraction step to convert text into entities and relationships.

### 9. Load the graph into Neo4j

Run the graph loading step to write nodes and relationships into AuraDB.

### 10. Start the backend

Run the FastAPI app to expose the query and graph endpoints.

### 11. Set up the frontend

Install the frontend dependencies inside `frontend/` and start the React + Vite app.

### 12. Test the full system

- Ask questions through the backend query endpoint.
- Open the graph visualization endpoint.
- Verify that the frontend chat and graph views work correctly.
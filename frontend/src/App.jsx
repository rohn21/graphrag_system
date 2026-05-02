import { useState } from "react";
import { API_BASE_URL } from "./config";
import GraphView from "./GraphView";
import ChatPanel from "./ChatPanel";

export default function App() {
  const [ingesting, setIngesting] = useState(false);
  const [status, setStatus] = useState("");

  const ingest = async () => {
    setIngesting(true);
    setStatus("Ingesting documents...");
    try {
      const res = await fetch(`${API_BASE_URL}/api/ingest`, { method: "POST" });
      const data = await res.json();
      setStatus(`Done: ${data.entities} entities, ${data.relationships} relationships`);
    } catch (e) {
      setStatus("Ingestion failed. Check backend.");
    }
    setIngesting(false);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#f1f5f9", fontFamily: "sans-serif" }}>
      <div style={{ padding: "16px 24px", borderBottom: "1px solid #1e293b", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h1 style={{ margin: 0, fontSize: 20 }}>GraphRAG Explorer</h1>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {status && <span style={{ color: "#94a3b8", fontSize: 13 }}>{status}</span>}
          <button onClick={ingest} disabled={ingesting} style={{ padding: "8px 16px", background: "#3b82f6", color: "white", borderRadius: 6, border: "none", cursor: "pointer" }}>
            {ingesting ? "Ingesting..." : "⬆ Ingest Documents"}
          </button>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, padding: 16, height: "calc(100vh - 64px)" }}>
        <GraphView />
        <ChatPanel />
      </div>
    </div>
  );
}
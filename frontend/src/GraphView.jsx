import { useEffect, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { API_BASE_URL } from "./config";

const TYPE_COLORS = {
  Person: "#f97316", Organization: "#3b82f6", Product: "#22c55e",
  Concept: "#a855f7", Place: "#eab308", Event: "#ef4444", Unknown: "#6b7280",
};

export default function GraphView() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  const fetchGraph = async () => {
    const res = await fetch(`${API_BASE_URL}/api/graph`);
    const data = await res.json();
    setGraphData(data);
  };

  useEffect(() => { fetchGraph(); }, []);

  return (
    <div style={{ background: "#0f172a", borderRadius: 8, overflow: "hidden" }}>
      <div style={{ padding: "8px 16px", color: "#94a3b8", fontSize: 12 }}>
        {graphData.nodes.length} nodes · {graphData.links.length} relationships
        <button onClick={fetchGraph} style={{ marginLeft: 12, cursor: "pointer" }}>↻ Refresh</button>
      </div>
      <ForceGraph2D
        graphData={graphData}
        width={700} height={500}
        nodeLabel="name"
        nodeColor={(node) => TYPE_COLORS[node.type] || TYPE_COLORS.Unknown}
        linkLabel="relation"
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        backgroundColor="#0f172a" nodeRelSize={6}
      />
    </div>
  );
}
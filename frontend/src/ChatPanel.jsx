import { useState, useRef, useEffect } from "react";
import { API_BASE_URL } from "./config";

export default function ChatPanel() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Graph loaded! Ask me anything about the documents." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: "assistant", text: "Error reaching backend." }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#1e293b", borderRadius: 8 }}>
      <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 12, textAlign: m.role === "user" ? "right" : "left" }}>
            <span style={{
              display: "inline-block", padding: "8px 12px", borderRadius: 8,
              background: m.role === "user" ? "#3b82f6" : "#334155", color: "#f1f5f9", maxWidth: "85%"
            }}>{m.text}</span>
          </div>
        ))}
        {loading && <div style={{ color: "#64748b" }}>Thinking...</div>}
        <div ref={bottomRef} />
      </div>
      <div style={{ display: "flex", padding: 12, gap: 8, borderTop: "1px solid #334155" }}>
        <input
          value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask a question..."
          style={{ flex: 1, padding: "8px 12px", borderRadius: 6, border: "1px solid #475569", background: "#0f172a", color: "#f1f5f9" }}
        />
        <button onClick={sendMessage} style={{ padding: "8px 16px", background: "#3b82f6", color: "white", borderRadius: 6, border: "none", cursor: "pointer" }}>Send</button>
      </div>
    </div>
  );
}
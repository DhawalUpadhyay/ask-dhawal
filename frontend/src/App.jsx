import { useState, useEffect, useRef } from "react";
import { API_BASE_URL } from "./config/api";

function App() {
  useEffect(() => {
    document.title = "Ask Dhawal – AI Resume";
  }, []);
  const endpoint = `${API_BASE_URL}/api/chat`;
  const [messages, setMessages] = useState([
    {
      role: "bot",
      content:
        "Hi 👋 I’m Dhawal’s AI resume. You can ask me about my experience, skills, or projects.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: input,
        session_id: sessionId,
      }),
    });

    const data = await res.json();
    setSessionId(data.session_id);

    const botMessage = { role: "bot", content: data.reply };
    setMessages((prev) => [...prev, botMessage]);
    setLoading(false);
    inputRef.current?.focus();
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.header}>
          <h1 style={styles.title}>Ask Dhawal</h1>
          <p style={styles.subtitle}>
            An AI-powered interactive resume. Ask anything about my experience,
            skills, or projects.
          </p>
        </div>

        <div style={styles.chat}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                ...styles.message,
                ...(msg.role === "user"
                  ? styles.userMessage
                  : styles.botMessage),
              }}
            >
              {msg.content}
            </div>
          ))}

          {loading && (
            <div style={{ ...styles.message, ...styles.botMessage }}>
              Typing…
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div style={styles.inputRow}>
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask a question…"
            style={styles.input}
          />
          <button
            onClick={sendMessage}
            style={{
              ...styles.button,
              opacity: loading ? 0.6 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #1f1f1f, #2a2a2a)",
    display: "flex",
    alignItems: "center",      // vertical center
    justifyContent: "center",  // horizontal center
    padding: "24px",
    color: "#fff",
    fontFamily: "Inter, system-ui, Arial",
    transform: "translateY(-20px)",
  },

  card: {
    width: "100%",
    maxWidth: "960px",
    height: "80vh",              // 👈 IMPORTANT
    margin: "0 auto",
    background: "#111",
    borderRadius: "16px",
    boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
    display: "flex",
    flexDirection: "column",     // 👈 IMPORTANT
    overflow: "hidden",          // 👈 prevents header scroll
  },

  header: {
    padding: "24px",
    borderBottom: "1px solid #222",
    flexShrink: 0, 
  },

  title: {
    margin: 0,
    fontSize: "28px",
  },

  subtitle: {
    marginTop: "8px",
    fontSize: "14px",
    color: "#aaa",
  },

  chat: {
    flex: 1,                     // 👈 takes remaining space
    padding: "20px",
    overflowY: "auto",           // 👈 ONLY scrollable area
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },

  message: {
    maxWidth: "75%",
    padding: "12px 16px",
    borderRadius: "14px",
    fontSize: "14px",
    lineHeight: 1.4,
  },

  userMessage: {
    alignSelf: "flex-end",
    background: "#4f46e5",
    color: "#fff",
  },

  botMessage: {
    alignSelf: "flex-start",
    background: "#1f2933",
    color: "#e5e7eb",
  },

  inputRow: {
    display: "flex",
    gap: "10px",
    padding: "16px",
    borderTop: "1px solid #222",
    flexShrink: 0, 
  },

  input: {
    flex: 1,
    padding: "12px 14px",
    borderRadius: "10px",
    border: "none",
    outline: "none",
    background: "#1f2933",
    color: "#fff",
    fontSize: "14px",
  },

  button: {
    padding: "12px 18px",
    borderRadius: "10px",
    border: "none",
    cursor: "pointer",
    background: "#4f46e5",
    color: "#fff",
    fontSize: "14px",
  },
};

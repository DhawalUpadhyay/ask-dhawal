import { useState, useEffect, useRef } from "react";
import { API_BASE_URL } from "./config/api";
import "./App.css";
import Login from "./Login";
import OtpVerify from "./OtpVerify";

const SUGGESTIONS = [
  "What's your AWS experience?",
  "Tell me about your GenAI work",
  "Can you join immediately?",
];

function App() {
  useEffect(() => {
    document.title = "Ask Dhawal – AI Resume";
  }, []);

  // --- Auth state machine ---
  const [screen, setScreen] = useState("login"); // "login" | "otp" | "chat"
  const [pendingAuth, setPendingAuth] = useState(null); // { sessionId, name, email }

  const handleLoginSuccess = (auth) => {
    setPendingAuth(auth);
    setScreen("otp");
  };

  const handleOtpSuccess = () => {
    setSessionId(pendingAuth.sessionId);
    setScreen("chat");
  };

  const handleBack = () => {
    setPendingAuth(null);
    setScreen("login");
  };

  // --- Chat state ---
  const [showInfo, setShowInfo] = useState(false);
  const endpoint = `${API_BASE_URL}/api/chat`;

  const [messages, setMessages] = useState([
    {
      role: "bot",
      content:
        "Hi 👋 I'm Dhawal's AI resume. Ask me anything about my experience, skills, or projects.",
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

  const sendMessage = async (messageText = null) => {
    const text = messageText ?? input;
    if (!text.trim() || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    if (!messageText) setInput("");
    setLoading(true);

    // Add placeholder bot message (will be filled by streaming tokens)
    setMessages((prev) => [...prev, { role: "bot", content: "" }]);

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // keep incomplete line in buffer

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;
          try {
            const event = JSON.parse(raw);
            if (event.type === "session" && event.session_id) {
              setSessionId(event.session_id);
            } else if (event.type === "token") {
              setMessages((prev) => {
                const msgs = [...prev];
                const last = msgs[msgs.length - 1];
                msgs[msgs.length - 1] = {
                  ...last,
                  content: last.content + event.content,
                };
                return msgs;
              });
            } else if (event.type === "done") {
              setLoading(false);
            }
          } catch {
            // skip malformed SSE lines
          }
        }
      }
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => {
        const msgs = [...prev];
        msgs[msgs.length - 1] = {
          role: "bot",
          content: "Something went wrong. Please try again.",
          isError: true,
        };
        return msgs;
      });
      setLoading(false);
    }

    inputRef.current?.focus();
  };

  const showSuggestions = messages.length === 1 && !loading;

  if (screen === "login") {
    return <Login onSuccess={handleLoginSuccess} />;
  }

  if (screen === "otp") {
    return (
      <OtpVerify
        sessionId={pendingAuth.sessionId}
        email={pendingAuth.email}
        onSuccess={handleOtpSuccess}
        onBack={handleBack}
      />
    );
  }

  return (
    <div style={styles.page}>
      <div className="chat-card" style={styles.card}>
        <div style={styles.header}>
          <div style={styles.headerRow}>
            <div>
              <h1 style={styles.title}>Ask Dhawal</h1>
              <p style={styles.subtitle}>
                An AI-powered interactive resume. Ask anything about my
                experience, skills, or projects.
              </p>
            </div>
            <button
              onClick={() => setShowInfo(true)}
              style={styles.infoButton}
              aria-label="About this chatbot"
              title="About this chatbot"
            >
              How this works ⓘ
            </button>
          </div>
        </div>

        <div style={styles.chat}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                ...styles.message,
                ...(msg.role === "user" ? styles.userMessage : styles.botMessage),
                ...(msg.isError ? styles.errorMessage : {}),
              }}
            >
              {msg.role === "bot" && msg.content === "" ? (
                <div className="typing-dots">
                  <span /><span /><span />
                </div>
              ) : (
                msg.content
              )}
            </div>
          ))}

          {showSuggestions && (
            <div style={styles.suggestions}>
              {SUGGESTIONS.map((q) => (
                <button
                  key={q}
                  style={styles.suggestionChip}
                  onClick={() => sendMessage(q)}
                >
                  {q}
                </button>
              ))}
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
            maxLength={2000}
          />
          <button
            onClick={() => sendMessage()}
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

      {showInfo && (
        <div style={styles.modalOverlay} onClick={() => setShowInfo(false)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>About this chatbot</h2>
            <p style={styles.modalText}>
              This chatbot is an AI-powered interactive resume for Dhawal
              Upadhyay. It is designed to help recruiters and hiring managers
              quickly explore his experience, skills, projects, and professional
              background through natural conversation.
            </p>
            <p style={styles.modalText}>
              At the beginning of the conversation, the assistant will request
              your name and email address to document the session for Dhawal's
              review. This information is not shared with the AI model. It is
              used solely to notify Dhawal that an interaction has taken place.
            </p>
            <p style={styles.modalText}>
              No chat content is permanently stored beyond the active session.
              Refreshing the page will restart the conversation and clear the
              current session.
            </p>
            <button style={styles.closeButton} onClick={() => setShowInfo(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #1f1f1f, #2a2a2a)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px",
    color: "#fff",
    fontFamily: "Inter, system-ui, Arial",
    transform: "translateY(-20px)",
  },
  card: {
    width: "100%",
    maxWidth: "960px",
    height: "80vh",
    margin: "0 auto",
    background: "#111",
    borderRadius: "16px",
    boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  header: {
    padding: "24px",
    borderBottom: "1px solid #222",
    flexShrink: 0,
  },
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "16px",
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
    flex: 1,
    padding: "20px",
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  message: {
    maxWidth: "75%",
    padding: "12px 16px",
    borderRadius: "14px",
    fontSize: "14px",
    lineHeight: 1.5,
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
  errorMessage: {
    background: "#3b1a1a",
    color: "#fca5a5",
  },
  suggestions: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
    marginTop: "4px",
  },
  suggestionChip: {
    padding: "8px 14px",
    borderRadius: "20px",
    border: "1px solid #374151",
    background: "transparent",
    color: "#9ca3af",
    fontSize: "13px",
    cursor: "pointer",
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
  infoButton: {
    background: "transparent",
    border: "none",
    color: "#9ca3af",
    fontSize: "14px",
    cursor: "pointer",
    padding: "4px 8px",
    whiteSpace: "nowrap",
  },
  modalOverlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.6)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  modal: {
    background: "#111",
    borderRadius: "14px",
    padding: "24px",
    maxWidth: "520px",
    width: "100%",
    boxShadow: "0 30px 60px rgba(0,0,0,0.7)",
    margin: "16px",
  },
  modalTitle: {
    marginTop: 0,
    marginBottom: "12px",
    fontSize: "20px",
  },
  modalText: {
    fontSize: "14px",
    color: "#d1d5db",
    lineHeight: 1.6,
    marginBottom: "12px",
  },
  closeButton: {
    marginTop: "16px",
    padding: "10px 16px",
    borderRadius: "8px",
    border: "none",
    background: "#4f46e5",
    color: "#fff",
    cursor: "pointer",
  },
};

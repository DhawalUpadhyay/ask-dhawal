import { useState } from "react";
import { API_BASE_URL } from "./config/api";

export default function Login({ onSuccess }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) {
      setError("Name is required.");
      return;
    }

    if (!email.trim()) {
      setError("Email is required.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/session/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim(), email: email.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Something went wrong. Please try again.");
        return;
      }
      onSuccess({ sessionId: data.session_id, name: name.trim(), email: email.trim() });
    } catch {
      setError("Could not connect. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>Ask Dhawal</h1>
        <p style={styles.subtitle}>
          An AI-powered interactive resume. Enter your details to get started.
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Your Name</label>
          <input
            style={styles.input}
            type="text"
            placeholder="e.g. Alex Johnson"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            disabled={loading}
          />

          <label style={styles.label}>Your Email</label>
          <input
            style={styles.input}
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />

          {error && <p style={styles.error}>{error}</p>}

          <button type="submit" style={{ ...styles.button, opacity: loading ? 0.6 : 1 }} disabled={loading}>
            {loading ? "Sending code…" : "Continue"}
          </button>
        </form>

        <p style={styles.note}>
          A one-time verification code will be sent to your email address.
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #1f1f1f, #2a2a2a)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px",
    fontFamily: "Inter, system-ui, Arial",
    color: "#fff",
  },
  card: {
    width: "100%",
    maxWidth: "420px",
    background: "#111",
    borderRadius: "16px",
    boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
    padding: "40px 32px",
  },
  title: {
    margin: "0 0 8px",
    fontSize: "28px",
  },
  subtitle: {
    margin: "0 0 32px",
    fontSize: "14px",
    color: "#9ca3af",
    lineHeight: 1.5,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "13px",
    color: "#9ca3af",
    marginTop: "8px",
  },
  input: {
    padding: "12px 14px",
    borderRadius: "10px",
    border: "1px solid #2d2d2d",
    background: "#1f2933",
    color: "#fff",
    fontSize: "14px",
    outline: "none",
  },
  button: {
    marginTop: "16px",
    padding: "13px",
    borderRadius: "10px",
    border: "none",
    background: "#4f46e5",
    color: "#fff",
    fontSize: "14px",
    cursor: "pointer",
    fontWeight: 600,
  },
  error: {
    margin: "4px 0 0",
    fontSize: "13px",
    color: "#fca5a5",
  },
  note: {
    marginTop: "20px",
    fontSize: "12px",
    color: "#6b7280",
    textAlign: "center",
  },
};

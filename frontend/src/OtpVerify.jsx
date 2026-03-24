import { useState, useEffect, useRef } from "react";
import { API_BASE_URL } from "./config/api";

export default function OtpVerify({ sessionId, email, onSuccess, onBack }) {
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (otp.trim().length !== 6) {
      setError("Please enter the 6-digit code.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/session/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, otp: otp.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Verification failed. Please try again.");
        return;
      }
      onSuccess();
    } catch {
      setError("Could not connect. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleOtpChange = (e) => {
    const val = e.target.value.replace(/\D/g, "").slice(0, 6);
    setOtp(val);
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>Check your email</h1>
        <p style={styles.subtitle}>
          We sent a 6-digit code to <strong style={{ color: "#e5e7eb" }}>{email}</strong>.
          Enter it below to continue.
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Verification Code</label>
          <input
            ref={inputRef}
            style={styles.otpInput}
            type="text"
            inputMode="numeric"
            placeholder="000000"
            value={otp}
            onChange={handleOtpChange}
            maxLength={6}
            disabled={loading}
          />

          {error && <p style={styles.error}>{error}</p>}

          <button
            type="submit"
            style={{ ...styles.button, opacity: loading ? 0.6 : 1 }}
            disabled={loading}
          >
            {loading ? "Verifying…" : "Verify & Start Chat"}
          </button>
        </form>

        <button style={styles.backButton} onClick={onBack}>
          ← Use a different email
        </button>
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
    lineHeight: 1.6,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "13px",
    color: "#9ca3af",
  },
  otpInput: {
    padding: "14px",
    borderRadius: "10px",
    border: "1px solid #2d2d2d",
    background: "#1f2933",
    color: "#fff",
    fontSize: "22px",
    letterSpacing: "0.3em",
    textAlign: "center",
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
  backButton: {
    marginTop: "20px",
    display: "block",
    width: "100%",
    background: "transparent",
    border: "none",
    color: "#6b7280",
    fontSize: "13px",
    cursor: "pointer",
    textAlign: "center",
  },
};

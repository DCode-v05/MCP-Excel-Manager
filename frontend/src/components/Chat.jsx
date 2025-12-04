// frontend/src/components/Chat.jsx
import { useState } from "react";
import { sendChatMessage } from "../services/api";

function Chat({ onChatResponse, onDataTable, onChartData }) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    if (!message.trim()) return;

    setLoading(true);

    try {
      const reply = await sendChatMessage(message);

      // Send text answer to App.jsx
      onChatResponse(reply);

      // Reset UI extras (user may not want tables/charts)
      onDataTable([]);
      onChartData([]);

      // Here, later we can detect "data:" or "chart:" markers from Gemini
      // Example:
      // if reply.startsWith("table:") => parse and onDataTable(rows)

    } catch (error) {
      onChatResponse("Error: " + error);
    }

    setMessage("");
    setLoading(false);
  }

  function handleEnter(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-container">
      <h3>Ask the CRM Assistant</h3>

      <textarea
        className="chat-input"
        rows={4}
        placeholder="Ask anything about Salesforce or Excel files (@accounts.xlsx)"
        value={message}
        onKeyDown={handleEnter}
        onChange={(e) => setMessage(e.target.value)}
      />

      <button
        disabled={loading}
        onClick={handleSend}
        className="send-btn"
      >
        {loading ? "Working..." : "Send"}
      </button>
    </div>
  );
}

export default Chat;

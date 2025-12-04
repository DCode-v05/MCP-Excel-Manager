// frontend/src/services/api.js
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// ----------------------------
// Axios instance
// ----------------------------
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// ----------------------------
// Utility: error extractor
// ----------------------------
function unwrapError(error) {
  if (error?.response?.data?.error) return error.response.data.error;
  if (error?.response?.data?.detail) return error.response.data.detail;
  return "Unexpected error";
}

// ----------------------------
// General Chat Endpoint
// ----------------------------

export async function sendChatMessage(message) {
  try {
    const res = await api.post("/chat", { message });
    return res.data.reply;
  } catch (e) {
    throw unwrapError(e);
  }
}

export default {
  sendChatMessage,
};

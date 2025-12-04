// frontend/src/components/Loader.jsx
import React from "react";
import "./Loader.css";

function Loader({ text = "Loading..." }) {
  return (
    <div className="loader-container">
      <div className="loader-spinner"></div>
      <p className="loader-text">{text}</p>
    </div>
  );
}

export default Loader;

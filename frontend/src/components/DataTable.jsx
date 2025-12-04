// frontend/src/components/DataTable.jsx
import React from "react";

function DataTable({ rows }) {
  if (!rows || rows.length === 0) {
    return null;
  }

  // Auto-detect columns from first row
  const columns = Object.keys(rows[0]);

  return (
    <div className="data-table">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>
                {col.replace(/_/g, " ").toUpperCase()}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col}>
                  {formatValue(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// --- helper ---
function formatValue(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return value.toString();
}

export default DataTable;

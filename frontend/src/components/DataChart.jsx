// frontend/src/components/DataChart.jsx
import React from "react";
import {
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  LineChart,
  Line,
  ResponsiveContainer
} from "recharts";

function DataChart({ data = [], xKey, yKey, type = "bar" }) {
  if (!data?.length) return null;
  if (!xKey || !yKey) return <p>Chart requires xKey and yKey.</p>;

  return (
    <div style={{ width: "100%", height: "350px", marginTop: "14px" }}>
      <ResponsiveContainer>
        {type === "line" ? (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xKey} />
            <YAxis dataKey={yKey} />
            <Tooltip />
            <Line type="monotone" dataKey={yKey} stroke="#007aff" />
          </LineChart>
        ) : (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xKey} />
            <YAxis dataKey={yKey} />
            <Tooltip />
            <Bar dataKey={yKey} fill="#007aff" />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

export default DataChart;

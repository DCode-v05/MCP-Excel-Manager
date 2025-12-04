import { useState } from "react";
import "./styles/App.css";

import Chat from "./components/Chat";
import DataTable from "./components/DataTable";
import DataChart from "./components/DataChart";

function App() {
  const [chatResult, setChatResult] = useState("");
  const [tableData, setTableData] = useState([]);
  const [chartData, setChartData] = useState([]);

  return (
    <div className="app-container">
      <header className="nav-bar">
        <h2>Salesforce CRM Assistant</h2>
        {}
      </header>

      <main className="main-content">
        <div className="left-panel">
          <Chat
            onChatResponse={(reply) => setChatResult(reply)}
            onDataTable={(rows) => setTableData(rows)}
            onChartData={(data) => setChartData(data)}
          />
        </div>

        <div className="right-panel">
          {chatResult && (
            <div className="chat-output">
              <h4>Assistant Response</h4>
              <p>{chatResult}</p>
            </div>
          )}

          {tableData?.length > 0 && (
            <DataTable rows={tableData} />
          )}

          {chartData?.length > 0 && (
            <DataChart data={chartData} />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;

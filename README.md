# MCP Excel Sheet Manager

## Project Description
This project is an advanced AI assistant that leverages the **Model Context Protocol (MCP)** to bridge Large Language Models (LLMs) like Google Gemini with local data sources. Currently focused on Excel integration, it allows users to chat with their spreadsheets—reading, analyzing, and modifying data through natural language commands. The application features a modern React frontend and a robust FastAPI backend acting as an MCP Client.

---

## Project Details

### Problem Statement
Interacting with structured data in files like Excel often requires manual manipulation or complex scripting. This project solves that by allowing users to use natural language to query and update their data, powered by the reasoning capabilities of Gemini and the standardized tool interface of MCP.

### Key Features
- **Natural Language Data Interaction:** Chat with your Excel files (e.g., "Show me rows in accounts.xlsx where revenue > 5000").
- **MCP Integration:** Uses a dedicated MCP Server (`excel_mcp_server.py`) to handle file operations safely.
- **Context Awareness:** Supports `@mentions` (e.g., `@filename.xlsx`) to automatically inject file context into the chat.
- **Data Visualization:** Frontend components to render result tables and charts dynamically.
- **Dual-Agent Architecture:**
  - **FastAPI Backend:** Acts as the Orchestrator/Client.
  - **MCP Server:** Specific process for handling Excel tools.

### Tech Stack
- **Backend Framework:** FastAPI (Python)
- **AI/LLM:** Google Gemini API
- **Protocol:** Model Context Protocol (MCP) / FastMCP
- **Data Processing:** Pandas
- **Frontend:** React, Vite
- **Styling:** Vanilla CSS

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DCode-v05/MCP-Excel-Manager.git
cd MCP-Excel-Manager
```

### 2. Install dependencies
**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 3. Run the Application
**Backend:**
Start the FastAPI server (which automatically connects to the internal MCP server):
```bash
# From the root directory
python -m backend.main
# OR using uvicorn directly
uvicorn backend.main:app --reload
```

**Frontend:**
Start the React development server:
```bash
cd frontend
npm run dev
```

---

## Usage
- **Chat Interface:** Open the web app (default `http://localhost:5173`) to interact with the assistant.
- **File Access:** Ensure your Excel files are placed in the `excel_data/` directory.
- **Commands:**
    - "List all Excel files."
    - "Read the content of @accounts.xlsx."
    - "Add a new contact to contacts.xlsx with name 'Alice'."

---

## Project Structure
```
MCP-Excel-Manager/
│
├── backend/
│   ├── api/
│   │   ├── models.py              # Pydantic models for request/response validation
│   │   └── routes.py              # API endpoint definitions
│   ├── core/
│   │   ├── chat.py                # Base chat logic class
│   │   └── ui_chat.py             # Chat handler with context injection support
│   ├── mcp/
│   │   ├── excel_mcp_server.py    # MCP server defining Excel tools
│   │   ├── mcp_client.py          # Client to communicate with the MCP server
│   │   └── tool_manager.py        # Logic for managing and retrieving tools
│   ├── services/
│   │   └── gemini_service.py      # Wrapper service for Google Gemini API
│   ├── utils/
│   │   ├── error_handlers.py      # Custom exception handlers
│   │   └── logger.py              # Logging configuration setup
│   ├── config.py                  # Environment and application configuration
│   └── main.py                    # Application entry point (FastAPI + MCP init)
│
├── excel_data/
│   ├── Accounts.xlsx              # Sample accounts data for testing
│   ├── Features.xlsx              # Sample features data
│   ├── Leads.xlsx                 # Sample leads data
│   ├── Opportunities.xlsx         # Sample opportunities data
│   ├── Sample.xlsx                # Generic sample Excel file
│   └── Workflows.xlsx             # Sample workflows data
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.jsx           # Main chat interface component
│   │   │   ├── DataChart.jsx      # Component to visualize data charts
│   │   │   ├── DataTable.jsx      # Component to display data tables
│   │   │   └── Loader.jsx         # Loading spinner indicator
│   │   ├── services/
│   │   │   └── api.js             # API service for backend communication
│   │   ├── styles/
│   │   │   ├── App.css            # Main application styles
│   │   │   └── Loader.css         # Styles for the loader component
│   │   ├── App.jsx                # Root React component layout
│   │   └── index.jsx              # Application entry point
│   ├── index.html                 # Main HTML template
│   ├── package-lock.json          # NPM dependency lock file
│   ├── package.json               # NPM project dependencies
│   └── vite.config.js             # Vite build configuration
│
├── .gitignore                     # Git ignore rules
├── README.md                      # Project documentation
└── requirements.txt               # Backend Python dependencies
```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
File Structure: 
Salesforce MCP/
│
├── backend/
│   ├── __init__.py
│   ├── main.py                          # FastAPI entry point
│   ├── config.py                        # Configuration management
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── salesforce_oauth.py          # Salesforce OAuth handler
│   │   └── token_manager.py             # Token storage & refresh
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                    # API endpoints
│   │   └── models.py                    # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── salesforce_service.py        # Salesforce API client
│   │   ├── gemini_service.py            # Gemini API wrapper
│   │   └── data_transformer.py          # Data transformation logic
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── mcp_client.py                # MCP client (reused from your code)
│   │   ├── excel_mcp_server.py          # MCP server for Excel operations
│   │   └── tool_manager.py              # Tool management (adapted)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── chat.py                      # Base chat logic
│   │   └── ui_chat.py                   # UI-specific chat handler
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                    # Logging configuration
│       └── error_handlers.py            # Custom error handlers
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx                      # Main React component
│   │   ├── index.jsx                    # React entry point
│   │   ├── components/
│   │   │   ├── Chat.jsx                 # Chat interface
│   │   │   ├── DataTable.jsx            # Table display
│   │   │   ├── DataChart.jsx            # Chart display
│   │   │   └── SalesforceAuth.jsx       # OAuth flow UI
│   │   ├── services/
│   │   │   └── api.js                   # API client
│   │   └── styles/
│   │       └── App.css
│   ├── package.json
│   └── vite.config.js
│
├── excel_data/                          # Excel files storage
│   ├── accounts.xlsx
│   ├── opportunities.xlsx
│   └── contacts.xlsx
│
├── logs/                                # Application logs
│
├── .env                                 # Environment variables
├── requirements.txt                     # Python dependencies
├── README.md                            # Documentation
└── docker-compose.yml                   # Optional: containerization
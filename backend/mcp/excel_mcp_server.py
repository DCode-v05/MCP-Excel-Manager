# backend/mcp/excel_mcp_server.py
from typing import List, Optional
from pathlib import Path
import pandas as pd
from pydantic import Field

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

EXCEL_DIR = Path("excel_data")

mcp = FastMCP("ExcelMCP", log_level="INFO")


# ------------------------------
# Helpers
# ------------------------------

def _resolve_file(file_name: str) -> Path:
    """
    Validate requested file is inside EXCEL_DIR and exists.
    Prevents directory traversal!
    """
    file_path = EXCEL_DIR / file_name
    if not file_path.exists():
        raise ValueError(f"Excel file '{file_name}' not found.")
    return file_path


# ------------------------------
# MCP TOOLS
# ------------------------------

@mcp.tool(
    name="list_excel_files",
    description="Returns list of available Excel file names in excel_data/"
)
def list_excel_files() -> List[str]:
    return [f.name for f in EXCEL_DIR.glob("*.xlsx")]


@mcp.tool(
    name="read_sheet",
    description="Reads entire sheet from an Excel file and returns table data."
)
def read_sheet(
    file_name: str = Field(description="Excel file name"),
    sheet_name: Optional[str] = Field(
        default=None, description="Sheet to read, default first sheet"
    ),
) -> List[dict]:
    file_path = _resolve_file(file_name)
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df.to_dict(orient="records")


@mcp.tool(
    name="read_range",
    description="Reads specified rows from a sheet"
)
def read_range(
    file_name: str = Field(description="Excel file name"),
    sheet_name: str = Field(description="Sheet name"),
    start_row: int = Field(description="Start row index (0-based)"),
    end_row: int = Field(description="End row index (inclusive)"),
) -> List[dict]:
    file_path = _resolve_file(file_name)
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    sliced = df.iloc[start_row : end_row + 1]
    return sliced.to_dict(orient="records")


@mcp.tool(
    name="write_cell",
    description="Write value into specific cell in Excel sheet"
)
def write_cell(
    file_name: str = Field(description="Excel file"),
    sheet_name: str = Field(description="Sheet name"),
    row: int = Field(description="Row index (0-based)"),
    col: int = Field(description="Column index (0-based)"),
    value: str = Field(description="Updated value"),
):
    file_path = _resolve_file(file_name)
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    df.iat[row, col] = value
    df.to_excel(file_path, sheet_name=sheet_name, index=False)

    return f"Cell [{row}, {col}] updated in '{file_name}'."


@mcp.tool(
    name="append_row",
    description="Append a new row (as dict) to sheet"
)
def append_row(
    file_name: str = Field(description="Excel file"),
    sheet_name: str = Field(description="Sheet"),
    row_data: dict = Field(description="New row as {colName: value}")
):
    file_path = _resolve_file(file_name)
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    df.to_excel(file_path, sheet_name=sheet_name, index=False)

    return f"Row added to '{file_name}'."

if __name__ == "__main__":
    mcp.run(transport="stdio")
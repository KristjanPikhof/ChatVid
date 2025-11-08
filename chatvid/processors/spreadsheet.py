"""
Spreadsheet file processor.

Handles Excel (.xlsx, .xls) and CSV (.csv) files using pandas.
Supports multi-sheet extraction and configurable row limits.
"""

import os
from pathlib import Path
from .base import DocumentProcessor, ProcessorRegistry


@ProcessorRegistry.register
class SpreadsheetProcessor(DocumentProcessor):
    """Processor for spreadsheet files (Excel and CSV)"""

    name = "Spreadsheet"
    extensions = [".xlsx", ".xls", ".csv"]
    dependencies = ["pandas", "openpyxl", "xlrd", "tabulate"]

    def extract_text(self, file_path: Path) -> str:
        """Extract text from spreadsheet file.

        Converts spreadsheet data to markdown-formatted tables for LLM processing.
        Supports multiple sheets in Excel files. CSV files are processed as single sheets.

        Args:
            file_path: Path to the spreadsheet file

        Returns:
            Extracted text with markdown-formatted tables
        """
        try:
            import pandas as pd
            import sys

            # Get configurable row limit from environment
            max_rows = int(os.getenv("MAX_SPREADSHEET_ROWS", "10000"))

            file_ext = file_path.suffix.lower()
            text_parts = []

            if file_ext == ".csv":
                # Handle CSV files
                try:
                    df = pd.read_csv(file_path, encoding='utf-8', nrows=max_rows, on_bad_lines='skip')
                except UnicodeDecodeError:
                    # Fallback to latin1 encoding
                    df = pd.read_csv(file_path, encoding='latin1', errors='ignore', nrows=max_rows, on_bad_lines='skip')

                if not df.empty:
                    # Convert to markdown table with text wrapping
                    table_text = df.to_markdown(index=False, tablefmt='pipe')
                    text_parts.append(f"## Data\n\n{table_text}\n")

                    # Add truncation warning if needed
                    if len(df) == max_rows:
                        text_parts.append(f"\n[Note: Data truncated at {max_rows} rows]\n")

            elif file_ext in [".xlsx", ".xls"]:
                # Handle Excel files
                engine = 'openpyxl' if file_ext == ".xlsx" else 'xlrd'

                try:
                    # Read all sheets
                    excel_file = pd.ExcelFile(file_path, engine=engine)
                    sheet_names = excel_file.sheet_names

                    for sheet_name in sheet_names:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=max_rows)

                        # Skip empty sheets
                        if df.empty:
                            continue

                        # Add sheet header
                        text_parts.append(f"## Sheet: {sheet_name}\n")

                        # Convert to markdown table with text wrapping
                        table_text = df.to_markdown(index=False, tablefmt='pipe')
                        text_parts.append(f"{table_text}\n")

                        # Add truncation warning if needed
                        if len(df) == max_rows:
                            text_parts.append(f"\n[Note: Sheet data truncated at {max_rows} rows]\n")

                        text_parts.append("\n")

                except Exception as e:
                    # Some .xls files are actually HTML files - try reading as HTML
                    if file_ext == ".xls" and "Expected BOF record" in str(e):
                        try:
                            # Try reading as HTML table
                            dfs = pd.read_html(file_path)
                            if dfs:
                                for i, df in enumerate(dfs, 1):
                                    if not df.empty:
                                        text_parts.append(f"## Table {i}\n")
                                        table_text = df.to_markdown(index=False, tablefmt='pipe')
                                        text_parts.append(f"{table_text}\n\n")
                            else:
                                print(f"Warning: {file_path.name} appears to be HTML format but no tables found", file=sys.stderr)
                                return ""
                        except Exception as html_error:
                            print(f"Error reading {file_path.name}: {e}", file=sys.stderr)
                            return ""
                    else:
                        print(f"Error reading Excel sheet: {e}", file=sys.stderr)
                        return ""

            return "\n".join(text_parts)

        except Exception as e:
            import sys
            print(f"Error reading spreadsheet {file_path.name}: {e}", file=sys.stderr)
            return ""

    def get_metadata(self, file_path: Path) -> dict:
        """Extract metadata from spreadsheet.

        Args:
            file_path: Path to the spreadsheet file

        Returns:
            Dictionary with metadata (sheet count, rows, columns)
        """
        try:
            import pandas as pd

            file_ext = file_path.suffix.lower()
            metadata = {}

            if file_ext == ".csv":
                df = pd.read_csv(file_path, nrows=1)
                metadata['sheet_count'] = 1
                metadata['total_columns'] = len(df.columns)

                # Get actual row count
                row_count = sum(1 for _ in open(file_path, 'r', encoding='utf-8', errors='ignore'))
                metadata['total_rows'] = row_count - 1  # Subtract header

            elif file_ext in [".xlsx", ".xls"]:
                engine = 'openpyxl' if file_ext == ".xlsx" else 'xlrd'
                excel_file = pd.ExcelFile(file_path, engine=engine)

                metadata['sheet_count'] = len(excel_file.sheet_names)
                metadata['sheet_names'] = excel_file.sheet_names

                # Get total rows and columns across all sheets
                total_rows = 0
                total_cols = 0
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, nrows=1)
                    if not df.empty:
                        total_cols = max(total_cols, len(df.columns))

                    # Count rows in sheet
                    df_full = pd.read_excel(excel_file, sheet_name=sheet_name)
                    total_rows += len(df_full)

                metadata['total_rows'] = total_rows
                metadata['total_columns'] = total_cols

            return metadata

        except Exception:
            return {}

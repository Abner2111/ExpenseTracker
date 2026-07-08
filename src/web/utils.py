def spreadsheet_url(sheet_id: str | None) -> str | None:
    if not sheet_id:
        return None
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

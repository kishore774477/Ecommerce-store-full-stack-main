import ast
import json
import os
import tempfile
import threading

import pandas as pd

# Streamlit serves each browser session on its own thread, and the API may run
# alongside it, so every read-modify-write of a CSV file holds this lock.
data_lock = threading.RLock()


def load_csv(file_path: str) -> pd.DataFrame:
    """Loads a CSV file into a pandas DataFrame (empty if missing or blank)."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return pd.DataFrame()
    return pd.read_csv(file_path)


def save_csv(df: pd.DataFrame, file_path: str):
    """Saves a DataFrame atomically so a crash never leaves a half-written file."""
    directory = os.path.dirname(file_path) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            df.to_csv(fh, index=False)
        os.replace(tmp_path, file_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def next_id(df: pd.DataFrame, column: str = "id") -> int:
    """Returns max(id) + 1, which stays unique even after rows are deleted."""
    if df.empty or column not in df.columns or df[column].dropna().empty:
        return 1
    return int(df[column].max()) + 1


def parse_items(items) -> dict:
    """Parses an order's items column into {product_id: quantity}.

    New orders store JSON; older orders stored str(dict), which is read with
    ast.literal_eval (never eval) for backwards compatibility.
    """
    if isinstance(items, dict):
        raw = items
    elif not isinstance(items, str) or not items.strip():
        return {}
    else:
        try:
            raw = json.loads(items)
        except (ValueError, TypeError):
            try:
                raw = ast.literal_eval(items)
            except (ValueError, SyntaxError):
                return {}
    if not isinstance(raw, dict):
        return {}
    parsed = {}
    for pid, qty in raw.items():
        try:
            parsed[int(pid)] = int(qty)
        except (ValueError, TypeError):
            continue
    return parsed


def format_price(amount) -> str:
    from config.settings import CURRENCY

    return f"{CURRENCY}{float(amount):,.2f}"

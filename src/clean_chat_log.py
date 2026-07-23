"""
Clean the raw UrbanCart chat query log (full pipeline).

Text normalization (ftfy/emoji/regex) + empty-message handling + intelligent
deduplication (same customer + same text within a time window), with an audit log.
The ground-truth label (true_intent) is never touched.
Run:  python src/clean_chat_log.py
Input:  data/raw/urbancart_chat_query_log_raw.csv
Output: data/processed/urbancart_chat_query_log_clean.csv  +  logs/chat_cleaning_audit.log
"""

import re
import html
import logging
from pathlib import Path

import pandas as pd
import ftfy
import emoji

RAW_PATH = "data/raw/urbancart_chat_query_log_raw.csv"
CLEAN_PATH = "data/processed/urbancart_chat_query_log_clean.csv"
DUP_WINDOW_SECONDS = 300   # same customer + same text within 5 min = a double-send

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    filename="logs/chat_cleaning_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


# ---------- text-normalization helpers (tested in 5.4c) ----------
def strip_html(text: str) -> str:
    text = html.unescape(text)
    return re.sub(r"<[^>]+>", "", text)


def fix_encoding(text: str) -> str:
    return ftfy.fix_text(text)


def strip_emojis(text: str) -> str:
    return emoji.replace_emoji(text, replace="")


def redact_pii(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[EMAIL]", text)
    text = re.sub(r"\b\d{7,}\b", "[PHONE]", text)
    return text


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    text = strip_html(text)
    text = fix_encoding(text)
    text = redact_pii(text)
    text = strip_emojis(text)
    text = normalize_whitespace(text)
    return text


# ---------- the pipeline ----------
def run_pipeline():
    df = pd.read_csv(RAW_PATH)
    n_in = len(df)
    logging.info(f"Loaded {n_in} raw chat rows")

    # 1. Clean text (label untouched)
    df["query_text"] = df["query_text"].fillna("")   # NaN -> "" so empties are caught, not turned into "nan"
    df["cleaned_text"] = df["query_text"].apply(clean_text)
    n_changed = int((df["cleaned_text"] != df["query_text"].astype(str)).sum())
    logging.info(f"Text cleaning altered {n_changed} rows")

    # 2. Drop empty messages (no information to answer — safe here, unlike a catalog row)
    empty_mask = df["cleaned_text"].str.strip().eq("")
    n_empty = int(empty_mask.sum())
    df = df[~empty_mask].copy()
    logging.info(f"Dropped {n_empty} empty/whitespace-only messages")

    # 3. Intelligent dedup: same customer + same cleaned text within the time window
    df["ts"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["customer_id", "cleaned_text", "ts"])
    prev_ts = df.groupby(["customer_id", "cleaned_text"])["ts"].shift()
    gap_sec = (df["ts"] - prev_ts).dt.total_seconds()
    dup_mask = gap_sec.notna() & (gap_sec <= DUP_WINDOW_SECONDS)
    n_dup = int(dup_mask.sum())
    df = df[~dup_mask].drop(columns=["ts"]).copy()
    logging.info(f"Dropped {n_dup} duplicate sends (same customer+text within {DUP_WINDOW_SECONDS}s)")

    n_out = len(df)
    df.to_csv(CLEAN_PATH, index=False)
    logging.info(f"Wrote {n_out} clean rows to {CLEAN_PATH}")

    return df, {"rows_in": n_in, "text_changed": n_changed,
                "empty_dropped": n_empty, "dupes_dropped": n_dup, "rows_out": n_out}


if __name__ == "__main__":
    df_clean, stats = run_pipeline()
    print("Chat cleaning complete:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print("\nSample cleaned rows (original -> cleaned):")
    print(df_clean[["query_text", "cleaned_text", "true_intent"]].head(8).to_string(index=False))
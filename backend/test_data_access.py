import sys
import os
import traceback
import io

# Force stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import FAISS_DIR, PROCESSED_DIR
from retrievers.faiss_retriever import load_faiss_indexes
from agent.tools import _load_order_df, _load_seller_df

def test_access():
    with open('dataset_check.txt', 'w', encoding='utf-8') as f:
        f.write("="*60 + "\nDATA ACCESS CHECK\n" + "="*60 + "\n")
        f.write(f"FAISS Dir: {FAISS_DIR}\n")
        f.write(f"Processed Dir: {PROCESSED_DIR}\n\n")

        f.write("[1/2] Checking FAISS Indexes and Chunk JSONs...\n")
        try:
            indexes, chunks = load_faiss_indexes()
            f.write("\n  >> SUCCESS: FAISS data loaded.\n")
            for k, v in indexes.items():
                f.write(f"     - index '{k}': {v.ntotal:,} vectors\n")
            for k, v in chunks.items():
                f.write(f"     - chunks '{k}': {len(v):,} records\n")
        except Exception as e:
            f.write(f"\n  >> FAILED to load FAISS data: {e}\n")
            f.write(traceback.format_exc() + "\n")

        f.write("\n[2/2] Checking Agent Parquet datasets...\n")
        try:
            df_order = _load_order_df()
            if df_order.empty:
                f.write("  >> WARNING: Orders Parquet is empty or missing.\n")
            else:
                f.write(f"  >> SUCCESS: Orders Parquet loaded. Rows: {len(df_order):,}\n")
        except Exception as e:
            f.write(f"  >> FAILED to load Orders Parquet: {e}\n")
            f.write(traceback.format_exc() + "\n")

        try:
            df_seller = _load_seller_df()
            if df_seller.empty:
                f.write("  >> WARNING: Sellers Parquet is empty or missing.\n")
            else:
                f.write(f"  >> SUCCESS: Sellers Parquet loaded. Rows: {len(df_seller):,}\n")
        except Exception as e:
            f.write(f"  >> FAILED to load Sellers Parquet: {e}\n")
            f.write(traceback.format_exc() + "\n")
            
        f.write("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_access()

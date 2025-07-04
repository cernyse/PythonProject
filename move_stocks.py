import os
import shutil

files_to_move = [
    "MSFT.csv", "TSLA.csv", "GOOG.csv", "AMZN.csv", "META.csv",
    "NVDA.csv", "SP500.csv", "SQ.csv", "BBBY.csv", "BRK.B.csv", "YNDX.csv"
]

# Go up one level from the current script location
source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
target_dir = os.path.join(source_dir, "fixed_stock_data")

os.makedirs(target_dir, exist_ok=True)

for file in files_to_move:
    src_path = os.path.join(source_dir, file)
    dst_path = os.path.join(target_dir, file)

    try:
        shutil.move(src_path, dst_path)
        print(f"✅ Moved: {file}")
    except FileNotFoundError:
        print(f"❌ File not found: {file}")
    except Exception as e:
        print(f"⚠️ Error moving {file}: {e}")

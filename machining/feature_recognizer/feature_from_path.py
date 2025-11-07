# feature_from_path.py
import os
import sys
from feature_recognizer import main

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: feature_from_path.py <input_file> [operation]")
        sys.exit(1)

    aSource = os.path.abspath(sys.argv[1])
    anOperation = sys.argv[2] if len(sys.argv) == 3 else "milling"

    sys.exit(main(aSource, anOperation))


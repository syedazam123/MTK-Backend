import sys
from dfm_analyzer import main
if __name__ == "__main__":
   # Usage: python dfm_from_path.py C:\path\to\file.stp
   if len(sys.argv) < 2:
       print("No file path provided.")
       sys.exit(1)
   aSource = sys.argv[1]
   anOperation = "milling"
   sys.exit(main(aSource, anOperation))
# app.py
from flask import Flask, render_template, request, send_from_directory, jsonify, send_file
from flask_cors import CORS
import subprocess
from pathlib import Path
import os
import json
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR = Path(__file__).parent.resolve()
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

PYTHON_EXE = r"C:\MTK\python_pilot\.venv\Scripts\python.exe"
FEATURE_SCRIPT = r"C:\MTK\python\machining\feature_recognizer\feature_from_path.py"
DFM_SCRIPT = r"C:\MTK\python\machining\dfm_analyzer\dfm_from_path.py"
CONVERTER_SCRIPT = r"C:\MTK\python\MTKConverter\MTKConverter.py"

IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None
RAILWAY_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")

def get_base_url():
    if IS_RAILWAY and RAILWAY_DOMAIN:
        return f"https://{RAILWAY_DOMAIN}"
    return "http://127.0.0.1:5000"

def read_measurements_from_json(converted_folder: str) -> dict:
    """
    Prefer process_metrics.json (written by feature_recognizer),
    fallback to process_data.json variants.
    """
    metrics_path = Path(converted_folder) / "process_metrics.json"
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            m = data.get("measurements", {})
            return {
                "volume": (m.get("volume") or {}).get("value", "N/A"),
                "surface_area": (m.get("surfaceArea") or {}).get("value", "N/A"),
                "centroid": (m.get("centroid") or {}).get("value", "N/A"),
            }
        except Exception as e:
            print(f"[WARNING] Failed to parse {metrics_path}: {e}")

    json_path = Path(converted_folder) / "process_data.json"
    if not json_path.exists():
        print(f"[INFO] process_data.json not found at {json_path}")
        return {"volume": "N/A", "surface_area": "N/A", "centroid": "N/A"}

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Variant A: data["parts"][0]["measurements"] (if some pipeline still writes it)
        if isinstance(data, dict) and "parts" in data and len(data["parts"]) > 0:
            meas = data["parts"][0].get("measurements", {})
            if meas:
                return {
                    "volume": (meas.get("volume") or {}).get("value", "N/A"),
                    "surface_area": (meas.get("surfaceArea") or {}).get("value", "N/A"),
                    "centroid": (meas.get("centroid") or {}).get("value", "N/A"),
                }

        # Variant B: top-level measurements dict
        if "measurements" in data:
            meas = data.get("measurements", {})
            return {
                "volume": (meas.get("volume") or {}).get("value", "N/A"),
                "surface_area": (meas.get("surfaceArea") or {}).get("value", "N/A"),
                "centroid": (meas.get("centroid") or {}).get("value", "N/A"),
            }

    except Exception as e:
        print(f"[ERROR] Failed to read measurements from process_data.json: {e}")

    return {"volume": "N/A", "surface_area": "N/A", "centroid": "N/A"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('cad_file')
    if not file:
        return "No file uploaded", 400

    save_path = (UPLOAD_FOLDER / file.filename).resolve()
    file.save(str(save_path))
    stem = save_path.stem

    converted_folder = str(save_path)
    for ext in [".stp", ".STP", ".step", ".STEP"]:
        if str(save_path).lower().endswith(ext.lower()):
            converted_folder = str(save_path)[: -len(ext)] + "_mtk"
            break

    print("\n" + "="*60)
    print("[INFO] Running MTK Converter...")
    print("="*60)
    try:
        converter_out = subprocess.check_output([
            PYTHON_EXE, CONVERTER_SCRIPT,
            "-i", str(save_path),
            "-p", "machining_milling",
            "-e", converted_folder
        ], text=True, stderr=subprocess.STDOUT)
        print("[SUCCESS] MTK Converter completed")
    except subprocess.CalledProcessError as e:
        converter_out = f"[MTK Converter error]\n{e.output}"
        print(f"[ERROR] MTK Converter failed: {e.output}")

    print("\n" + "="*60)
    print("[INFO] Running Feature Recognizer...")
    print("="*60)
    try:
        # feature_from_path defaults to "milling" when operation omitted
        features_out = subprocess.check_output(
            [PYTHON_EXE, FEATURE_SCRIPT, str(save_path)],
            text=True, stderr=subprocess.STDOUT
        )
        print("[SUCCESS] Feature Recognizer completed")
    except subprocess.CalledProcessError as e:
        features_out = f"[Feature recognizer error]\n{e.output}"
        print(f"[ERROR] Feature Recognizer failed: {e.output}")

    print("\n" + "="*60)
    print("[INFO] Running DFM Analyzer...")
    print("="*60)
    try:
        dfm_out = subprocess.check_output(
            [PYTHON_EXE, DFM_SCRIPT, str(save_path)],
            text=True, stderr=subprocess.STDOUT
        )
        print("[SUCCESS] DFM Analyzer completed")
    except subprocess.CalledProcessError as e:
        dfm_out = f"[DFM error]\n{e.output}"
        print(f"[ERROR] DFM Analyzer failed: {e.output}")

    print("\n" + "="*60)
    print("[INFO] Reading measurements from JSON...")
    print("="*60)
    try:
        meas = read_measurements_from_json(converted_folder)
        print(f"[SUCCESS] Measurements retrieved: {meas}")
    except Exception as e:
        print(f"[ERROR] Failed to read measurements: {e}")
        meas = {"volume": "N/A", "surface_area": "N/A", "centroid": "N/A"}

    process = "machining_milling"
    model_name = Path(save_path).stem
    base_url = get_base_url()

    viewer_url = (
        f"http://localhost:5173/mtk-explorer/viewer/{process}/{model_name}"
        f"?server={base_url}/uploads/{model_name}_mtk"
    )

    html = f"""
    <h2>Analysis complete for: {file.filename}</h2>
    <h3>MTK Converter Output</h3>
    <pre style="white-space: pre-wrap;">{converter_out}</pre>
    <h3>Feature Recognition</h3>
    <pre style="white-space: pre-wrap;">{features_out}</pre>
    <h3>DFM Analysis</h3>
    <pre style="white-space: pre-wrap;">{dfm_out}</pre>
    <h3>Feature Measurements</h3>
    <pre>Volume (mm³): {meas.get('volume')} | Surface Area (mm²): {meas.get('surface_area')} | Centroid: {meas.get('centroid')}</pre>
    <p><strong>Converted model folder:</strong> {converted_folder}</p>
    <p>
        <a href="{viewer_url}" target="_blank"
           style="padding:10px 15px; background-color:#007BFF; color:white;
           text-decoration:none; border-radius:5px;">
           Open in 3D Viewer
        </a>
    </p>
    <p><a href="/">Analyze another file</a></p>
    """
    return html

@app.route("/uploads/<path:subpath>")
def serve_uploads(subpath):
    full_path = os.path.join(app.config["UPLOAD_FOLDER"], subpath)
    folder = os.path.dirname(full_path)
    file = os.path.basename(full_path)

    if not os.path.exists(full_path):
        return jsonify({"error": f"File not found: {subpath}"}), 404

    if file.endswith(".json"):
        return send_file(full_path, mimetype="application/json")

    return send_from_directory(folder, file)

@app.route("/api/listModels", methods=["GET"])
def list_models():
    try:
        models = [
            d for d in os.listdir(app.config["UPLOAD_FOLDER"])
            if d.endswith("_mtk") and os.path.isdir(os.path.join(app.config["UPLOAD_FOLDER"], d))
        ]
        print(f"[INFO] listModels found: {models}")
        return jsonify(models)
    except Exception as e:
        print(f"[ERROR] listModels failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/getAllFiles", methods=["GET"])
def get_all_files():
    folder = request.args.get("folder")
    if not folder:
        return jsonify({"error": "Missing 'folder' query parameter"}), 400

    base_dir = os.path.join(app.config["UPLOAD_FOLDER"], folder)
    if not os.path.exists(base_dir):
        return jsonify({"error": f"Folder not found: {base_dir}"}), 404

    file_data = []
    for root, _, files in os.walk(base_dir):
        for fname in files:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, base_dir).replace("\\", "/")
            with open(full_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            file_data.append({
                "name": fname,
                "relativePath": rel_path,
                "buffer": encoded
            })

    print(f"[INFO] getAllFiles served {len(file_data)} files from {base_dir}")
    return jsonify(file_data)

if __name__ == "__main__":
    env_info = "Railway" if IS_RAILWAY else "Local"
    print(f"Flask server running in {env_info} mode with full CORS enabled...")
    if IS_RAILWAY:
        print(f"   Public domain: {RAILWAY_DOMAIN}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
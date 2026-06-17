import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path

# Initialize Flask App
# We specify the workspace directory files for static and templates
app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

# Configuration
# On Vercel serverless functions, the filesystem is read-only except for /tmp.
if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = Path('/tmp')
    OUTPUT_FOLDER = Path('/tmp')
    # Set environment variable so that imported scripts also write to /tmp
    os.environ['OUTPUT_FOLDER'] = '/tmp'
else:
    UPLOAD_FOLDER = Path('uploads')
    OUTPUT_FOLDER = Path('output')

ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Ensure folders exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS

# Serve main page
@app.route('/')
def index():
    return render_template('index.html')

# API for Excel Conversion
@app.route('/api/convert', methods=['POST'])
def convert_file():
    # 1. Validate request
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part in the request.'}), 400
    
    file = request.files['file']
    mode = request.form.get('mode')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file.'}), 400
    
    if not mode or mode not in ['regular', 'supply']:
        return jsonify({'success': False, 'error': 'Invalid conversion mode selected.'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Unsupported file format. Use CSV, XLSX, or XLS.'}), 400
        
    try:
        # 2. Save uploaded file
        filename = secure_filename(file.filename)
        # Ensure name is not empty after securing
        if not filename:
            filename = "uploaded_sheet" + Path(file.filename).suffix
            
        upload_path = UPLOAD_FOLDER / filename
        file.save(upload_path)
        
        # 3. Import and run the appropriate conversion script
        # Because we modified convert.py and supply.py to return (output_file, student_count)
        if mode == 'regular':
            from convert import convert_to_university_format
            output_file, students_count = convert_to_university_format(upload_path)
        else:
            from supply import main as supply_main
            output_file, students_count = supply_main(upload_path)
            
        # 4. Return success details with generated filename
        output_path = Path(output_file)
        return jsonify({
            'success': True,
            'filename': output_path.name,
            'students_count': students_count
        })
        
    except Exception as e:
        # Catch errors from scripts and format them nicely for frontend display
        print(f"Error during sheet conversion ({mode}):", str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# Route to download the output file
@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    # Sanitize download request
    filename = secure_filename(filename)
    return send_from_directory(
        directory=OUTPUT_FOLDER.resolve(),
        path=filename,
        as_attachment=True
    )

if __name__ == '__main__':
    # Add workspace to path to be absolutely sure imports work
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting University Excel Converter Flask Web App...")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(host='0.0.0.0', port=5000, debug=True)

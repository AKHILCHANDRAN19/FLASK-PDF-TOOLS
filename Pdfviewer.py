from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Check if the uploaded file is a PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the upload page
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload PDF</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                text-align: center;
            }
            .upload-form {
                margin-top: 50px;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Upload a PDF File</h1>
        <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf" required>
            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    '''

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return redirect(url_for('view_pdf', filename=filename))
    return "Invalid file format", 400

# Serve uploaded PDF files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to display the PDF using PDF.js
@app.route('/view/<filename>')
def view_pdf(filename):
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>View PDF</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }}
            #pdf-container {{
                width: 100%;
                height: 100vh;
                overflow: auto;
                background: #f0f0f0;
                text-align: center;
            }}
            canvas {{
                margin: 10px auto;
                display: block;
                border: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <h1>PDF Viewer</h1>
        <div id="pdf-container"></div>
        <script>
            const url = '/uploads/{filename}';
            const pdfContainer = document.getElementById('pdf-container');

            // Load PDF
            const loadingTask = pdfjsLib.getDocument(url);
            loadingTask.promise.then(pdf => {{
                for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {{
                    pdf.getPage(pageNumber).then(page => {{
                        const viewport = page.getViewport({{ scale: 1.5 }});
                        const canvas = document.createElement('canvas');
                        const context = canvas.getContext('2d');
                        canvas.width = viewport.width;
                        canvas.height = viewport.height;
                        pdfContainer.appendChild(canvas);

                        const renderContext = {{
                            canvasContext: context,
                            viewport: viewport
                        }};
                        page.render(renderContext);
                    }});
                }}
            }});
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)

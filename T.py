from flask import Flask, render_template_string, request, send_file, send_from_directory, abort
import os
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Utility Functions
def add_page_numbers(input_pdf_path, output_pdf_path, numbering_method, position):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    total_pages = len(reader.pages)

    for i in range(total_pages):
        page = reader.pages[i]
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)

        if numbering_method == 'simple':
            page_number = f"Page {i + 1} of {total_pages}"
        elif numbering_method == 'detailed':
            page_number = f"{i + 1}"
        else:
            page_number = f"Page {i + 1}"

        c.setFont("Helvetica", 10)
        if position == 'left':
            c.drawString(30, 30, page_number)
        elif position == 'middle':
            c.drawString(letter[0]/2 - 20, 30, page_number)
        elif position == 'right':
            c.drawString(letter[0] - 80, 30, page_number)

        c.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

def process_pdf_split(pdf_path, start_page, end_page):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        for page_num in range(start_page - 1, min(end_page, len(pdf_reader.pages))):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'split_output.pdf')
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        return output_path

def merge_pdfs(pdf_files):
    pdf_writer = PyPDF2.PdfWriter()

    for file in pdf_files:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

    output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'merged_output.pdf')
    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)
    return output_path

# HTML Templates
STYLE = '''
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f8f9fa;
        color: #333;
        line-height: 1.6;
    }
    header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    nav {
        background: white;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    .tool-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    .tool-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .tool-card:hover {
        transform: translateY(-5px);
    }
    .btn {
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: #1e3c72;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        transition: background 0.2s;
        border: none;
        cursor: pointer;
        font-size: 1rem;
    }
    .btn:hover {
        background: #2a5298;
    }
    form {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    input, select {
        width: 100%;
        padding: 0.8rem;
        margin: 0.5rem 0 1rem;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    label {
        font-weight: 500;
        color: #444;
    }
    .alert {
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .alert-success { background: #d4edda; color: #155724; }
    .alert-error { background: #f8d7da; color: #721c24; }
'''

# Routes
@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Tools - Professional PDF Processing</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>{{ style }}</style>
        </head>
        <body>
            <header>
                <h1>PDF Tools</h1>
                <p>Professional PDF Processing Solutions</p>
            </header>
            <div class="container">
                <div class="tool-grid">
                    <div class="tool-card">
                        <h2>PDF Splitter</h2>
                        <p>Extract specific pages from your PDF document.</p>
                        <a href="/splitter" class="btn">Split PDF</a>
                    </div>
                    <div class="tool-card">
                        <h2>PDF Merger</h2>
                        <p>Combine multiple PDF files into one document.</p>
                        <a href="/merger" class="btn">Merge PDFs</a>
                    </div>
                    <div class="tool-card">
                        <h2>Page Numbering</h2>
                        <p>Add custom page numbers to your PDF.</p>
                        <a href="/page-numbering" class="btn">Add Numbers</a>
                    </div>
                    <div class="tool-card">
                        <h2>Text Extraction</h2>
                        <p>Extract text content from PDF files.</p>
                        <a href="/extract-text" class="btn">Extract Text</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    ''', style=STYLE)

@app.route('/splitter', methods=['GET', 'POST'])
def splitter():
    if request.method == 'POST':
        try:
            file = request.files['pdf_file']
            start_page = int(request.form['start_page'])
            end_page = int(request.form['end_page'])
            
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(pdf_path)
            
            output_path = process_pdf_split(pdf_path, start_page, end_page)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Splitter - PDF Tools</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>{{ style }}</style>
        </head>
        <body>
            <header>
                <h1>PDF Splitter</h1>
                <p>Extract specific pages from your PDF</p>
            </header>
            <div class="container">
                <form method="POST" enctype="multipart/form-data">
                    <label for="pdf_file">Select PDF File:</label>
                    <input type="file" name="pdf_file" accept=".pdf" required>
                    
                    <label for="start_page">Start Page:</label>
                    <input type="number" name="start_page" min="1" required>
                    
                    <label for="end_page">End Page:</label>
                    <input type="number" name="end_page" min="1" required>
                    
                    <button type="submit" class="btn">Split PDF</button>
                </form>
            </div>
        </body>
        </html>
    ''', style=STYLE)

@app.route('/merger', methods=['GET', 'POST'])
def merger():
    if request.method == 'POST':
        try:
            files = request.files.getlist('pdf_files')
            output_path = merge_pdfs(files)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Merger - PDF Tools</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>{{ style }}</style>
        </head>
        <body>
            <header>
                <h1>PDF Merger</h1>
                <p>Combine multiple PDF files into one</p>
            </header>
            <div class="container">
                <form method="POST" enctype="multipart/form-data">
                    <label for="pdf_files">Select Multiple PDF Files:</label>
                    <input type="file" name="pdf_files" accept=".pdf" multiple required>
                    <button type="submit" class="btn">Merge PDFs</button>
                </form>
            </div>
        </body>
        </html>
    ''', style=STYLE)

@app.route('/page-numbering', methods=['GET', 'POST'])
def page_numbering():
    if request.method == 'POST':
        try:
            file = request.files['pdf_file']
            numbering_method = request.form['numbering_method']
            position = request.form['position']
            
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(input_path)
            
            output_filename = f"numbered_{file.filename}"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            add_page_numbers(input_path, output_path, numbering_method, position)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Numbering - PDF Tools</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>{{ style }}</style>
        </head>
        <body>
            <header>
                <h1>Page Numbering</h1>
                <p>Add custom page numbers to your PDF</p>
            </header>
            <div class="container">
                <form method="POST" enctype="multipart/form-data">
                    <label for="pdf_file">Select PDF File:</label>
                    <input type="file" name="pdf_file" accept=".pdf" required>
                    
                    <label for="numbering_method">Numbering Style:</label>
                    <select name="numbering_method" required>
                        <option value="simple">Page X of Y</option>
                        <option value="detailed">Numbers Only</option>
                        <option value="classic">Page X</option>
                    </select>
                    
                    <label for="position">Position:</label>
                    <select name="position" required>
                        <option value="left">Bottom Left</option>
                        <option value="middle">Bottom Center</option>
                        <option value="right">Bottom Right</option>
                    </select>
                    
                    <button type="submit" class="btn">Add Page Numbers</button>
                </form>
            </div>
        </body>
        </html>
    ''', style=STYLE)

@app.route('/extract-text', methods=['GET', 'POST'])
def extract_text():
    if request.method == 'POST':
        try:
            file = request.files['pdf_file']
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(pdf_path)
            
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            
            return render_template_string('''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Extracted Text - PDF Tools</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        {{ style }}
                        .text-content {
                            background: white;
                            padding: 2rem;
                            border-radius: 10px;
                            white-space: pre-wrap;
                            font-family: monospace;
                            margin-top: 2rem;
                        }
                    </style>
                </head>
                <body>
                    <header>
                        <h1>Extracted Text</h1>
                    </header>
                    <div class="container">
                        <div class="text-content">{{ text }}</div>
                     <a href="/extract-text" class="btn" style="margin-top: 1rem;">Extract Another PDF</a>
                    </div>
                </body>
                </html>
            ''', style=STYLE, text=text)

          return render_template_string('''
              <!DOCTYPE html>
              <html>
              <head>
                  <title>Text Extraction - PDF Tools</title>
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <style>{{ style }}</style>
            </head>
            <body>
              <header>
                  <h1>Text Extraction</h1>
                  <p>Extract text content from your PDF</p>
              </header>
                 <div class="container">
                <form method="POST" enctype="multipart/form-data">
                    <label for="pdf_file">Select PDF File:</label>
                    <input type="file" name="pdf_file" accept=".pdf" required>
                    <button type="submit" class="btn">Extract Text</button>
                </form>
                  </div>
              </body>
             </html>
           ''', style=STYLE)

@app.errorhandler(404)
def not_found_error(error):
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - Page Not Found</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>{{ style }}</style>
        </head>
        <body>
            <header>
                <h1>404 - Page Not Found</h1>
            </header>
            <div class="container">
                <div class="tool-card">
                    <h2>Oops! Page not found.</h2>
                    <p>The page you're looking for doesn't exist.</p>
                    <a href="/" class="btn">Return Home</a>
                </div>
            </div>
        </body>
        </html>
    ''', style=STYLE), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>500 - Internal Server Error</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>{{ style }}</style>
        </head>
        <body>
            <header>
                <h1>500 - Internal Server Error</h1>
            </header>
            <div class="container">
                <div class="tool-card">
                    <h2>Something went wrong!</h2>
                    <p>An unexpected error occurred. Please try again later.</p>
                    <a href="/" class="btn">Return Home</a>
                </div>
            </div>
        </body>
        </html>
    ''', style=STYLE), 500

# File cleanup function
def cleanup_old_files():
    """Clean up files older than 1 hour from upload and output folders"""
    current_time = time.time()
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.getmtime(filepath) < current_time - 3600:  # 1 hour
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error removing file {filepath}: {e}")

if __name__ == '__main__':
    import time
    from threading import Timer
    
    # Run cleanup every hour
    def schedule_cleanup():
        cleanup_old_files()
        Timer(3600, schedule_cleanup).start()
    
    schedule_cleanup()
    app.run(debug=True)

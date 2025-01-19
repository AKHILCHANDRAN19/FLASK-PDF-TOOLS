import os
from flask import Flask, render_template_string, request, send_from_directory, abort
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to add page numbers to the PDF
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
            page_number = f"{i + 1}, "
        else:
            page_number = f"Page {i + 1}"

        c.setFont("Helvetica", 10)
        if position == 'left':
            c.drawString(10, 10, page_number)
        elif position == 'middle':
            c.drawString(270, 10, page_number)  # Center position
        elif position == 'right':
            c.drawString(500, 10, page_number)

        c.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])

        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

# Function to extract pages from a PDF
def extract_pages(input_pdf_path, page_numbers, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page_num in page_numbers:
        if page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])

    with open(output_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)

# Home route with tool selection
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Page Numbering Tool Route
@app.route('/page-numbering', methods=['GET', 'POST'])
def page_numbering():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file part"
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            return "No selected file"
        
        input_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(input_pdf_path)

        numbering_method = request.form['numbering_method']
        position = request.form['position']

        output_pdf_filename = f"{os.path.splitext(pdf_file.filename)[0]}_page_numbered.pdf"
        output_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], output_pdf_filename)
        
        add_page_numbers(input_pdf_path, output_pdf_path, numbering_method, position)
        
        # Ensure the file exists and is valid before serving
        if not os.path.exists(output_pdf_path):
            abort(404, description="File not found")

        return send_from_directory(app.config['OUTPUT_FOLDER'], output_pdf_filename, as_attachment=True)
    
    return render_template_string(PAGE_NUMBERING_TEMPLATE)

# Extract Pages Tool Route
@app.route('/extract-pages', methods=['GET', 'POST'])
def extract_pages_route():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file part"
        
        pdf_file = request.files['pdf_file']
        
        if pdf_file.filename == '':
            return "No selected file"
        
        input_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(input_pdf_path)

        page_numbers = request.form['page_numbers']
        page_numbers = list(map(int, page_numbers.split(',')))  # Convert string to list of integers

        output_pdf_filename = f"{os.path.splitext(pdf_file.filename)[0]}_extracted.pdf"
        output_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], output_pdf_filename)
        extract_pages(input_pdf_path, page_numbers, output_pdf_path)
        
        # Ensure the file exists and is valid before serving
        if not os.path.exists(output_pdf_path):
            abort(404, description="File not found")

        return send_from_directory(app.config['OUTPUT_FOLDER'], output_pdf_filename, as_attachment=True)

    return render_template_string(EXTRACT_PAGES_TEMPLATE)

# HTML Template for Home Page with Tool Selection
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Tools</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f4f7;
            margin: 0;
            padding: 0;
            color: #333;
        }
        header {
            background-color: #0066cc;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
        }
        main {
            padding: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .form-container {
            background-color: white;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            width: 100%;
            max-width: 500px;
        }
        button {
            background-color: #0066cc;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }
        button:hover {
            background-color: #004d99;
        }
        footer {
            text-align: center;
            padding: 20px;
            background-color: #f0f4f7;
            color: #333;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <header>
        PDF Tools
    </header>

    <main>
        <div class="form-container">
            <h2>Select a Tool</h2>
            <a href="/page-numbering">
                <button>Page Numbering Tool</button>
            </a>
            <a href="/extract-pages">
                <button>Extract Pages Tool</button>
            </a>
        </div>
    </main>

    <footer>
        <p>Created by Your Name - PDF Processing Tools</p>
    </footer>
</body>
</html>
'''

# HTML Template for Page Numbering Tool
PAGE_NUMBERING_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Numbering Tool</title>
    <style>
        body { font-family: 'Arial', sans-serif; background-color: #f0f4f7; margin: 0; padding: 0; color: #333; }
        header { background-color: #0066cc; color: white; padding: 20px; text-align: center; font-size: 24px; }
        main { padding: 40px; display: flex; justify-content: center; align-items: center; flex-direction: column; }
        .form-container { background-color: white; padding: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border-radius: 8px; width: 100%; max-width: 500px; }
        button { background-color: #0066cc; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 20px; }
        button:hover { background-color: #004d99; }
        footer { text-align: center; padding: 20px; background-color: #f0f4f7; color: #333; margin-top: 40px; }
    </style>
</head>
<body>
    <header>
        PDF Page Numbering Tool
    </header>

    <main>
        <div class="form-container">
            <h2>Upload a PDF to Add Page Numbers</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="pdf_file" accept=".pdf" required><br><br>

                <label for="numbering_method">Choose Numbering Method:</label><br>
                <select name="numbering_method" required>
                    <option value="simple">Page 1 of 4</option>
                    <option value="detailed">1, 2, 3...</option>
                    <option value="classic">Page 1</option>
                </select><br><br>

                <label for="position">Choose Position:</label><br>
                <select name="position" required>
                    <option value="left">Bottom Left</option>
                    <option value="middle">Bottom Center</option>
                    <option value="right">Bottom Right</option>
                </select><br><br>

                <button type="submit">Upload and Add Page Numbers</button>
            </form>
        </div>
    </main>

    <footer>
        <p>Created by Your Name - PDF Processing Tools</p>
    </footer>
</body>
</html>
'''

# HTML Template for Extract Pages Tool
EXTRACT_PAGES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extract Pages Tool</title>
    <style>
        body { font-family: 'Arial', sans-serif; background-color: #f0f4f7; margin: 0; padding: 0; color: #333; }
        header { background-color: #0066cc; color: white; padding: 20px; text-align: center; font-size: 24px; }
        main { padding: 40px; display: flex; justify-content: center; align-items: center; flex-direction: column; }
        .form-container { background-color: white; padding: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border-radius: 8px; width: 100%; max-width: 500px; }
        button { background-color: #0066cc; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 20px; }
        button:hover { background-color: #004d99; }
        footer { text-align: center; padding: 20px; background-color: #f0f4f7; color: #333; margin-top: 40px; }
    </style>
</head>
<body>
    <header>
        PDF Extract Pages Tool
    </header>

    <main>
        <div class="form-container">
            <h2>Extract Pages from PDF</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="pdf_file" accept=".pdf" required><br><br>

                <label for="page_numbers">Enter Page Numbers (comma separated):</label><br>
                <input type="text" name="page_numbers" placeholder="e.g., 0,2,4" required><br><br>

                <button type="submit">Extract Pages</button>
            </form>
        </div>
    </main>

    <footer>
        <p>Created by Your Name - PDF Processing Tools</p>
    </footer>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)

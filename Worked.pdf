from flask import Flask, render_template_string, request, send_file
import os
import PyPDF2
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

# Folder to save uploaded files and outputs
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# CSS styles embedded in the script
STYLE = '''
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
        color: #333;
        padding: 20px;
    }

    header {
        text-align: center;
        margin-bottom: 30px;
    }

    h1 {
        color: #007bff;
        font-size: 2.5rem;
    }

    p {
        font-size: 1.1rem;
    }

    .btn {
        display: inline-block;
        background-color: #007bff;
        color: #fff;
        padding: 15px 30px;
        text-decoration: none;
        font-size: 1.2rem;
        border-radius: 5px;
        margin: 10px;
        text-align: center;
    }

    .btn:hover {
        background-color: #0056b3;
    }

    form {
        max-width: 500px;
        margin: 0 auto;
        background-color: #fff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }

    label {
        display: block;
        margin-bottom: 10px;
        font-size: 1rem;
    }

    input[type="file"],
    input[type="number"] {
        width: 100%;
        padding: 10px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 1rem;
    }

    input[type="number"]:focus,
    input[type="file"]:focus {
        outline: none;
        border-color: #007bff;
    }
'''

# HTML templates embedded in the script
HOME_PAGE = '''
    <html>
    <head>
        <title>PDF Tools</title>
        <style>{{ style }}</style>
    </head>
    <body>
        <header>
            <h1>PDF Tools</h1>
            <p>Welcome to the PDF tools. Select an option below:</p>
        </header>
        <div class="options">
            <a href="/splitter" class="btn">PDF Splitter</a>
            <a href="/merger" class="btn">PDF Merger</a>
            <a href="/rotate" class="btn">PDF Rotate</a>
            <a href="/extract_text" class="btn">Extract Text from PDF</a>
            <a href="/remove_page" class="btn">Remove Page from PDF</a>
            <a href="/add_page_numbers" class="btn">Add Page Numbers</a>
        </div>
    </body>
    </html>
'''

# Page to add page numbers
ADD_PAGE_NUMBERS_PAGE = '''
    <html>
    <head>
        <title>Add Page Numbers</title>
        <style>{{ style }}</style>
    </head>
    <body>
        <header>
            <h1>Add Page Numbers to PDF</h1>
            <p>Select the PDF and the numbering method:</p>
        </header>
        <form action="/add_page_numbers" method="POST" enctype="multipart/form-data">
            <label for="pdf_file">Upload PDF</label>
            <input type="file" name="pdf_file" required>

            <label for="numbering_method">Numbering Method</label>
            <select name="numbering_method" required>
                <option value="simple">Simple (Page X of Y)</option>
                <option value="detailed">Detailed (X of Y)</option>
            </select>

            <button type="submit" class="btn">Add Page Numbers</button>
        </form>
    </body>
    </html>
'''

# Function to add page numbers to the PDF
def add_page_numbers(input_pdf_path, output_pdf_path, numbering_method):
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
            page_number = f"{i + 1} of {total_pages}"

        # Add page number to the PDF
        c.setFont("Helvetica", 12)
        c.drawString(500, 10, page_number)
        c.save()

        # Merge the page with the page number
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])

        writer.add_page(page)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

# Routes for PDF tools
@app.route('/')
def home():
    return render_template_string(HOME_PAGE, style=STYLE)

# Add page numbers
@app.route('/add_page_numbers', methods=['GET', 'POST'])
def add_page_numbers_route():
    if request.method == 'POST':
        file = request.files['pdf_file']
        numbering_method = request.form['numbering_method']

        # Save uploaded PDF file
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Add page numbers
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output_with_page_numbers.pdf')
        add_page_numbers(pdf_path, output_path, numbering_method)

        return send_file(output_path, as_attachment=True)

    return render_template_string(ADD_PAGE_NUMBERS_PAGE, style=STYLE)

# PDF Splitter
@app.route('/splitter', methods=['GET', 'POST'])
def splitter():
    if request.method == 'POST':
        file = request.files['pdf_file']
        start_page = int(request.form['start_page'])
        end_page = int(request.form['end_page'])

        # Save uploaded PDF file
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Split the PDF
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_writer = PyPDF2.PdfWriter()

            for page_num in range(start_page - 1, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'split_output.pdf')
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template_string(SPLITTER_PAGE, style=STYLE)

# PDF Merger
@app.route('/merger', methods=['GET', 'POST'])
def merger():
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')
        pdf_writer = PyPDF2.PdfWriter()

        for file in files:
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(pdf_path)

            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)

        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'merged_output.pdf')
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template_string(MERGER_PAGE, style=STYLE)

# PDF Rotate
@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    if request.method == 'POST':
        file = request.files['pdf_file']
        degree = int(request.form['degree'])

        # Normalize degree to be between 0 and 360
        degree = degree % 360

        # Save uploaded PDF file
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Rotate the PDF
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_writer = PyPDF2.PdfWriter()

            for page in pdf_reader.pages:
                # Get current rotation
                current_rotation = page.get('/Rotate', 0)
                
                # Calculate new rotation
                new_rotation = (current_rotation + degree) % 360
                
                # Create a new page object
                page.rotate(new_rotation)
                pdf_writer.add_page(page)

            output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'rotated_output.pdf')
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template_string(ROTATE_PAGE, style=STYLE)

# Extract text from PDF
@app.route('/extract_text', methods=['GET', 'POST'])
def extract_text():
    if request.method == 'POST':
        file = request.files['pdf_file']

        # Save uploaded PDF file
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Extract text from the PDF
        text = ''
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)

            for page in pdf_reader.pages:
                text += page.extract_text()

        return render_template_string(EXTRACT_TEXT_PAGE, text=text, style=STYLE)

    return render_template_string(EXTRACT_TEXT_PAGE, style=STYLE)

# Remove Page from PDF
@app.route('/remove_page', methods=['GET', 'POST'])
def remove_page():
    if request.method == 'POST':
        file = request.files['pdf_file']
        page_number = int(request.form['page_number'])

        # Save uploaded PDF file
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Remove page from PDF
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            pdf_writer = PdfWriter()

            for i in range(len(pdf_reader.pages)):
                if i != page_number - 1:
                    pdf_writer.add_page(pdf_reader.pages[i])

            output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'removed_page_output.pdf')
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template_string(REMOVE_PAGE_PAGE, style=STYLE)

if __name__ == '__main__':
    app.run(debug=True)

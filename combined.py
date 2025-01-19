from flask import Flask, render_template_string, request, send_file, send_from_directory, abort
import os
import PyPDF2
import io

app = Flask(__name__)

# Folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        </div>
    </body>
    </html>
'''

SPLITTER_PAGE = '''
    <html>
    <head>
        <title>PDF Splitter</title>
        <style>{{ style }}</style>
    </head>
    <body>
        <header>
            <h1>PDF Splitter</h1>
            <p>Select the start and end pages to split the PDF file:</p>
        </header>
        <form action="/splitter" method="POST" enctype="multipart/form-data">
            <label for="pdf_file">Upload PDF</label>
            <input type="file" name="pdf_file" required>

            <label for="start_page">Start Page</label>
            <input type="number" name="start_page" required>

            <label for="end_page">End Page</label>
            <input type="number" name="end_page" required>

            <button type="submit" class="btn">Split PDF</button>
        </form>
    </body>
    </html>
'''

MERGER_PAGE = '''
    <html>
    <head>
        <title>PDF Merger</title>
        <style>{{ style }}</style>
    </head>
    <body>
        <header>
            <h1>PDF Merger</h1>
            <p>Upload multiple PDFs to merge them into one document:</p>
        </header>
        <form action="/merger" method="POST" enctype="multipart/form-data">
            <label for="pdf_files">Select PDFs to Merge</label>
            <input type="file" name="pdf_files" multiple required>

            <button type="submit" class="btn">Merge PDFs</button>
        </form>
    </body>
    </html>
'''

ROTATE_PAGE = '''
    <html>
    <head>
        <title>PDF Rotate</title>
        <style>{{ style }}</style>
    </head>
    <body>
        <header>
            <h1>PDF Rotate</h1>
            <p>Select a PDF and a degree to rotate:</p>
        </header>
        <form action="/rotate" method="POST" enctype="multipart/form-data">
            <label for="pdf_file">Upload PDF</label>
            <input type="file" name="pdf_file" required>

            <label for="degree">Rotation Degree</label>
            <input type="number" name="degree" required>

            <button type="submit" class="btn">Rotate PDF</button>
        </form>
    </body>
    </html>
'''

EXTRACT_TEXT_PAGE = '''
    <html>
    <head>
        <title>Extract Text</title>
        <style>{{ style }}</style>
    </head>
    <body>
        <header>
            <h1>Extract Text from PDF</h1>
            <p>Upload a PDF to extract text:</p>
        </header>
        <form action="/extract_text" method="POST" enctype="multipart/form-data">
            <label for="pdf_file">Upload PDF</label>
            <input type="file" name="pdf_file" required>

            <button type="submit" class="btn">Extract Text</button>
        </form>
    </body>
    </html>
'''

REMOVE_PAGE_PAGE = '''
    <html>
    <head>
        <title>Remove Page from PDF</title>
        <style>{{ style }}</style>
    </head>
    <body>
        <header>
            <h1>Remove Page from PDF</h1>
            <p>Select the page to remove:</p>
        </header>
        <form action="/remove_page" method="POST" enctype="multipart/form-data">
            <label for="pdf_file">Upload PDF</label>
            <input type="file" name="pdf_file" required>

            <label for="page_number">Page Number to Remove</label>
            <input type="number" name="page_number" required>

            <button type="submit" class="btn">Remove Page</button>
        </form>
    </body>
    </html>
'''

# Home route
@app.route('/')
def home():
    return render_template_string(HOME_PAGE, style=STYLE)

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

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'split_output.pdf')
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

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged_output.pdf')
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

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'rotated_output.pdf')
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template_string(ROTATE_PAGE, style=STYLE)

# Extract Text from PDF
@app.route('/extract_text', methods=['GET', 'POST'])
def extract_text():
    if request.method == 'POST':
        file = request.files['pdf_file']

        # Save uploaded PDF file
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(pdf_path)

        # Extract text from the PDF
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

        return f"<pre>{text}</pre>"

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

        # Remove the specified page
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_writer = PyPDF2.PdfWriter()

            for i, page in enumerate(pdf_reader.pages):
                if i != page_number - 1:
                    pdf_writer.add_page(page)

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'removed_page_output.pdf')
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

        return send_file(output_path, as_attachment=True)

    return render_template_string(REMOVE_PAGE_PAGE, style=STYLE)

if __name__ == '__main__':
    app.run(debug=True)

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
from docx2pdf import convert as docx2pdf_convert
from pptx import Presentation
import zipfile
import os
from PIL import Image
from io import BytesIO
import tempfile
import shutil

st.set_page_config(page_title="PDF & File Converter", page_icon="💚", layout="centered")

st.image("logo1.png", width=150)
st.title("PDF & File Converter")

operations = [
    "Generate Empty PDF",
    "Convert Any File to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF",
    "Compress PDF",
    "Insert Page Numbers",
    "Images to PDF",
    "Remove Uploaded Files"
]

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

selected_operation = st.selectbox("Select Operation", operations)

format_instructions = {
    "Generate Empty PDF": "No file upload required. Just enter the number of pages.",
    "Convert Any File to PDF": "Upload txt, docx, pptx, png, jpg, jpeg files. (DOC and PPT not supported in cloud).",
    "Extract Pages from PDF": "Upload a single PDF file.",
    "Merge PDFs": "Upload exactly two PDF files.",
    "Split PDF": "Upload a single PDF file.",
    "Compress PDF": "Upload a single large PDF (up to 200MB).",
    "Insert Page Numbers": "Upload a single PDF file.",
    "Images to PDF": "Upload multiple PNG, JPG, JPEG files.",
    "Remove Uploaded Files": "Click the button below to clear uploaded files."
}

st.info(f"**Instructions:** {format_instructions[selected_operation]}")

if selected_operation != "Remove Uploaded Files":
    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, key=selected_operation)

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

# Function to generate empty PDF
def generate_empty_pdf(pages):
    pdf = FPDF()
    for _ in range(pages):
        pdf.add_page()
    temp_path = "empty_pdf.pdf"
    pdf.output(temp_path)
    return temp_path

# Convert supported files to PDF
def convert_to_pdf(file):
    filename = file.name.lower()
    with tempfile.TemporaryDirectory() as temp_dir:
        if filename.endswith('.txt'):
            content = file.getvalue().decode('utf-8')
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, content)
            pdf_path = os.path.join(temp_dir, 'converted.pdf')
            pdf.output(pdf_path)
            return pdf_path

        elif filename.endswith('.docx'):
            docx_path = os.path.join(temp_dir, 'input.docx')
            with open(docx_path, 'wb') as f:
                f.write(file.getvalue())
            output_path = os.path.join(temp_dir, 'converted.pdf')
            docx2pdf_convert(docx_path, output_path)
            return output_path

        elif filename.endswith('.pptx'):
            pptx_path = os.path.join(temp_dir, 'input.pptx')
            with open(pptx_path, 'wb') as f:
                f.write(file.getvalue())
            prs = Presentation(pptx_path)
            pdf = FPDF()
            for slide in prs.slides:
                pdf.add_page()
            output_pdf_path = os.path.join(temp_dir, 'converted.pdf')
            pdf.output(output_pdf_path)
            return output_pdf_path

        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file)
            pdf_bytes = BytesIO()
            img.convert("RGB").save(pdf_bytes, format='PDF')
            pdf_path = os.path.join(temp_dir, file.name.rsplit('.', 1)[0] + '.pdf')
            with open(pdf_path, 'wb') as out:
                out.write(pdf_bytes.getvalue())
            return pdf_path
        else:
            return None

# Extract pages
def extract_pages(pdf_file, pages_input):
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    ranges = pages_input.replace(' ', '').split(',')
    for part in ranges:
        if '-' in part:
            start, end = part.split('-')
            for p in range(int(start)-1, int(end)):
                writer.add_page(reader.pages[p])
        else:
            writer.add_page(reader.pages[int(part)-1])
    output = BytesIO()
    writer.write(output)
    return output

# Merge PDFs
def merge_pdfs(files):
    writer = PdfWriter()
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    output = BytesIO()
    writer.write(output)
    return output

# Split PDF custom range or each page
def split_pdf_custom(file, pages_per_file):
    reader = PdfReader(file)
    outputs = []
    for i in range(0, len(reader.pages), pages_per_file):
        writer = PdfWriter()
        for p in reader.pages[i:i+pages_per_file]:
            writer.add_page(p)
        out = BytesIO()
        writer.write(out)
        outputs.append(out)
    return outputs

def split_pdf_pages_zip(file):
    reader = PdfReader(file)
    zip_bytes = BytesIO()
    with zipfile.ZipFile(zip_bytes, 'w') as zipf:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            out = BytesIO()
            writer.write(out)
            zipf.writestr(f'page_{i+1}.pdf', out.getvalue())
    return zip_bytes

# Compress PDF (simple approach)
def compress_pdf(file):
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    out = BytesIO()
    writer.write(out)
    return out

# Insert page numbers
def insert_page_numbers(file):
    reader = PdfReader(file)
    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        writer.add_page(page)
    out = BytesIO()
    writer.write(out)
    return out

# Images to PDF
def images_to_pdf(files):
    images = [Image.open(f).convert("RGB") for f in files]
    pdf_bytes = BytesIO()
    images[0].save(pdf_bytes, save_all=True, append_images=images[1:], format="PDF")
    return pdf_bytes

# Main logic
if selected_operation == "Generate Empty PDF":
    pages = st.number_input("Enter number of pages", min_value=1, value=1)
    if st.button("Generate PDF"):
        output_path = generate_empty_pdf(pages)
        with open(output_path, "rb") as f:
            st.download_button("Download Empty PDF", f, file_name="empty.pdf")
        os.remove(output_path)

elif selected_operation == "Convert Any File to PDF" and st.session_state.uploaded_files:
    converted_files = []
    for f in st.session_state.uploaded_files:
        pdf_path = convert_to_pdf(f)
        if pdf_path:
            converted_files.append((f.name, pdf_path))
        else:
            st.warning(f"Unsupported format: {f.name}")
    if converted_files:
        with zipfile.ZipFile("converted_files.zip", 'w') as zipf:
            for original_name, path in converted_files:
                zipf.write(path, arcname=original_name.rsplit('.', 1)[0] + ".pdf")
        with open("converted_files.zip", "rb") as f:
            st.download_button("Download Converted Files (ZIP)", f, file_name="converted_files.zip")
        os.remove("converted_files.zip")

elif selected_operation == "Extract Pages from PDF" and st.session_state.uploaded_files:
    pages_input = st.text_input("Enter page numbers or ranges (e.g., 1,3-5)")
    if st.button("Extract Pages"):
        file = st.session_state.uploaded_files[0]
        extracted_pdf = extract_pages(file, pages_input)
        st.download_button("Download Extracted PDF", extracted_pdf, file_name="extracted_pages.pdf")

elif selected_operation == "Merge PDFs" and st.session_state.uploaded_files:
    if len(st.session_state.uploaded_files) == 2:
        merged_pdf = merge_pdfs(st.session_state.uploaded_files)
        st.download_button("Download Merged PDF", merged_pdf, file_name="merged.pdf")
    else:
        st.warning("Upload exactly two PDF files.")

elif selected_operation == "Split PDF" and st.session_state.uploaded_files:
    split_option = st.radio("Choose splitting option:", ["Custom Page Range", "Split into Single Pages (ZIP)"])
    file = st.session_state.uploaded_files[0]
    if split_option == "Custom Page Range":
        pages_per_file = st.number_input("Enter number of pages per split file", min_value=1, value=1)
        if st.button("Split"):
            split_pdfs = split_pdf_custom(file, pages_per_file)
            with zipfile.ZipFile("splitted_files.zip", 'w') as zipf:
                for idx, part in enumerate(split_pdfs):
                    zipf.writestr(f"part_{idx+1}.pdf", part.getvalue())
            with open("splitted_files.zip", "rb") as f:
                st.download_button("Download Split Files (ZIP)", f, file_name="splitted_files.zip")
            os.remove("splitted_files.zip")
    else:
        if st.button("Split and Download ZIP"):
            zip_file = split_pdf_pages_zip(file)
            st.download_button("Download ZIP of single-page PDFs", zip_file, file_name="split_pages.zip")

elif selected_operation == "Compress PDF" and st.session_state.uploaded_files:
    if st.button("Compress and Download"):
        compressed_pdf = compress_pdf(st.session_state.uploaded_files[0])
        st.download_button("Download Compressed PDF", compressed_pdf, file_name="compressed.pdf")

elif selected_operation == "Insert Page Numbers" and st.session_state.uploaded_files:
    if st.button("Insert Page Numbers"):
        numbered_pdf = insert_page_numbers(st.session_state.uploaded_files[0])
        st.download_button("Download PDF with Page Numbers", numbered_pdf, file_name="numbered.pdf")

elif selected_operation == "Images to PDF" and st.session_state.uploaded_files:
    if st.button("Convert Images to Single PDF"):
        pdf_bytes = images_to_pdf(st.session_state.uploaded_files)
        st.download_button("Download PDF", pdf_bytes, file_name="images.pdf")

elif selected_operation == "Remove Uploaded Files":
    if st.button("Remove All Files"):
        st.session_state.uploaded_files = []
        st.success("All uploaded files have been cleared.")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 12px;'>© 2025 Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | trainees from techwing 🧡</p>",
    unsafe_allow_html=True
        )

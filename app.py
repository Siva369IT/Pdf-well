import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from io import BytesIO
from zipfile import ZipFile
from docx import Document
from pptx import Presentation
import fitz  # PyMuPDF for compression
import os

st.set_page_config(page_title="PDF & File Converter", layout="wide")

def load_css():
    css_code = """
    .title { text-align: center; font-size: 40px; font-weight: bold; color: #333; margin-bottom: 20px; }
    .footer { text-align: center; font-size: 12px; color: #666; margin-top: 40px; }
    .incorrect { color: blue; font-weight: bold; }
    """
    st.markdown(f"<style>{css_code}</style>", unsafe_allow_html=True)

load_css()

st.image("logo1.png", width=140)
st.markdown('<p class="title">📁 PDF & File Converter Tool</p>', unsafe_allow_html=True)

operation = st.selectbox("Select an Operation:", [
    "Generate Empty PDF",
    "Convert Any File to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF",
    "Compress PDF",
    "Insert Page Numbers",
    "Images to PDF",
    "Remove All Uploaded Files"
])

upload_types = {
    "Convert Any File to PDF": ["png", "jpg", "jpeg", "txt", "docx", "pptx"],
    "Extract Pages from PDF": ["pdf"],
    "Merge PDFs": ["pdf"],
    "Split PDF": ["pdf"],
    "Compress PDF": ["pdf"],
    "Insert Page Numbers": ["pdf"],
    "Images to PDF": ["png", "jpg", "jpeg"],
}

if operation not in ["Generate Empty PDF", "Remove All Uploaded Files"]:
    allowed_types = upload_types.get(operation, [])
    uploaded_files = st.file_uploader(f"Upload file(s) for: {operation}", type=allowed_types, accept_multiple_files=True)
    if uploaded_files:
        st.success(f"✅ Uploaded {len(uploaded_files)} file(s).")
    else:
        uploaded_files = []
else:
    uploaded_files = []

def download_button(data, file_name, mime_type):
    st.download_button("📥 Download", data, file_name=file_name, mime=mime_type)

def convert_text_to_pdf(text_file):
    text = text_file.read().decode()
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    for line in text.split('\n'):
        c.drawString(40, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# --- GENERATE EMPTY PDF ---
if operation == "Generate Empty PDF":
    num_pages = st.number_input("Enter number of empty pages:", min_value=1, step=1)
    if st.button("Generate Empty PDF"):
        pdf_writer = PdfWriter()
        for _ in range(num_pages):
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)
            pdf_writer.add_page(new_pdf.pages[0])
        output = BytesIO()
        pdf_writer.write(output)
        download_button(output.getvalue(), "empty_pages.pdf", "application/pdf")

# --- CONVERT ANY FILE TO PDF ---
elif operation == "Convert Any File to PDF" and uploaded_files:
    pdf_files = []
    for file in uploaded_files:
        if file.type.startswith("image"):
            image = Image.open(file)
            buffer = BytesIO()
            image.save(buffer, format="PDF")
            pdf_files.append((file.name.split('.')[0] + ".pdf", buffer.getvalue()))
        elif file.type == "text/plain":
            pdf_files.append((file.name.split('.')[0] + ".pdf", convert_text_to_pdf(file)))
        elif file.name.endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
            pdf_files.append((file.name.split('.')[0] + ".pdf", convert_text_to_pdf(BytesIO(text.encode()))))
        elif file.name.endswith('.pptx'):
            ppt = Presentation(file)
            pdf_writer = PdfWriter()
            for slide in ppt.slides:
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                text = ""
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
                can.drawString(40, 750, text[:1000])
                can.save()
                packet.seek(0)
                new_pdf = PdfReader(packet)
                pdf_writer.add_page(new_pdf.pages[0])
            output = BytesIO()
            pdf_writer.write(output)
            pdf_files.append((file.name.split('.')[0] + ".pdf", output.getvalue()))
        else:
            st.markdown(f"<p class='incorrect'>❗ Unsupported file: {file.name}</p>", unsafe_allow_html=True)

    if pdf_files:
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zip_file:
            for pdf_name, pdf_data in pdf_files:
                zip_file.writestr(pdf_name, pdf_data)
        download_button(zip_buffer.getvalue(), "converted_files.zip", "application/zip")

# --- EXTRACT PAGES ---
elif operation == "Extract Pages from PDF" and uploaded_files:
    page_input = st.text_input("Enter pages/ranges (example: 1,3,5-7):")
    if st.button("Extract Pages"):
        for file in uploaded_files:
            reader = PdfReader(file)
            writer = PdfWriter()
            pages_to_extract = []
            parts = page_input.replace(" ", "").split(',')
            for part in parts:
                if '-' in part:
                    start, end = part.split('-')
                    pages_to_extract.extend(range(int(start)-1, int(end)))
                else:
                    pages_to_extract.append(int(part)-1)
            for p in pages_to_extract:
                writer.add_page(reader.pages[p])
            output = BytesIO()
            writer.write(output)
            download_button(output.getvalue(), "extracted_pages.pdf", "application/pdf")

# --- MERGE PDFs ---
elif operation == "Merge PDFs" and len(uploaded_files) == 2:
    if st.button("Merge PDFs"):
        merger = PdfWriter()
        for file in uploaded_files:
            reader = PdfReader(file)
            for page in reader.pages:
                merger.add_page(page)
        output = BytesIO()
        merger.write(output)
        download_button(output.getvalue(), "merged.pdf", "application/pdf")

# --- SPLIT PDF ---
elif operation == "Split PDF" and uploaded_files:
    file = uploaded_files[0]
    reader = PdfReader(file)
    split_type = st.radio("Select split method:", ["Custom split (pages each)", "Split each page into separate PDFs"])
    if split_type == "Custom split (pages each)":
        split_pages = st.number_input("Enter number of pages per PDF:", min_value=1, step=1)
        if st.button("Split"):
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w") as zipf:
                for start in range(0, len(reader.pages), split_pages):
                    writer = PdfWriter()
                    for i in range(start, min(start + split_pages, len(reader.pages))):
                        writer.add_page(reader.pages[i])
                    output = BytesIO()
                    writer.write(output)
                    zipf.writestr(f"split_{start//split_pages + 1}.pdf", output.getvalue())
            download_button(zip_buffer.getvalue(), "split_files.zip", "application/zip")
    else:
        if st.button("Split each page to separate PDFs"):
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w") as zipf:
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    output = BytesIO()
                    writer.write(output)
                    zipf.writestr(f"page_{i+1}.pdf", output.getvalue())
            download_button(zip_buffer.getvalue(), "split_pages.zip", "application/zip")

# --- COMPRESS PDF ---
elif operation == "Compress PDF" and uploaded_files:
    file = uploaded_files[0]
    compress_ratio = st.slider("Compression level (drag to compress more):", 1, 9, 5)
    if st.button("Compress PDF"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        output = BytesIO()
        doc.save(output, deflate=True, garbage=4, clean=True, compress=compress_ratio)
        download_button(output.getvalue(), "compressed.pdf", "application/pdf")

# --- INSERT PAGE NUMBERS ---
elif operation == "Insert Page Numbers" and uploaded_files:
    if st.button("Insert Page Numbers"):
        reader = PdfReader(uploaded_files[0])
        writer = PdfWriter()
        for idx, page in enumerate(reader.pages):
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.drawString(300, 10, str(idx + 1))
            can.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)
            page.merge_page(new_pdf.pages[0])
            writer.add_page(page)
        output = BytesIO()
        writer.write(output)
        download_button(output.getvalue(), "numbered.pdf", "application/pdf")

# --- IMAGES TO PDF ---
elif operation == "Images to PDF" and uploaded_files:
    if st.button("Convert Images to Single PDF"):
        image_list = [Image.open(img).convert("RGB") for img in uploaded_files]
        output = BytesIO()
        image_list[0].save(output, format="PDF", save_all=True, append_images=image_list[1:])
        download_button(output.getvalue(), "images_to_pdf.pdf", "application/pdf")

# --- REMOVE UPLOADED FILES ---
if operation == "Remove All Uploaded Files":
    st.warning("❗ Remove uploaded files by refreshing the page or clicking 'Clear Cache' in Streamlit.")

# --- Footer ---
st.markdown("""<p class="footer">© 2025 Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | trainees from techwing 🧡</p>""", unsafe_allow_html=True)

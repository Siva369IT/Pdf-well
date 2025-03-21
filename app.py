import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz
import os

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# Load Custom CSS (Optional)
def load_css():
    if os.path.exists("assets/Style.css"):
        with open("assets/Style.css", "r") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

load_css()

st.image("logo1.png", width=150)
st.markdown('<p class="title">📄 PDF & File Converter</p>', unsafe_allow_html=True)

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

operation = st.selectbox("Select an operation:", [
    "Click me to see the operations -->",
    "Clear All Uploaded Files ❌",
    "Generate Empty PDF 🖨️",
    "Convert Any File to PDF ♻️",
    "Images to pdf 🏞️",
    "Extract Pages from PDF 🪓",
    "Merge PDFs 📄+📃",
    "Split PDF (1 to 2 📑 PDFs)",
    "Compress PDF 📉",
    "Insert Page Numbers 📝 to PDF"
])

# Clear all uploaded files
if operation == "Clear All Uploaded Files ❌":
    st.session_state.clear()
    st.success("✅ All uploaded files cleared! Session reset.")
    st.stop()

file_formats = {
    "Convert Any File to PDF ♻️": ["pdf", "png", "jpg", "jpeg", "txt", "docx", "pptx"],
    "Images to pdf 🏞️": ["png", "jpg", "jpeg"],
    "Extract Pages from PDF 🪓": ["pdf"],
    "Merge PDFs 📄+📃": ["pdf"],
    "Split PDF (1 to 2 📑 PDFs)": ["pdf"],
    "Compress PDF 📉": ["pdf"],
    "Insert Page Numbers 📝 to PDF": ["pdf"]
}

# File uploader
if operation in file_formats:
    uploaded_files = st.file_uploader(
        "Upload file(s)", type=file_formats[operation],
        accept_multiple_files=operation in ["Merge PDFs 📄+📃", "Convert Any File to PDF ♻️", "Images to pdf 🏞️"]
    )
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

files = st.session_state.uploaded_files

# Generate Empty PDF
if operation == "Generate Empty PDF 🖨️":
    pages = st.number_input("Enter number of pages:", 1, 100, 1)
    if st.button("Generate"):
        output = BytesIO()
        c = canvas.Canvas(output, pagesize=letter)
        for p in range(pages):
            c.drawString(300, 500, f"Page {p+1}")
            c.showPage()
        c.save()
        output.seek(0)
        st.download_button("Download Empty PDF", output, "Empty.pdf", "application/pdf")

# Convert Any File to PDF
if operation == "Convert Any File to PDF ♻️" and files:
    for file in files:
        name, ext = os.path.splitext(file.name)
        ext = ext[1:].lower()
        output_pdf = BytesIO()
        try:
            if ext in ["png", "jpg", "jpeg"]:
                Image.open(file).convert("RGB").save(output_pdf, format="PDF")
            elif ext == "txt":
                c = canvas.Canvas(output_pdf, pagesize=letter)
                for line in file.read().decode().split("\n"):
                    c.drawString(100, 750, line)
                    c.showPage()
                c.save()
            elif ext == "docx":
                doc = Document(file)
                c = canvas.Canvas(output_pdf, pagesize=letter)
                for para in doc.paragraphs:
                    c.drawString(100, 750, para.text)
                    c.showPage()
                c.save()
            elif ext == "pptx":
                ppt = Presentation(file)
                c = canvas.Canvas(output_pdf, pagesize=letter)
                for slide in ppt.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            c.drawString(100, 750, shape.text)
                            c.showPage()
                c.save()
            else:
                st.warning(f"Unsupported file type: {ext}")
                continue
            output_pdf.seek(0)
            st.download_button(f"Download {name}.pdf", output_pdf, f"{name}.pdf", "application/pdf")
        except Exception as e:
            st.error(f"⚠️ Error converting {file.name}: {e}")

# Images to PDF
if operation == "Images to pdf 🏞️" and files:
    st.subheader("🏞️ Convert Images to Single PDF")
    image_files = [file for file in files if file.type.startswith("image/")]
    if image_files:
        if st.button("Convert Images to PDF"):
            try:
                images = [Image.open(BytesIO(img.getvalue())).convert("RGB") for img in image_files]
                output_pdf = BytesIO()
                if images:
                    images[0].save(output_pdf, save_all=True, append_images=images[1:], format="PDF")
                    output_pdf.seek(0)
                    st.success("✅ Images converted to a single PDF!")
                    st.download_button("📥 Download PDF", output_pdf, "Images_to_PDF.pdf", "application/pdf")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
    else:
        st.warning("⚠️ Please upload image files (PNG, JPG, JPEG).")

# Extract Pages from PDF
if operation == "Extract Pages from PDF 🪓" and files:
    try:
        pdf_reader = PdfReader(BytesIO(files[0].getvalue()))
        pages = st.text_input("Enter page numbers (comma-separated):")
        if st.button("Extract Pages"):
            writer = PdfWriter()
            for p in [int(x.strip()) - 1 for x in pages.split(",") if x.strip().isdigit()]:
                writer.add_page(pdf_reader.pages[p])
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            st.download_button("Download Extracted PDF", output, "Extracted.pdf", "application/pdf")
    except Exception as e:
        st.error(f"⚠️ Error reading PDF: {e}")

# Merge PDFs
if operation == "Merge PDFs 📄+📃" and files:
    try:
        writer = PdfWriter()
        for file in files:
            reader = PdfReader(BytesIO(file.getvalue()))
            for page in reader.pages:
                writer.add_page(page)
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        st.download_button("Download Merged PDF", output, "Merged.pdf", "application/pdf")
    except Exception as e:
        st.error(f"⚠️ Merge error: {e}")

# Split PDF
if operation == "Split PDF (1 to 2 📑 PDFs)" and files:
    try:
        pdf_reader = PdfReader(BytesIO(files[0].getvalue()))
        if len(pdf_reader.pages) > 1:
            split_at = st.number_input("Split at page:", 1, len(pdf_reader.pages) - 1, 1)
            if st.button("Split PDF"):
                w1, w2 = PdfWriter(), PdfWriter()
                for i, page in enumerate(pdf_reader.pages):
                    (w1 if i < split_at else w2).add_page(page)
                out1, out2 = BytesIO(), BytesIO()
                w1.write(out1)
                w2.write(out2)
                out1.seek(0)
                out2.seek(0)
                st.download_button("Download Part 1", out1, "Split_Part1.pdf", "application/pdf")
                st.download_button("Download Part 2", out2, "Split_Part2.pdf", "application/pdf")
        else:
            st.warning("⚠️ Cannot split a single-page PDF.")
    except Exception as e:
        st.error(f"⚠️ Split error: {e}")

# Compress PDF
if operation == "Compress PDF 📉" and files:
    try:
        file_bytes = BytesIO(files[0].getvalue())
        pdf = fitz.open(stream=file_bytes, filetype="pdf")
        compressed = BytesIO()
        pdf.save(compressed, deflate=True)
        compressed.seek(0)
        st.download_button("Download Compressed PDF", compressed, "Compressed.pdf", "application/pdf")
    except Exception as e:
        st.error(f"⚠️ Compression error: {e}")

# Insert Page Numbers
if operation == "Insert Page Numbers 📝 to PDF" and files:
    try:
        reader = PdfReader(BytesIO(files[0].getvalue()))
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            overlay = BytesIO()
            c = canvas.Canvas(overlay, pagesize=letter)
            c.drawString(500, 20, f"Page {i + 1}")
            c.save()
            overlay.seek(0)
            overlay_pdf = PdfReader(overlay)
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        st.download_button("Download Numbered PDF", output, "Numbered.pdf", "application/pdf")
    except Exception as e:
        st.error(f"⚠️ Numbering error: {e}")

st.markdown('<div class="footer">© Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satya Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | Techwing Trainees 🧡</div>', unsafe_allow_html=True)

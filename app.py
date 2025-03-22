import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz  # PyMuPDF
import os
import zipfile

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# ✅ Load Custom CSS
def load_css():
    with open("assets/Style.css", "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

load_css()

# ✅ Logo
st.image("logo1.png", width=150)
st.markdown('<p class="title">📄 PDF & File Converter</p>', unsafe_allow_html=True)

# ✅ Select Operation
operation = st.selectbox("Select an operation:", [
    "Select an operation 👆",
    "Generate Empty PDF 🖨️",
    "Convert Any File to PDF ♻️",
    "Images to pdf 🏞️",
    "Extract Pages from PDF 🪓",
    "Merge PDFs 📄+📃",
    "Split PDF (1 to 2 📑 PDFs) ➡ or ➡ Split each page as separate PDF",
    "Compress PDF 📉",
    "Insert Page Numbers 📝 to PDF"
])

# ✅ Show allowed formats dynamically
operation_formats = {
    "Convert Any File to PDF ♻️": "Allowed formats: PNG, JPG, JPEG, TXT, DOCX, PPTX",
    "Images to pdf 🏞️": "Allowed formats: PNG, JPG, JPEG",
    "Extract Pages from PDF 🪓": "Upload a single PDF",
    "Merge PDFs 📄+📃": "Upload multiple PDFs",
    "Split PDF (1 to 2 📑 PDFs) ➡ or ➡ Split each page as separate PDF": "Upload a single PDF",
    "Compress PDF 📉": "Upload a single PDF",
    "Insert Page Numbers 📝 to PDF": "Upload a single PDF",
    "Generate Empty PDF 🖨️": "No file upload needed, just enter number of pages."
}
if operation in operation_formats:
    st.info(operation_formats[operation])

# ✅ Clear Uploaded Files Button below uploader
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

uploaded_files = st.file_uploader("Upload file(s):", type=["pdf", "png", "jpg", "jpeg", "docx", "pptx", "txt"], accept_multiple_files=True)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

if st.session_state.uploaded_files:
    if st.button("❌ Remove Uploaded Files"):
        st.session_state.uploaded_files = []
        st.experimental_rerun()

# ✅ Generate Empty PDF
if operation == "Generate Empty PDF 🖨️":
    st.subheader("📄 Generate an Empty PDF")
    num_pages = st.number_input("Enter number of pages:", min_value=1, max_value=100000, value=1, step=1)
    if st.button("Generate PDF"):
        output_pdf = BytesIO()
        c = canvas.Canvas(output_pdf, pagesize=letter)
        for i in range(num_pages):
            c.drawString(100, 750, f"Page {i + 1}")
            c.showPage()
        c.save()
        output_pdf.seek(0)
        st.success(f"✅ Generated PDF with {num_pages} pages!")
        st.download_button("📥 Download Empty PDF", data=output_pdf, file_name="Empty_PDF.pdf", mime="application/pdf")
    st.stop()

# ✅ Start feature operations only if files uploaded
files = st.session_state.uploaded_files

if files:
    # Convert any file to PDF
    if operation == "Convert Any File to PDF ♻️":
        for file in files:
            ext = file.name.split('.')[-1].lower()
            output_pdf = BytesIO()
            if ext in ["png", "jpg", "jpeg"]:
                image = Image.open(file)
                image.convert("RGB").save(output_pdf, format="PDF")
            elif ext == "txt":
                c = canvas.Canvas(output_pdf, pagesize=letter)
                lines = file.getvalue().decode().split("\n")
                for line in lines:
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
                st.warning(f"❗ Unsupported file format: {ext}")
                continue
            output_pdf.seek(0)
            st.download_button(f"📥 Download {file.name.split('.')[0]}.pdf", data=output_pdf, file_name=f"{file.name.split('.')[0]}.pdf", mime="application/pdf")

    # Images to PDF
    elif operation == "Images to pdf 🏞️":
        images = [Image.open(f) for f in files if f.type.startswith("image/")]
        if images:
            if st.button("Convert to PDF"):
                output_pdf = BytesIO()
                images[0].save(output_pdf, save_all=True, append_images=[img.convert("RGB") for img in images[1:]], format="PDF")
                output_pdf.seek(0)
                st.download_button("📥 Download Images PDF", data=output_pdf, file_name="Images_to_PDF.pdf", mime="application/pdf")
        else:
            st.warning("❗ Upload image files only.")

    # Extract Pages
    elif operation == "Extract Pages from PDF 🪓":
        if files[0].type == "application/pdf":
            pdf = PdfReader(files[0])
            pages_input = st.text_input("Enter page numbers (comma-separated):")
            if st.button("Extract Pages"):
                if pages_input:
                    output_pdf = BytesIO()
                    pdf_writer = PdfWriter()
                    for p in pages_input.split(","):
                        page_num = int(p.strip()) - 1
                        if 0 <= page_num < len(pdf.pages):
                            pdf_writer.add_page(pdf.pages[page_num])
                    pdf_writer.write(output_pdf)
                    output_pdf.seek(0)
                    st.download_button("📥 Download Extracted PDF", data=output_pdf, file_name="Extracted.pdf", mime="application/pdf")
        else:
            st.warning("❗ Please upload a single PDF file.")

    # Merge PDFs
    elif operation == "Merge PDFs 📄+📃":
        if all(f.type == "application/pdf" for f in files):
            pdf_writer = PdfWriter()
            for f in files:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
            output_pdf = BytesIO()
            pdf_writer.write(output_pdf)
            output_pdf.seek(0)
            st.download_button("📥 Download Merged PDF", data=output_pdf, file_name="Merged_PDF.pdf", mime="application/pdf")
        else:
            st.warning("❗ Please upload only PDF files to merge.")

    # Split PDF (custom option or per-page zip)
    elif operation == "Split PDF (1 to 2 📑 PDFs) ➡ or ➡ Split each page as separate PDF":
        if files[0].type == "application/pdf":
            pdf = PdfReader(files[0])
            split_option = st.radio("Select Split Option:", ["Split by custom page count", "Split each page as separate PDF (ZIP)"])
            if split_option == "Split by custom page count":
                chunk_size = st.number_input("Enter chunk size (e.g., 50):", min_value=1, max_value=len(pdf.pages))
                if st.button("Split PDF"):
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                        for i in range(0, len(pdf.pages), chunk_size):
                            writer = PdfWriter()
                            for page in pdf.pages[i:i + chunk_size]:
                                writer.add_page(page)
                            temp_pdf = BytesIO()
                            writer.write(temp_pdf)
                            temp_pdf.seek(0)
                            zipf.writestr(f"part_{i // chunk_size + 1}.pdf", temp_pdf.read())
                    zip_buffer.seek(0)
                    st.download_button("📥 Download Split ZIP", data=zip_buffer, file_name="SplitPDFs.zip", mime="application/zip")

            elif split_option == "Split each page as separate PDF (ZIP)":
                if st.button("Split into Individual PDFs"):
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                        for i, page in enumerate(pdf.pages):
                            writer = PdfWriter()
                            writer.add_page(page)
                            page_pdf = BytesIO()
                            writer.write(page_pdf)
                            page_pdf.seek(0)
                            zipf.writestr(f"Page_{i + 1}.pdf", page_pdf.read())
                    zip_buffer.seek(0)
                    st.download_button("📥 Download Pages ZIP", data=zip_buffer, file_name="Each_Page_ZIP.zip", mime="application/zip")
        else:
            st.warning("❗ Please upload a single PDF file.")

    # Compress PDF
    elif operation == "Compress PDF 📉":
        if files[0].type == "application/pdf":
            doc = fitz.open(stream=files[0].getvalue(), filetype="pdf")
            output_pdf = BytesIO()
            new_pdf = fitz.open()
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_io = BytesIO()
                img.save(img_io, format="JPEG", quality=50)
                img_pdf = fitz.open(stream=img_io.getvalue(), filetype="pdf")
                new_pdf.insert_pdf(img_pdf)
            new_pdf.save(output_pdf)
            output_pdf.seek(0)
            st.download_button("📥 Download Compressed PDF", data=output_pdf, file_name="Compressed_PDF.pdf", mime="application/pdf")
        else:
            st.warning("❗ Please upload a PDF file.")

    # Insert page numbers
    elif operation == "Insert Page Numbers 📝 to PDF":
        if files[0].type == "application/pdf":
            pdf = PdfReader(files[0])
            writer = PdfWriter()
            for i, page in enumerate(pdf.pages):
                overlay_stream = BytesIO()
                c = canvas.Canvas(overlay_stream, pagesize=letter)
                c.drawString(500, 20, f"Page {i+1}")
                c.save()
                overlay_stream.seek(0)
                overlay_pdf = PdfReader(overlay_stream)
                page.merge_page(overlay_pdf.pages[0])
                writer.add_page(page)
            output_pdf = BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)
            st.download_button("📥 Download Numbered PDF", data=output_pdf, file_name="Numbered_PDF.pdf", mime="application/pdf")
        else:
            st.warning("❗ Please upload a PDF file.")

# ✅ Footer
st.markdown('<div class="footer">© Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satya Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | Techwing Trainees 🧡 </div>', unsafe_allow_html=True)

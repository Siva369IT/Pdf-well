import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz  # PyMuPDF for PDF compression

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# ✅ Load Custom CSS
def load_css():
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

if operation == "Clear All Uploaded Files ❌":
    st.session_state.clear()
    st.success("✅ All uploaded files cleared! Session reset.")
    st.stop()

file_formats = {
    "Convert Any File to PDF ♻️": "Upload files (png, jpg, jpeg, txt, docx, pptx):",
    "Images to pdf 🏞️": "Upload images (png, jpg, jpeg):",
    "Extract Pages from PDF 🪓": "Upload a PDF:",
    "Merge PDFs 📄+📃": "Upload PDFs to merge:",
    "Split PDF (1 to 2 📑 PDFs)": "Upload a PDF to split:",
    "Compress PDF 📉": "Upload a PDF to compress:",
    "Insert Page Numbers 📝 to PDF": "Upload a PDF to insert numbers:"
}

if operation in file_formats:
    st.markdown(f"### {file_formats[operation]}")
    file_types = {
        "Convert Any File to PDF ♻️": ["pdf", "png", "jpg", "jpeg", "txt", "docx", "pptx"],
        "Images to pdf 🏞️": ["png", "jpg", "jpeg"],
        "Extract Pages from PDF 🪓": ["pdf"],
        "Merge PDFs 📄+📃": ["pdf"],
        "Split PDF (1 to 2 📑 PDFs)": ["pdf"],
        "Compress PDF 📉": ["pdf"],
        "Insert Page Numbers 📝 to PDF": ["pdf"]
    }

    uploaded_files = st.file_uploader(
        "Upload file(s)", 
        type=file_types[operation], 
        accept_multiple_files=operation in ["Merge PDFs 📄+📃", "Convert Any File to PDF ♻️", "Images to pdf 🏞️"]
    )
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

files = st.session_state.uploaded_files

# ✅ Generate Empty PDF
if operation == "Generate Empty PDF 🖨️":
    st.subheader("📃 Create Empty PDF")
    total_pages = st.number_input("Number of pages:", min_value=1, max_value=100, value=1)
    if st.button("Generate Empty PDF"):
        output_pdf = BytesIO()
        c = canvas.Canvas(output_pdf, pagesize=letter)
        for i in range(1, total_pages + 1):
            c.drawString(300, 500, f"Page {i}")
            c.showPage()
        c.save()
        output_pdf.seek(0)
        st.success("✅ Generated Empty PDF!")
        st.download_button("📥 Download", data=output_pdf, file_name="Empty_PDF.pdf", mime="application/pdf")

# ✅ Convert Any File to PDF
if operation == "Convert Any File to PDF ♻️" and files:
    st.subheader("🔄 Convert Files to PDF")
    for uploaded_file in files:
        ext = uploaded_file.name.rsplit(".", 1)[1].lower()
        file_name = uploaded_file.name.rsplit(".", 1)[0]
        output_pdf = BytesIO()
        if ext in ["png", "jpg", "jpeg"]:
            img = Image.open(uploaded_file)
            img.convert("RGB").save(output_pdf, format="PDF")
        elif ext == "txt":
            pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
            for line in uploaded_file.getvalue().decode().split("\n"):
                pdf_canvas.drawString(100, 750, line)
                pdf_canvas.showPage()
            pdf_canvas.save()
        elif ext == "docx":
            doc = Document(uploaded_file)
            pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
            for para in doc.paragraphs:
                pdf_canvas.drawString(100, 750, para.text)
                pdf_canvas.showPage()
            pdf_canvas.save()
        elif ext == "pptx":
            ppt = Presentation(uploaded_file)
            pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
            for slide in ppt.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        pdf_canvas.drawString(100, 750, shape.text)
                        pdf_canvas.showPage()
            pdf_canvas.save()
        else:
            st.error(f"Unsupported file type: {ext}")
            continue
        output_pdf.seek(0)
        st.download_button(f"📥 Download {file_name}.pdf", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

# ✅ Extract Pages
if operation == "Extract Pages from PDF 🪓" and files:
    pdf_reader = PdfReader(BytesIO(files[0].getvalue()))
    pages = st.text_input("Enter pages (comma-separated):")
    if st.button("Extract"):
        if pages:
            pdf_writer = PdfWriter()
            for p in [int(x.strip()) - 1 for x in pages.split(",")]:
                if 0 <= p < len(pdf_reader.pages):
                    pdf_writer.add_page(pdf_reader.pages[p])
                else:
                    st.error(f"Invalid page {p+1}")
            output = BytesIO()
            pdf_writer.write(output)
            output.seek(0)
            st.download_button("📥 Download Extracted PDF", data=output, file_name="Extracted.pdf", mime="application/pdf")

# ✅ Merge PDFs
if operation == "Merge PDFs 📄+📃" and files:
    if len(files) >= 2:
        pdf_writer = PdfWriter()
        for f in files:
            reader = PdfReader(BytesIO(f.getvalue()))
            for page in reader.pages:
                pdf_writer.add_page(page)
        output = BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        st.download_button("📥 Download Merged PDF", data=output, file_name="Merged.pdf", mime="application/pdf")
    else:
        st.warning("Upload at least two PDFs!")

# ✅ Split PDF
if operation == "Split PDF (1 to 2 📑 PDFs)" and files:
    pdf_reader = PdfReader(BytesIO(files[0].getvalue()))
    if len(pdf_reader.pages) <= 1:
        st.warning("PDF has only one page.")
    else:
        split_point = st.number_input("Split after page:", min_value=1, max_value=len(pdf_reader.pages)-1)
        if st.button("Split PDF"):
            w1, w2 = PdfWriter(), PdfWriter()
            for i in range(split_point):
                w1.add_page(pdf_reader.pages[i])
            for i in range(split_point, len(pdf_reader.pages)):
                w2.add_page(pdf_reader.pages[i])
            b1, b2 = BytesIO(), BytesIO()
            w1.write(b1); w2.write(b2)
            b1.seek(0); b2.seek(0)
            st.download_button("📥 Download Part 1", data=b1, file_name="Split_Part1.pdf", mime="application/pdf")
            st.download_button("📥 Download Part 2", data=b2, file_name="Split_Part2.pdf", mime="application/pdf")

# ✅ Compress PDF
if operation == "Compress PDF 📉" and files:
    pdf_reader = fitz.open(stream=files[0].getvalue(), filetype="pdf")
    output = BytesIO()
    pdf_reader.save(output, garbage=4, deflate=True)
    output.seek(0)
    st.download_button("📥 Download Compressed PDF", data=output, file_name="Compressed.pdf", mime="application/pdf")

# ✅ Insert Page Numbers
if operation == "Insert Page Numbers 📝 to PDF" and files:
    pdf_reader = PdfReader(BytesIO(files[0].getvalue()))
    pdf_writer = PdfWriter()
    for i, page in enumerate(pdf_reader.pages):
        overlay = BytesIO()
        c = canvas.Canvas(overlay, pagesize=letter)
        c.drawString(500, 20, f"Page {i+1}")
        c.save()
        overlay.seek(0)
        overlay_reader = PdfReader(overlay)
        page.merge_page(overlay_reader.pages[0])
        pdf_writer.add_page(page)
    output = BytesIO()
    pdf_writer.write(output)
    output.seek(0)
    st.download_button("📥 Download Numbered PDF", data=output, file_name="Numbered.pdf", mime="application/pdf")

# ✅ Footer
st.markdown('<div class="footer">© Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satya Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | Techwing Trainees 🧡</div>', unsafe_allow_html=True)

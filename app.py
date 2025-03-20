import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz  # PyMuPDF for PDF compression
import os

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# ✅ Load Custom CSS
def load_css():
    with open("assets/Style.css", "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

load_css()

# ✅ Display Logo
st.image("logo1.png", width=150)
st.markdown('<p class="title">📄 PDF & File Converter</p>', unsafe_allow_html=True)

# ✅ Reset session state if not defined
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# ✅ Operation Selector
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

# ✅ Clear uploaded files
if operation == "Clear All Uploaded Files ❌":
    st.session_state.uploaded_files = []
    st.success("✅ All uploaded files cleared!")
    st.stop()

# ✅ Generate Empty PDF
if operation == "Generate Empty PDF 🖨️":
    st.subheader("📄 Generate an Empty PDF")
    num_pages = st.number_input("Enter number of pages:", min_value=1, max_value=1000, value=1, step=1)
    if st.button("Generate Empty PDF"):
        output_pdf = BytesIO()
        pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
        pdf_canvas.setFont("Helvetica", 12)
        for i in range(num_pages):
            pdf_canvas.drawString(100, 750, f"Page {i + 1}")
            pdf_canvas.showPage()
        pdf_canvas.save()
        output_pdf.seek(0)
        st.success(f"✅ Empty PDF with {num_pages} pages generated!")
        st.download_button("📥 Download Empty PDF", data=output_pdf, file_name="Empty_PDF.pdf", mime="application/pdf")
    st.stop()

# ✅ Dynamic upload label based on operation
upload_labels = {
    "Convert Any File to PDF ♻️": "Upload files to convert to PDF (png, jpg, jpeg, txt, docx, pptx):",
    "Images to pdf 🏞️": "Upload images to convert to PDF (png, jpg, jpeg):",
    "Extract Pages from PDF 🪓": "Upload a PDF to extract pages:",
    "Merge PDFs 📄+📃": "Upload multiple PDFs to merge:",
    "Split PDF (1 to 2 📑 PDFs)": "Upload a PDF to split into two:",
    "Compress PDF 📉": "Upload a PDF to compress:",
    "Insert Page Numbers 📝 to PDF": "Upload a PDF to insert page numbers:"
}

# ✅ Show uploader only if operation selected
if operation in upload_labels:
    uploaded_files = st.file_uploader(upload_labels[operation],
                                       type=["pdf", "png", "jpg", "jpeg", "txt", "docx", "pptx"],
                                       accept_multiple_files=True if operation == "Merge PDFs 📄+📃" or operation == "Convert Any File to PDF ♻️" or operation == "Images to pdf 🏞️" else False)
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

# ✅ OPERATIONS IMPLEMENTATION:
files = st.session_state.uploaded_files

# ✅ Convert Any File to PDF
if operation == "Convert Any File to PDF ♻️" and files:
    st.subheader("🔄 Convert Files to PDF")
    for uploaded_file in files:
        file_name = uploaded_file.name.rsplit(".", 1)[0]
        ext = uploaded_file.name.rsplit(".", 1)[1].lower()
        output_pdf = BytesIO()
        if ext in ["png", "jpg", "jpeg"]:
            img = Image.open(uploaded_file)
            img.convert("RGB").save(output_pdf, format="PDF")
        elif ext == "txt":
            pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
            lines = uploaded_file.read().decode().split("\n")
            for line in lines:
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

# ✅ Images to PDF
if operation == "Images to pdf 🏞️" and files:
    st.subheader("🏞️ Convert Images to Single PDF")
    image_files = [file for file in files if file.type.startswith("image/")]
    if image_files:
        if st.button("Convert Images"):
            images = [Image.open(img).convert("RGB") for img in image_files]
            output_pdf = BytesIO()
            images[0].save(output_pdf, save_all=True, append_images=images[1:], format="PDF")
            output_pdf.seek(0)
            st.success("✅ Images converted successfully!")
            st.download_button("📥 Download PDF", data=output_pdf, file_name="Images_Converted.pdf", mime="application/pdf")
    else:
        st.warning("⚠️ Please upload image files.")

# ✅ Extract Pages from PDF
if operation == "Extract Pages from PDF 🪓" and files:
    pdf_reader = PdfReader(files[0])
    pages = st.text_input("Enter page numbers (comma-separated):")
    if st.button("Extract"):
        if pages:
            pdf_writer = PdfWriter()
            page_list = [int(p.strip()) - 1 for p in pages.split(",")]
            for p in page_list:
                if 0 <= p < len(pdf_reader.pages):
                    pdf_writer.add_page(pdf_reader.pages[p])
                else:
                    st.error(f"Invalid page number: {p + 1}")
            output_pdf = BytesIO()
            pdf_writer.write(output_pdf)
            output_pdf.seek(0)
            st.download_button("📥 Download Extracted PDF", data=output_pdf, file_name="Extracted_Pages.pdf", mime="application/pdf")

# ✅ Merge PDFs
if operation == "Merge PDFs 📄+📃" and files:
    if len(files) < 2:
        st.warning("⚠️ Please upload at least two PDFs to merge.")
    else:
        pdf_writer = PdfWriter()
        for file in files:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        output_pdf = BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)
        st.download_button("📥 Download Merged PDF", data=output_pdf, file_name="Merged_PDF.pdf", mime="application/pdf")

# ✅ Split PDF
if operation == "Split PDF (1 to 2 📑 PDFs)" and files:
    pdf_reader = PdfReader(files[0])
    if len(pdf_reader.pages) <= 1:
        st.warning("⚠️ PDF has only one page, cannot split.")
    else:
        split_point = st.number_input("Enter split page:", min_value=1, max_value=len(pdf_reader.pages)-1)
        if st.button("Split PDF"):
            part1_writer, part2_writer = PdfWriter(), PdfWriter()
            for i in range(split_point):
                part1_writer.add_page(pdf_reader.pages[i])
            for i in range(split_point, len(pdf_reader.pages)):
                part2_writer.add_page(pdf_reader.pages[i])
            part1_io, part2_io = BytesIO(), BytesIO()
            part1_writer.write(part1_io)
            part2_writer.write(part2_io)
            part1_io.seek(0)
            part2_io.seek(0)
            st.download_button("📥 Download Part 1", data=part1_io, file_name="Split_Part1.pdf", mime="application/pdf")
            st.download_button("📥 Download Part 2", data=part2_io, file_name="Split_Part2.pdf", mime="application/pdf")

# ✅ Compress PDF
if operation == "Compress PDF 📉" and files:
    pdf_reader = fitz.open(stream=files[0].getvalue(), filetype="pdf")
    output_pdf = BytesIO()
    pdf_reader.save(output_pdf, garbage=4, deflate=True)
    output_pdf.seek(0)
    st.download_button("📥 Download Compressed PDF", data=output_pdf, file_name="Compressed_PDF.pdf", mime="application/pdf")

# ✅ Insert Page Numbers
if operation == "Insert Page Numbers 📝 to PDF" and files:
    pdf_reader = PdfReader(files[0])
    pdf_writer = PdfWriter()
    for i, page in enumerate(pdf_reader.pages):
        overlay = BytesIO()
        c = canvas.Canvas(overlay, pagesize=letter)
        c.drawString(500, 20, f"Page {i + 1}")
        c.save()
        overlay.seek(0)
        overlay_reader = PdfReader(overlay)
        page.merge_page(overlay_reader.pages[0])
        pdf_writer.add_page(page)
    output_pdf = BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)
    st.download_button("📥 Download Numbered PDF", data=output_pdf, file_name="Numbered_PDF.pdf", mime="application/pdf")

# ✅ Footer
st.markdown('<div class="footer">© Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satya Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | Techwing Trainees 🧡</div>', unsafe_allow_html=True)

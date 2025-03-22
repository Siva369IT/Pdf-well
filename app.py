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

# --- Select Operation ---
operation = st.selectbox("Select an operation:", [
    "Generate Empty PDF 🖨️",
    "Convert Any File to PDF ♻️",
    "Images to pdf 🏞️",
    "Extract Pages from PDF 🪓",
    "Merge PDFs 📄+📃",
    "Split PDF (1 to 2 📑 PDFs)",
    "Compress PDF 📉",
    "Insert Page Numbers 📝 to PDF"
])

# ✅ Add "Clear Uploaded Files" Button
if "uploaded_files" in st.session_state:
    if st.button("Remove Uploaded Files"):
        # Clear the uploaded files
        st.session_state.uploaded_files = []
        st.success("✅ Uploaded files have been removed! Please choose a new operation to proceed.")
        st.stop()  # Stop further execution and let users select a new operation
# ✅ Generate Empty PDF
if operation == "Generate Empty PDF 🖨️":
    st.subheader("📄 Generate an Empty PDF")
    num_pages = st.number_input("Enter number of pages:", min_value=1, max_value=100000, value=1, step=1)

    if st.button("Generate an Empty PDF"):
        output_pdf = BytesIO()
        pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
        pdf_canvas.setFont("Helvetica", 12)

        for i in range(num_pages):
            pdf_canvas.drawString(100, 750, f"Page {i+1}")
            pdf_canvas.showPage()

        pdf_canvas.save()
        output_pdf.seek(0)

        st.success(f"✅ Empty PDF with {num_pages} pages generated!")
        st.download_button("📥 Download Empty PDF", data=output_pdf, file_name="Empty_PDF.pdf", mime="application/pdf")

    st.stop()

# ✅ File Upload
uploaded_files = st.file_uploader("Upload file(s)", type=["pdf", "png", "jpg", "jpeg", "docx", "pptx", "txt"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded!")

    # ✅ Convert Any File to PDF
    if operation == "Convert Any File to PDF ♻️":
        st.subheader("🔄 Convert Any File to PDF")
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name.split(".")[0]
            file_extension = uploaded_file.name.split(".")[-1].lower()
            output_pdf = BytesIO()

            if file_extension in ["png", "jpg", "jpeg"]:
                image = Image.open(uploaded_file)
                image.convert("RGB").save(output_pdf, format="PDF")
            elif file_extension == "txt":
                pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
                for line in uploaded_file.getvalue().decode().split("\n"):
                    pdf_canvas.drawString(100, 750, line)
                    pdf_canvas.showPage()
                pdf_canvas.save()
            elif file_extension == "docx":
                doc = Document(uploaded_file)
                pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
                for para in doc.paragraphs:
                    pdf_canvas.drawString(100, 750, para.text)
                    pdf_canvas.showPage()
                pdf_canvas.save()
            elif file_extension == "pptx":
                ppt = Presentation(uploaded_file)
                pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
                for slide in ppt.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            pdf_canvas.drawString(100, 750, shape.text)
                            pdf_canvas.showPage()
                pdf_canvas.save()
            else:
                st.error(f"❌ Unsupported file format: {file_extension}")
                continue

            output_pdf.seek(0)
            st.download_button(f"📥 Download {file_name}.pdf", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")
            
    # ✅ Extract Pages from PDF
    elif operation == "Extract Pages from PDF 🪓":
        pdf_reader = PdfReader(uploaded_files[0])
        pages_to_extract = st.text_input("Enter page numbers (comma-separated):")
        if st.button("Extract"):
            if pages_to_extract:
                selected_pages = [int(p.strip()) - 1 for p in pages_to_extract.split(",")]
                pdf_writer = PdfWriter()
                for p in selected_pages:
                    if 0 <= p < len(pdf_reader.pages):
                        pdf_writer.add_page(pdf_reader.pages[p])
                    else:
                        st.error(f"Invalid page number: {p+1}")
                output_pdf = BytesIO()
                pdf_writer.write(output_pdf)
                output_pdf.seek(0)
                st.download_button("📄 Download Extracted PDF", data=output_pdf, file_name="Extracted_Pages.pdf", mime="application/pdf")
                
    # ✅ Merge PDFs
    elif operation == "Merge PDFs 📄+📃":
        pdf_writer = PdfWriter()
        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        output_pdf = BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)
        st.download_button("📥 Download Merged PDF", data=output_pdf, file_name="Merged_PDF.pdf", mime="application/pdf")

    # ✅ Split PDF
    elif operation == "Split PDF (1 to 2 📑 PDFs)":
        pdf_reader = PdfReader(uploaded_files[0])
        split_page = st.number_input("Enter the split page number:", min_value=1, max_value=len(pdf_reader.pages) - 1)
        if st.button("Split PDF"):
            part1_writer, part2_writer = PdfWriter(), PdfWriter()
            for i in range(split_page):
                part1_writer.add_page(pdf_reader.pages[i])
            for i in range(split_page, len(pdf_reader.pages)):
                part2_writer.add_page(pdf_reader.pages[i])
            output1, output2 = BytesIO(), BytesIO()
            part1_writer.write(output1)
            part2_writer.write(output2)
            output1.seek(0)
            output2.seek(0)
            st.download_button("📄 Download First Part", data=output1, file_name="Split_Part1.pdf", mime="application/pdf")
            st.download_button("📄 Download Second Part", data=output2, file_name="Split_Part2.pdf", mime="application/pdf")

    # ✅ Compress PDF
    elif operation == "Compress PDF 📉":
        pdf_reader = fitz.open(stream=uploaded_files[0].getvalue(), filetype="pdf")
        output_pdf = BytesIO()
        pdf_writer = fitz.open()
        for page in pdf_reader:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(output_pdf, format="PDF")
        output_pdf.seek(0)
        st.download_button("📥 Download Compressed PDF", data=output_pdf, file_name="Compressed_PDF.pdf", mime="application/pdf")

    # ✅ Insert Page Numbers
    elif operation == "Insert Page Numbers 📝 to PDF":
        pdf_reader = PdfReader(uploaded_files[0])
        pdf_writer = PdfWriter()
        output_pdf = BytesIO()

        for i, page in enumerate(pdf_reader.pages):
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(500, 20, f"Page {i + 1}")
            c.save()
            packet.seek(0)
            overlay_reader = PdfReader(packet)
            page.merge_page(overlay_reader.pages[0])
            pdf_writer.add_page(page)

        pdf_writer.write(output_pdf)
        output_pdf.seek(0)
        st.download_button("📄 Download Numbered PDF", data=output_pdf, file_name="Numbered_PDF.pdf", mime="application/pdf")

    # ✅ Images to PDF (Multiple images to single PDF)
    elif operation == "Images to pdf 🏞️":
        st.subheader("🏞️ Convert Multiple Images to Single PDF")
        image_files = [file for file in uploaded_files if file.type.startswith("image/")]

        if image_files:
            if st.button("Convert Images to PDF"):
                pdf_images = []
                for img_file in image_files:
                    image = Image.open(img_file)
                    img_converted = image.convert("RGB")
                    pdf_images.append(img_converted)
            
                output_pdf = BytesIO()
                pdf_images[0].save(output_pdf, save_all=True, append_images=pdf_images[1:], format="PDF")
                output_pdf.seek(0)

                st.success("✅ Images successfully converted to a single PDF!")
                st.download_button("📥 Download Images PDF", data=output_pdf, file_name="Images_to_PDF.pdf", mime="application/pdf")
        else:
            st.warning("⚠️ Please upload image files (PNG, JPG, JPEG) to convert.")
    
# ✅ Footer
st.markdown('<div class="footer">© Pavan sri sai mondem |Siva satyamsetti |Uma satya mounika sapireddy |Bhuvaneswari Devi Seru | Chandu meela | Techwing Trainees 🧡 </div>', unsafe_allow_html=True)

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io
from fpdf import FPDF
from docx import Document
from pptx import Presentation
import fitz  # PyMuPDF
import zipfile

st.set_page_config(page_title="PDF & File Converter", layout="centered")
st.markdown("<h1 style='text-align: center;'>PDF & File Converter (All-in-One)</h1>", unsafe_allow_html=True)
st.write("")

operation = st.selectbox("**Select Operation**", [
    "Generate Empty PDF",
    "Convert Any File to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF",
    "Compress PDF",
    "Insert Page Numbers into PDF",
    "Images to PDF"
])

uploaded_files = st.file_uploader("Upload files below:", accept_multiple_files=True)

# 1. Generate Empty PDF
if operation == "Generate Empty PDF":
    max_pages = st.number_input("Enter number of pages (max 10000)", min_value=1, max_value=10000, value=1)
    if st.button("Generate PDF"):
        pdf = FPDF()
        for i in range(1, max_pages + 1):
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Page {i}", ln=1, align="C")
        output_buf = io.BytesIO(pdf.output(dest="S").encode("latin1"))
        st.download_button("Download Empty PDF", data=output_buf, file_name="Empty.pdf", mime="application/pdf")

# 2. Convert Any File to PDF (direct download)
if operation == "Convert Any File to PDF" and uploaded_files:
    for file in uploaded_files:
        if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file)
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            for para in doc.paragraphs:
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, para.text)
            output_buf = io.BytesIO(pdf.output(dest="S").encode("latin1"))
            st.download_button(f"Download {file.name[:-5]}.pdf", data=output_buf, file_name=f"{file.name[:-5]}.pdf", mime="application/pdf")

        elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            prs = Presentation(file)
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            for slide in prs.slides:
                text = "\n".join([shape.text for shape in slide.shapes if hasattr(shape, "text")])
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, text)
            output_buf = io.BytesIO(pdf.output(dest="S").encode("latin1"))
            st.download_button(f"Download {file.name[:-5]}.pdf", data=output_buf, file_name=f"{file.name[:-5]}.pdf", mime="application/pdf")

        elif file.type.startswith("text/"):
            content = file.read().decode()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, content)
            output_buf = io.BytesIO(pdf.output(dest="S").encode("latin1"))
            st.download_button(f"Download {file.name[:-4]}.pdf", data=output_buf, file_name=f"{file.name[:-4]}.pdf", mime="application/pdf")

        elif file.type.startswith("image/"):
            image = Image.open(file)
            pdf = FPDF(unit="pt", format=[image.width, image.height])
            pdf.add_page()
            img_buf = io.BytesIO()
            image.save(img_buf, format="PNG")
            img_buf.seek(0)
            pdf.image(img_buf, 0, 0)
            output_buf = io.BytesIO(pdf.output(dest="S").encode("latin1"))
            st.download_button(f"Download {file.name}.pdf", data=output_buf, file_name=f"{file.name}.pdf", mime="application/pdf")
        else:
            st.error(f"Unsupported file: {file.name}")

# 3. Extract Pages from PDF
if operation == "Extract Pages from PDF" and uploaded_files:
    start_page = st.number_input("Start Page", min_value=1, step=1)
    end_page = st.number_input("End Page", min_value=1, step=1)
    if st.button("Extract"):
        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            pdf_writer = PdfWriter()
            for page in range(int(start_page)-1, int(end_page)):
                pdf_writer.add_page(pdf_reader.pages[page])
            output_buf = io.BytesIO()
            pdf_writer.write(output_buf)
            output_buf.seek(0)
            st.download_button("Download Extracted PDF", data=output_buf, file_name="extracted.pdf", mime="application/pdf")

# 4. Merge PDFs
if operation == "Merge PDFs" and uploaded_files:
    if st.button("Merge PDFs"):
        pdf_writer = PdfWriter()
        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        output_buf = io.BytesIO()
        pdf_writer.write(output_buf)
        output_buf.seek(0)
        st.download_button("Download Merged PDF", data=output_buf, file_name="merged.pdf", mime="application/pdf")

# 5. Split PDF
if operation == "Split PDF" and uploaded_files:
    if st.button("Split PDF into Single Pages (ZIP)"):
        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, mode="w") as zf:
                for i, page in enumerate(pdf_reader.pages):
                    pdf_writer = PdfWriter()
                    pdf_writer.add_page(page)
                    page_buf = io.BytesIO()
                    pdf_writer.write(page_buf)
                    zf.writestr(f"page_{i+1}.pdf", page_buf.getvalue())
            zip_buf.seek(0)
            st.download_button("Download ZIP of split pages", data=zip_buf, file_name="split_pages.zip", mime="application/zip")

# 6. Compress PDF
if operation == "Compress PDF" and uploaded_files:
    if st.button("Compress PDF"):
        for file in uploaded_files:
            pdf_reader = fitz.open(stream=file.read(), filetype="pdf")
            pdf_writer = fitz.open()
            for page in pdf_reader:
                pdf_writer.insert_pdf(pdf_reader, from_page=page.number, to_page=page.number)
            output_buf = io.BytesIO()
            pdf_writer.save(output_buf)
            output_buf.seek(0)
            st.download_button("Download Compressed PDF", data=output_buf, file_name="compressed.pdf", mime="application/pdf")

# 7. Insert Page Numbers
if operation == "Insert Page Numbers into PDF" and uploaded_files:
    if st.button("Insert Page Numbers"):
        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            pdf = FPDF()
            for i, page in enumerate(pdf_reader.pages, start=1):
                pdf.add_page()
                text = page.extract_text()
                pdf.set_font("Arial", size=12)
                if text:
                    pdf.multi_cell(0, 10, text)
                pdf.set_y(-30)
                pdf.cell(0, 10, f"Page {i}", align="C")
            output_buf = io.BytesIO(pdf.output(dest="S").encode("latin1"))
            st.download_button("Download PDF with Page Numbers", data=output_buf, file_name="page_numbered.pdf", mime="application/pdf")

# 8. Images to PDF
if operation == "Images to PDF" and uploaded_files:
    if st.button("Convert Images to PDF"):
        pdf = FPDF()
        for img_file in uploaded_files:
            image = Image.open(img_file)
            width, height = image.size
            pdf.add_page(format=(width, height))
            img_buf = io.BytesIO()
            image.save(img_buf, format="PNG")
            img_buf.seek(0)
            pdf.image(img_buf, 0, 0, width, height)
        output_buf = io.BytesIO(pdf.output(dest="S").encode("latin1"))
        st.download_button("Download PDF", data=output_buf, file_name="images_to_pdf.pdf", mime="application/pdf")

# Add Footer
st.markdown("""
<hr>
<div style='text-align: center; font-size: small;'>
<b>App Owners:</b><br>
Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela
</div>
""", unsafe_allow_html=True)

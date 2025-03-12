import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from reportlab.pdfgen import canvas

st.set_page_config(page_title="PDF & File Converter", layout="wide")
import streamlit as st

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/Style.css")
st.title("📄 PDF, Image & Word Converter Tool")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx", "pptx"])

if uploaded_file:
    file_bytes = BytesIO(uploaded_file.getbuffer())
    st.success(f"Uploaded {uploaded_file.name} successfully!")

    # Convert File to PDF
    if uploaded_file.type.startswith("image") or uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.ms-powerpoint"]:
        output_pdf = BytesIO()
        if uploaded_file.type.startswith("image"):
            image = Image.open(file_bytes)
            image.save(output_pdf, "PDF", resolution=100.0)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file_bytes)
            pdf_canvas = canvas.Canvas(output_pdf)
            pdf_canvas.setFont("Helvetica", 12)
            y_position = 750
            for para in doc.paragraphs:
                pdf_canvas.drawString(50, y_position, para.text)
                y_position -= 20
            pdf_canvas.save()
        output_pdf.seek(0)
        file_name = st.text_input("Enter output file name:", value="Converted_File")
        st.download_button("Download PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # Extract Pages from PDF
    elif uploaded_file.type == "application/pdf":
        reader = PdfReader(file_bytes)
        total_pages = len(reader.pages)
        st.write(f"Total pages: {total_pages}")
        pages_to_extract = st.multiselect("Select pages to extract:", list(range(1, total_pages + 1)))

        if st.button("Extract Pages"):
            writer = PdfWriter()
            for page_num in pages_to_extract:
                writer.add_page(reader.pages[page_num - 1])
            output_pdf = BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)
            file_name = st.text_input("Enter output file name:", value="Extracted_Pages")
            st.download_button("Download Extracted PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # Merge PDFs
    if st.button("Merge PDFs"):
        uploaded_files = st.file_uploader("Upload PDFs to merge", accept_multiple_files=True, type=["pdf"])
        if uploaded_files:
            writer = PdfWriter()
            for file in uploaded_files:
                reader = PdfReader(BytesIO(file.getbuffer()))
                for page in reader.pages:
                    writer.add_page(page)
            output_pdf = BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)
            file_name = st.text_input("Enter output file name:", value="Merged_File")
            st.download_button("Download Merged PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # Split PDF
    if st.button("Split PDF"):
        split_pages = st.text_input("Enter page numbers to split (comma-separated):")
        if split_pages:
            split_pages = [int(x.strip()) for x in split_pages.split(",")]
            writer = PdfWriter()
            for page_num in split_pages:
                writer.add_page(reader.pages[page_num - 1])
            output_pdf = BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)
            file_name = st.text_input("Enter output file name:", value="Split_File")
            st.download_button("Download Split PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # Generate Empty PDF
    if st.button("Generate Empty PDF"):
        num_pages = st.number_input("Enter number of pages:", min_value=1, step=1)
        output_pdf = BytesIO()
        pdf_canvas = canvas.Canvas(output_pdf)
        for i in range(num_pages):
            pdf_canvas.drawString(100, 750, f"Page {i+1}")
            pdf_canvas.showPage()
        pdf_canvas.save()
        output_pdf.seek(0)
        file_name = st.text_input("Enter output file name:", value="Empty_PDF")
        st.download_button("Download Empty PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from docx import Document
from pptx import Presentation
import os
import io

# Set page config
st.set_page_config(page_title="PDF, Image & Word Converter Tool", page_icon="📄", layout="wide")

# Load custom CSS
with open("assets/style.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Title with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("logo1.png", width=100)
with col2:
    st.title("PDF, Image & Word Converter Tool")

# Sidebar for operations
st.sidebar.header("Select an operation:")
operation = st.sidebar.selectbox("Choose:", ["Generate Empty PDF", "Convert to PDF", "Merge PDFs", "Split PDFs", "Extract Pages"])

# Function to create an empty PDF
def create_empty_pdf(pages):
    output = PdfWriter()
    for _ in range(pages):
        output.add_blank_page(width=612, height=792)  # Standard A4 size
    return output

# Function to convert files to PDF
def convert_to_pdf(uploaded_file):
    file_extension = uploaded_file.name.split(".")[-1].lower()
    pdf_writer = PdfWriter()
    pdf_buffer = io.BytesIO()

    if file_extension == "docx":
        doc = Document(uploaded_file)
        pdf_writer.add_blank_page()
        pdf_writer.write(pdf_buffer)
    elif file_extension in ["ppt", "pptx"]:
        prs = Presentation(uploaded_file)
        pdf_writer.add_blank_page()
        pdf_writer.write(pdf_buffer)
    else:
        st.error("Unsupported file format!")
        return None

    return pdf_buffer.getvalue()

# Operation: Generate Empty PDF
if operation == "Generate Empty PDF":
    st.subheader("📝 Create an Empty PDF")
    pages = st.number_input("Enter number of pages:", min_value=1, value=1, step=1)
    if st.button("Generate Empty PDF"):
        pdf_output = create_empty_pdf(pages)
        output_buffer = io.BytesIO()
        pdf_output.write(output_buffer)
        st.download_button("Download PDF", output_buffer.getvalue(), file_name="empty.pdf", mime="application/pdf")

# Operation: Convert to PDF
elif operation == "Convert to PDF":
    st.subheader("📂 Convert Any File to PDF")
    uploaded_file = st.file_uploader("Upload a file", type=["docx", "ppt", "pptx"])
    if uploaded_file:
        pdf_data = convert_to_pdf(uploaded_file)
        if pdf_data:
            st.download_button("Download PDF", pdf_data, file_name="converted.pdf", mime="application/pdf")

# Operation: Merge PDFs
elif operation == "Merge PDFs":
    st.subheader("📑 Merge Multiple PDFs")
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        merger = PdfMerger()
        for pdf in uploaded_files:
            merger.append(PdfReader(pdf))
        output_buffer = io.BytesIO()
        merger.write(output_buffer)
        st.download_button("Download Merged PDF", output_buffer.getvalue(), file_name="merged.pdf", mime="application/pdf")

# Operation: Split PDFs
elif operation == "Split PDFs":
    st.subheader("✂ Split a PDF")
    uploaded_pdf = st.file_uploader("Upload a PDF to split", type="pdf")
    if uploaded_pdf:
        pdf_reader = PdfReader(uploaded_pdf)
        total_pages = len(pdf_reader.pages)
        start, end = st.slider("Select page range", 1, total_pages, (1, total_pages))
        if st.button("Split PDF"):
            pdf_writer = PdfWriter()
            for i in range(start - 1, end):
                pdf_writer.add_page(pdf_reader.pages[i])
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            st.download_button("Download Split PDF", output_buffer.getvalue(), file_name="split.pdf", mime="application/pdf")

# Operation: Extract Pages
elif operation == "Extract Pages":
    st.subheader("🔍 Extract Specific Pages from PDF")
    uploaded_pdf = st.file_uploader("Upload a PDF to extract pages", type="pdf")
    if uploaded_pdf:
        pdf_reader = PdfReader(uploaded_pdf)
        total_pages = len(pdf_reader.pages)
        pages = st.text_input(f"Enter pages (1-{total_pages}, comma-separated):")
        if st.button("Extract Pages"):
            selected_pages = [int(p) - 1 for p in pages.split(",") if p.isdigit() and 1 <= int(p) <= total_pages]
            if selected_pages:
                pdf_writer = PdfWriter()
                for page in selected_pages:
                    pdf_writer.add_page(pdf_reader.pages[page])
                output_buffer = io.BytesIO()
                pdf_writer.write(output_buffer)
                st.download_button("Download Extracted PDF", output_buffer.getvalue(), file_name="extracted.pdf", mime="application/pdf")
            else:
                st.error("Invalid page selection!")

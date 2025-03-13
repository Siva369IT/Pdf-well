import streamlit as st
import os
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas
from PIL import Image

# Set page config
st.set_page_config(page_title="PDF Well", page_icon="💚", layout="wide")

# Load custom CSS
with open("assets/Style.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Title
st.title("PDF Well - All-in-One PDF Toolkit")

# Sidebar
st.sidebar.header("Choose an Action")
option = st.sidebar.selectbox("Select an option:", ["Convert to PDF", "Extract Pages", "Merge PDFs", "Split PDF", "Create Empty PDF"])

# File uploader
uploaded_files = st.file_uploader("Upload your file(s)", accept_multiple_files=True)

# Process the selected option
if option == "Convert to PDF":
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            if file_extension in ["png", "jpg", "jpeg"]:
                image = Image.open(uploaded_file)
                pdf_path = f"{uploaded_file.name}.pdf"
                image.convert("RGB").save(pdf_path)
                st.download_button("Download PDF", data=open(pdf_path, "rb"), file_name=pdf_path, mime="application/pdf")

            elif file_extension in ["docx", "doc"]:
                doc = Document(uploaded_file)
                pdf_path = f"{uploaded_file.name}.pdf"
                pdf = canvas.Canvas(pdf_path)
                for para in doc.paragraphs:
                    pdf.drawString(100, 800, para.text)
                pdf.save()
                st.download_button("Download PDF", data=open(pdf_path, "rb"), file_name=pdf_path, mime="application/pdf")

            elif file_extension in ["pptx", "ppt"]:
                ppt = Presentation(uploaded_file)
                pdf_path = f"{uploaded_file.name}.pdf"
                pdf = canvas.Canvas(pdf_path)
                for slide in ppt.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            pdf.drawString(100, 800, shape.text)
                pdf.save()
                st.download_button("Download PDF", data=open(pdf_path, "rb"), file_name=pdf_path, mime="application/pdf")

            else:
                st.error("Unsupported file format.")

elif option == "Extract Pages":
    if uploaded_files:
        for uploaded_file in uploaded_files:
            pdf_reader = PdfReader(uploaded_file)
            pages = st.text_input("Enter page numbers to extract (comma-separated, e.g., 1,3,5)").split(",")
            if st.button("Extract"):
                pdf_writer = PdfWriter()
                for page_num in pages:
                    try:
                        pdf_writer.add_page(pdf_reader.pages[int(page_num) - 1])
                    except IndexError:
                        st.error(f"Page {page_num} does not exist.")
                output_path = "extracted_pages.pdf"
                with open(output_path, "wb") as out_file:
                    pdf_writer.write(out_file)
                st.download_button("Download Extracted PDF", data=open(output_path, "rb"), file_name="extracted_pages.pdf", mime="application/pdf")

elif option == "Merge PDFs":
    if len(uploaded_files) > 1:
        pdf_writer = PdfWriter()
        for uploaded_file in uploaded_files:
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
        output_path = "merged.pdf"
        with open(output_path, "wb") as out_file:
            pdf_writer.write(out_file)
        st.download_button("Download Merged PDF", data=open(output_path, "rb"), file_name="merged.pdf", mime="application/pdf")

elif option == "Split PDF":
    if uploaded_files:
        for uploaded_file in uploaded_files:
            pdf_reader = PdfReader(uploaded_file)
            for i, page in enumerate(pdf_reader.pages):
                pdf_writer = PdfWriter()
                pdf_writer.add_page(page)
                output_path = f"split_page_{i+1}.pdf"
                with open(output_path, "wb") as out_file:
                    pdf_writer.write(out_file)
                st.download_button(f"Download Page {i+1}", data=open(output_path, "rb"), file_name=output_path, mime="application/pdf")

elif option == "Create Empty PDF":
    output_path = "empty.pdf"
    pdf = canvas.Canvas(output_path)
    for i in range(1, 6):  # 5 blank pages
        pdf.showPage()
    pdf.save()
    st.download_button("Download Empty PDF", data=open(output_path, "rb"), file_name="empty.pdf", mime="application/pdf")

# Copyright
st.markdown("<small>© Pavan Sri Sai Mondem, Siva Satyamsetti, Uma Satyam Mounika Sapireddy, Bhuvaneswari Devi Seru, Chandu Meela</small>", unsafe_allow_html=True)

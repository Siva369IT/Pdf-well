import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
import zipfile
import os
from io import BytesIO
from PIL import Image
from docx2pdf import convert as convert_docx
import pptx
import tempfile
import shutil

st.set_page_config(page_title="PDF & File Converter 💚", layout="centered")

st.markdown("<h1 style='text-align: center; color: green;'>PDF & File Converter 💚</h1>", unsafe_allow_html=True)

file_formats = {
    "Generate Empty PDF 📄": [],
    "Convert Any File to PDF 🔄": ["txt", "docx", "pptx", "png", "jpg", "jpeg"],
    "Extract Pages from PDF 🪓": ["pdf"],
    "Merge PDFs 📚": ["pdf"],
    "Split PDF ✂️": ["pdf"],
    "Compress PDF 📉": ["pdf"],
    "Insert Page Numbers 📝 to PDF": ["pdf"],
    "Images to PDF 🖼️": ["png", "jpg", "jpeg"]
}

if 'last_operation' not in st.session_state:
    st.session_state.last_operation = ""
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

def clear_uploaded_files():
    st.session_state.uploaded_files = []

operation = st.selectbox("Select Operation:", list(file_formats.keys()))
if operation != st.session_state.last_operation:
    clear_uploaded_files()
    st.session_state.last_operation = operation

if file_formats[operation]:
    st.info(f"Upload only: {', '.join(file_formats[operation])} files")

if operation == "Generate Empty PDF 📄":
    pages = st.number_input("Number of pages:", min_value=1, max_value=1369, value=1)
    if st.button("Generate PDF"):
        pdf = FPDF()
        for i in range(pages):
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Page {i+1}", ln=True, align="C")
        output = BytesIO()
        pdf.output(output)
        output.seek(0)
        st.download_button("Download Empty PDF", data=output, file_name="empty.pdf")

else:
    files = st.file_uploader("Upload files:", type=file_formats[operation], accept_multiple_files=True)
    if files:
        st.session_state.uploaded_files = files

def save_temp_files(uploaded_files):
    temp_dir = tempfile.mkdtemp()
    saved_files = []
    for file in uploaded_files:
        path = os.path.join(temp_dir, file.name)
        with open(path, "wb") as f:
            f.write(file.getvalue())
        saved_files.append(path)
    return saved_files, temp_dir

# Convert Any File to PDF
if operation == "Convert Any File to PDF 🔄" and st.session_state.uploaded_files:
    if st.button("Convert"):
        try:
            files, temp_dir = save_temp_files(st.session_state.uploaded_files)
            pdf_files = []
            for file_path in files:
                ext = file_path.split(".")[-1].lower()
                if ext == "txt":
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    with open(file_path, "r") as f:
                        for line in f:
                            pdf.multi_cell(0, 10, line)
                    output_path = file_path.replace(ext, "pdf")
                    pdf.output(output_path)
                    pdf_files.append(output_path)
                elif ext == "docx":
                    output_path = file_path.replace(ext, "pdf")
                    convert_docx(file_path, output_path)
                    pdf_files.append(output_path)
                elif ext == "pptx":
                    prs = pptx.Presentation(file_path)
                    pdf = FPDF()
                    for slide in prs.slides:
                        pdf.add_page()
                        text = ""
                        for shape in slide.shapes:
                            if hasattr(shape, "text"):
                                text += shape.text + "\n"
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, text)
                    output_path = file_path.replace(ext, "pdf")
                    pdf.output(output_path)
                    pdf_files.append(output_path)
                elif ext in ["png", "jpg", "jpeg"]:
                    pdf = FPDF()
                    pdf.add_page()
                    img = Image.open(file_path)
                    img_path = os.path.join(temp_dir, "temp_img.jpg")
                    img.save(img_path)
                    pdf.image(img_path, x=10, y=10, w=180)
                    output_path = file_path.replace(ext, "pdf")
                    pdf.output(output_path)
                    pdf_files.append(output_path)
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zipf:
                for pdf_file in pdf_files:
                    zipf.write(pdf_file, arcname=os.path.basename(pdf_file))
            zip_buf.seek(0)
            st.download_button("Download All PDFs (ZIP)", zip_buf, "converted_files.zip")
            shutil.rmtree(temp_dir)
        except:
            st.error("Error while converting. Please check files.")

# Extract Pages
if operation == "Extract Pages from PDF 🪓" and st.session_state.uploaded_files:
    page_range = st.text_input("Enter pages (e.g., 1,3,5-8):")
    if st.button("Extract"):
        try:
            for file in st.session_state.uploaded_files:
                reader = PdfReader(file)
                writer = PdfWriter()
                pages = []
                parts = page_range.split(",")
                for part in parts:
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        pages.extend(range(start, end+1))
                    else:
                        pages.append(int(part))
                pages = [p - 1 for p in pages]
                for p in pages:
                    writer.add_page(reader.pages[p])
                output = BytesIO()
                writer.write(output)
                output.seek(0)
                st.download_button("Download Extracted PDF", output, file_name="extracted.pdf")
        except:
            st.error("Error during extraction.")

# Merge PDFs
if operation == "Merge PDFs 📚" and st.session_state.uploaded_files:
    if st.button("Merge PDFs"):
        try:
            writer = PdfWriter()
            for file in st.session_state.uploaded_files:
                writer.append(PdfReader(file))
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            st.download_button("Download Merged PDF", output, file_name="merged.pdf")
        except:
            st.error("Merge error. Please try again.")

# Split PDF
if operation == "Split PDF ✂️" and st.session_state.uploaded_files:
    split_option = st.radio("Split Option:", ["Split each page into separate PDFs (ZIP)", "Split by fixed number of pages"])
    if split_option == "Split by fixed number of pages":
        split_size = st.number_input("Pages per split:", min_value=1, value=1)
    if st.button("Split"):
        try:
            for file in st.session_state.uploaded_files:
                reader = PdfReader(file)
                if split_option == "Split each page into separate PDFs (ZIP)":
                    zip_buf = BytesIO()
                    with zipfile.ZipFile(zip_buf, "w") as zipf:
                        for i, page in enumerate(reader.pages):
                            writer = PdfWriter()
                            writer.add_page(page)
                            page_buf = BytesIO()
                            writer.write(page_buf)
                            page_buf.seek(0)
                            zipf.writestr(f"page_{i+1}.pdf", page_buf.read())
                    zip_buf.seek(0)
                    st.download_button("Download ZIP of split pages", zip_buf, "split_pages.zip")
                else:
                    count = 0
                    part_num = 1
                    while count < len(reader.pages):
                        writer = PdfWriter()
                        for i in range(split_size):
                            if count + i < len(reader.pages):
                                writer.add_page(reader.pages[count+i])
                        part_buf = BytesIO()
                        writer.write(part_buf)
                        part_buf.seek(0)
                        st.download_button(f"Download Part {part_num}", part_buf, file_name=f"part_{part_num}.pdf")
                        count += split_size
                        part_num += 1
        except:
            st.error("Split error. Please check the file.")

# Compress PDF
if operation == "Compress PDF 📉" and st.session_state.uploaded_files:
    if st.button("Compress PDF"):
        for file in st.session_state.uploaded_files:
            reader = PdfReader(file)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            st.download_button("Download Compressed PDF", output, "compressed.pdf")

# Insert Page Numbers
if operation == "Insert Page Numbers 📝 to PDF" and st.session_state.uploaded_files:
    if st.button("Insert Page Numbers"):
        for file in st.session_state.uploaded_files:
            reader = PdfReader(file)
            pdf = FPDF()
            for idx, page in enumerate(reader.pages):
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(0, 10, txt=f"Page {idx+1}", ln=1, align="C")
            output_buf = BytesIO()
            pdf.output(output_buf)
            output_buf.seek(0)
            st.download_button("Download PDF with Page Numbers", output_buf, "paged.pdf")

# Images to PDF
if operation == "Images to PDF 🖼️" and st.session_state.uploaded_files:
    if st.button("Create PDF from Images"):
        pdf = FPDF()
        for file in st.session_state.uploaded_files:
            image = Image.open(file)
            pdf.add_page()
            img_path = os.path.join(tempfile.mkdtemp(), "temp.jpg")
            image.save(img_path)
            pdf.image(img_path, x=10, y=10, w=180)
        output = BytesIO()
        pdf.output(output)
        output.seek(0)
        st.download_button("Download Images PDF", output, "images.pdf")

st.markdown("""<hr><small>Copyright © 2025  
Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela</small>""", unsafe_allow_html=True)

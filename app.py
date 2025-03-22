import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
from PIL import Image
import os, io, zipfile
import fitz  # PyMuPDF
from docx2pdf import convert as convert_docx
import comtypes.client
import tempfile
import shutil

st.set_page_config(page_title="PDF Utility App", layout="centered")
st.image("logo1.png", use_column_width=False)

st.title("PDF & File Utility App")

# Function to convert DOC/DOCX/PPT/PPTX to PDF
def convert_office_file_to_pdf(file, ext):
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file.name)
        output_pdf = os.path.join(temp_dir, "output.pdf")
        with open(input_path, "wb") as f:
            f.write(file.getvalue())

        if ext == ".docx":
            convert_docx(input_path, output_pdf)
        elif ext == ".doc":
            word = comtypes.client.CreateObject("Word.Application")
            doc = word.Documents.Open(input_path)
            doc.SaveAs(output_pdf, FileFormat=17)
            doc.Close()
            word.Quit()
        elif ext == ".pptx" or ext == ".ppt":
            powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
            powerpoint.Visible = 1
            deck = powerpoint.Presentations.Open(input_path)
            deck.SaveAs(output_pdf, 32) 
            deck.Close()
            powerpoint.Quit()

        return output_pdf

# Function to convert text file to PDF
def convert_txt_to_pdf(file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    content = file.getvalue().decode("utf-8")
    for line in content.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# UI Options
operations = [
    "Generate Empty PDF",
    "Convert Any File to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF",
    "Compress PDF",
    "Insert Page Numbers",
    "Images to PDF",
    "Remove All Uploaded Files"
]
selected_operation = st.selectbox("Select Operation", operations)

allowed_formats = {
    "Convert Any File to PDF": "Allowed: TXT, DOC, DOCX, PPT, PPTX, PNG, JPG, JPEG",
    "Extract Pages from PDF": "Upload a single PDF",
    "Merge PDFs": "Upload exactly 2 PDFs",
    "Split PDF": "Upload a single PDF",
    "Compress PDF": "Upload a single PDF (up to 200MB)",
    "Insert Page Numbers": "Upload a single PDF",
    "Images to PDF": "Upload multiple images (JPG, PNG, JPEG)",
}

if selected_operation in allowed_formats:
    st.info(allowed_formats[selected_operation])

uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)

# Error handling
def invalid_file_format():
    st.error("❗ Incorrect file format uploaded! Please check the allowed formats.", icon="⚠️")

# Generate Empty PDF
if selected_operation == "Generate Empty PDF":
    pages = st.number_input("Enter number of pages:", min_value=1, max_value=500, step=1)
    if st.button("Generate PDF"):
        pdf = FPDF()
        for _ in range(pages):
            pdf.add_page()
        output = io.BytesIO()
        pdf.output(output)
        output.seek(0)
        st.download_button("Download Empty PDF", output, file_name="empty.pdf")

# Convert Any File to PDF
elif selected_operation == "Convert Any File to PDF" and uploaded_files:
    pdf_outputs = []
    for file in uploaded_files:
        ext = os.path.splitext(file.name)[-1].lower()
        if ext in [".txt"]:
            pdf_outputs.append((file.name.replace(ext, ".pdf"), convert_txt_to_pdf(file)))
        elif ext in [".docx", ".doc", ".pptx", ".ppt"]:
            pdf_path = convert_office_file_to_pdf(file, ext)
            with open(pdf_path, "rb") as f:
                pdf_outputs.append((file.name.replace(ext, ".pdf"), io.BytesIO(f.read())))
        elif ext in [".png", ".jpg", ".jpeg"]:
            image = Image.open(file)
            pdf_bytes = io.BytesIO()
            image.convert("RGB").save(pdf_bytes, "PDF")
            pdf_bytes.seek(0)
            pdf_outputs.append((file.name.replace(ext, ".pdf"), pdf_bytes))
        else:
            invalid_file_format()
    if pdf_outputs:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, file_data in pdf_outputs:
                zipf.writestr(name, file_data.getvalue())
        zip_buffer.seek(0)
        st.download_button("Download All PDFs (ZIP)", zip_buffer, file_name="converted_files.zip")

# Extract Pages
elif selected_operation == "Extract Pages from PDF" and uploaded_files:
    file = uploaded_files[0]
    reader = PdfReader(file)
    ranges = st.text_input("Enter pages or ranges (e.g., 1,3-5):")
    if st.button("Extract Pages"):
        writer = PdfWriter()
        for part in ranges.split(","):
            if "-" in part:
                start, end = part.split("-")
                for i in range(int(start) - 1, int(end)):
                    writer.add_page(reader.pages[i])
            else:
                writer.add_page(reader.pages[int(part) - 1])
        output_pdf = io.BytesIO()
        writer.write(output_pdf)
        output_pdf.seek(0)
        st.download_button("Download Extracted PDF", output_pdf, file_name="extracted_pages.pdf")

# Merge PDFs
elif selected_operation == "Merge PDFs" and len(uploaded_files) == 2:
    if st.button("Merge Now"):
        writer = PdfWriter()
        for file in uploaded_files:
            reader = PdfReader(file)
            for page in reader.pages:
                writer.add_page(page)
        merged_output = io.BytesIO()
        writer.write(merged_output)
        merged_output.seek(0)
        st.download_button("Download Merged PDF", merged_output, file_name="merged.pdf")

# Split PDF
elif selected_operation == "Split PDF" and uploaded_files:
    file = uploaded_files[0]
    reader = PdfReader(file)
    split_option = st.radio("Choose split option:", ["Custom split", "Split into individual pages"])
    if split_option == "Custom split":
        split_size = st.number_input("Split after how many pages?", min_value=1, step=1)
        if st.button("Split"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i in range(0, len(reader.pages), split_size):
                    writer = PdfWriter()
                    for page in reader.pages[i:i+split_size]:
                        writer.add_page(page)
                    temp_pdf = io.BytesIO()
                    writer.write(temp_pdf)
                    zipf.writestr(f"split_{i+1}.pdf", temp_pdf.getvalue())
            zip_buffer.seek(0)
            st.download_button("Download Split PDFs (ZIP)", zip_buffer, file_name="split_files.zip")
    else:
        if st.button("Split into single pages"):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    single_pdf = io.BytesIO()
                    writer.write(single_pdf)
                    zipf.writestr(f"page_{i+1}.pdf", single_pdf.getvalue())
            zip_buffer.seek(0)
            st.download_button("Download ZIP", zip_buffer, file_name="individual_pages.zip")

# Compress PDF
elif selected_operation == "Compress PDF" and uploaded_files:
    file = uploaded_files[0]
    compression_level = st.slider("Compression quality (lower = more compressed)", 10, 95, 50)
    if st.button("Compress Now"):
        pdf_document = fitz.open(stream=file.getvalue(), filetype="pdf")
        compressed_pdf = io.BytesIO()
        pdf_document.save(compressed_pdf, garbage=4, deflate=True, clean=True)
        compressed_pdf.seek(0)
        st.download_button("Download Compressed PDF", compressed_pdf, file_name="compressed.pdf")

# Insert Page Numbers
elif selected_operation == "Insert Page Numbers" and uploaded_files:
    file = uploaded_files[0]
    if st.button("Insert Page Numbers"):
        pdf_document = fitz.open(stream=file.getvalue(), filetype="pdf")
        for page_number, page in enumerate(pdf_document.pages(), start=1):
            page.insert_text((72, page.rect.height - 50), str(page_number), fontsize=12, color=(0, 0, 0))
        output_pdf = io.BytesIO()
        pdf_document.save(output_pdf)
        output_pdf.seek(0)
        st.download_button("Download PDF with Page Numbers", output_pdf, file_name="numbered.pdf")

# Images to PDF
elif selected_operation == "Images to PDF" and uploaded_files:
    images = [Image.open(f).convert("RGB") for f in uploaded_files]
    output_pdf = io.BytesIO()
    images[0].save(output_pdf, save_all=True, append_images=images[1:], format="PDF")
    output_pdf.seek(0)
    st.download_button("Download PDF", output_pdf, file_name="images_to_pdf.pdf")

# Remove all
elif selected_operation == "Remove All Uploaded Files":
    st.success("All uploaded files removed! You can re-upload now.")

# Footer
st.markdown("""
<hr>
<div style="text-align:center; font-size: small;">
© 2025 Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | trainees from techwing 🧡
</div>
""", unsafe_allow_html=True)

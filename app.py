import streamlit as st
import os
import io
import zipfile
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from docx2pdf import convert as docx2pdf_convert
from pptx import Presentation
from datetime import datetime

st.set_page_config(page_title="PDF & File Converter", layout="wide")
st.title("💚 PDF & File Converter Web App")

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

uploaded_files = []

def check_uploaded_files(files, allowed_extensions):
    if not files:
        st.warning("Please upload at least one file.")
        return False
    invalid_files = [f.name for f in files if not any(f.name.lower().endswith(ext) for ext in allowed_extensions)]
    if invalid_files:
        st.error(f"Unsupported file format: {', '.join(invalid_files)}.\n\nAllowed: {', '.join(allowed_extensions)}")
        return False
    return True

def save_pdf(output_writer, output_name):
    output_buffer = io.BytesIO()
    output_writer.write(output_buffer)
    output_buffer.seek(0)
    st.download_button(f"Download {output_name}", output_buffer, file_name=output_name, mime="application/pdf")

operation = st.selectbox("**Select an Operation:**", list(file_formats.keys()))

if operation:
    allowed = file_formats[operation]
    if allowed:
        st.info(f"Allowed file formats: {', '.join(allowed)}")
        uploaded_files = st.file_uploader("Upload Files", type=allowed, accept_multiple_files=True)
    elif operation != "Generate Empty PDF 📄":
        st.warning("No files required for this operation.")

    if uploaded_files and not check_uploaded_files(uploaded_files, allowed):
        uploaded_files = []

    if uploaded_files or operation == "Generate Empty PDF 📄":
        custom_filename = st.text_input("Enter custom file name (without extension)", "output")
        if st.button("Process"):
            try:
                if operation == "Generate Empty PDF 📄":
                    pdf = FPDF()
                    for i in range(1, 6):
                        pdf.add_page()
                        pdf.set_font("Arial", size=24)
                        pdf.cell(200, 100, txt=f"Page {i}", ln=True, align="C")
                    pdf_output = pdf.output(dest="S").encode("latin-1")
                    st.download_button("Download Empty PDF", data=pdf_output, file_name=f"{custom_filename}.pdf", mime="application/pdf")

                elif operation == "Convert Any File to PDF 🔄":
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        for file in uploaded_files:
                            ext = file.name.split(".")[-1].lower()
                            pdf_writer = PdfWriter()
                            if ext == "txt":
                                content = file.read().decode()
                                pdf = FPDF()
                                pdf.add_page()
                                pdf.set_font("Arial", size=12)
                                pdf.multi_cell(0, 10, content)
                                pdf_stream = io.BytesIO(pdf.output(dest="S").encode("latin-1"))
                                zip_file.writestr(f"{file.name}.pdf", pdf_stream.getvalue())
                            elif ext == "docx":
                                doc_path = f"{file.name}"
                                with open(doc_path, "wb") as f:
                                    f.write(file.getvalue())
                                out_path = f"{file.name}.pdf"
                                docx2pdf_convert(doc_path, out_path)
                                with open(out_path, "rb") as f:
                                    zip_file.writestr(f"{file.name}.pdf", f.read())
                                os.remove(doc_path)
                                os.remove(out_path)
                            elif ext == "pptx":
                                prs = Presentation(io.BytesIO(file.getvalue()))
                                pdf = FPDF()
                                for slide in prs.slides:
                                    pdf.add_page()
                                    pdf.set_font("Arial", size=16)
                                    text = ""
                                    for shape in slide.shapes:
                                        if hasattr(shape, "text"):
                                            text += shape.text + "\n"
                                    pdf.multi_cell(0, 10, text.strip())
                                pdf_stream = io.BytesIO(pdf.output(dest="S").encode("latin-1"))
                                zip_file.writestr(f"{file.name}.pdf", pdf_stream.getvalue())
                            elif ext in ["png", "jpg", "jpeg"]:
                                image = Image.open(file)
                                pdf = FPDF(unit="pt", format=image.size)
                                pdf.add_page()
                                img_buffer = io.BytesIO()
                                image.save(img_buffer, format="PNG")
                                img_buffer.seek(0)
                                pdf.image(img_buffer, 0, 0)
                                pdf_stream = io.BytesIO(pdf.output(dest="S").encode("latin-1"))
                                zip_file.writestr(f"{file.name}.pdf", pdf_stream.getvalue())
                    zip_buffer.seek(0)
                    st.download_button("Download All PDFs (ZIP)", zip_buffer, file_name=f"{custom_filename}.zip")

                elif operation == "Extract Pages from PDF 🪓":
                    page_numbers = st.text_input("Enter page numbers to extract (comma-separated)", "1")
                    if st.button("Extract"):
                        pdf_reader = PdfReader(uploaded_files[0])
                        output = PdfWriter()
                        pages = [int(i.strip()) - 1 for i in page_numbers.split(",")]
                        for p in pages:
                            output.add_page(pdf_reader.pages[p])
                        save_pdf(output, f"{custom_filename}.pdf")

                elif operation == "Merge PDFs 📚":
                    output = PdfWriter()
                    for file in uploaded_files:
                        reader = PdfReader(io.BytesIO(file.getvalue()))
                        for page in reader.pages:
                            output.add_page(page)
                    save_pdf(output, f"{custom_filename}.pdf")

                elif operation == "Split PDF ✂️":
                    pdf_reader = PdfReader(io.BytesIO(uploaded_files[0].getvalue()))
                    mid = len(pdf_reader.pages) // 2
                    first_half = PdfWriter()
                    second_half = PdfWriter()
                    for i, page in enumerate(pdf_reader.pages):
                        if i < mid:
                            first_half.add_page(page)
                        else:
                            second_half.add_page(page)
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                        out1 = io.BytesIO()
                        first_half.write(out1)
                        zip_file.writestr(f"{custom_filename}_part1.pdf", out1.getvalue())
                        out2 = io.BytesIO()
                        second_half.write(out2)
                        zip_file.writestr(f"{custom_filename}_part2.pdf", out2.getvalue())
                    zip_buffer.seek(0)
                    st.download_button("Download Split PDFs (ZIP)", zip_buffer, file_name=f"{custom_filename}.zip")

                elif operation == "Compress PDF 📉":
                    pdf_reader = PdfReader(io.BytesIO(uploaded_files[0].getvalue()))
                    output = PdfWriter()
                    for page in pdf_reader.pages:
                        output.add_page(page)
                    save_pdf(output, f"{custom_filename}.pdf")

                elif operation == "Insert Page Numbers 📝 to PDF":
                    reader = PdfReader(io.BytesIO(uploaded_files[0].getvalue()))
                    pdf = FPDF()
                    for i, page in enumerate(reader.pages, start=1):
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.cell(0, 10, f"Page {i}", 0, 1, "C")
                    pdf_output = pdf.output(dest="S").encode("latin-1")
                    st.download_button("Download PDF with Page Numbers", pdf_output, file_name=f"{custom_filename}.pdf")

                elif operation == "Images to PDF 🖼️":
                    pdf = FPDF()
                    for img in uploaded_files:
                        image = Image.open(img)
                        pdf.add_page()
                        pdf.image(img, 0, 0, image.width / 2, image.height / 2)
                    pdf_output = pdf.output(dest="S").encode("latin-1")
                    st.download_button("Download Images to PDF", pdf_output, file_name=f"{custom_filename}.pdf")

            except Exception as e:
                st.error("An error occurred while processing. Please try again!")

    if uploaded_files:
        if st.button("Remove Uploaded Files"):
            uploaded_files.clear()
            st.success("Files removed! You can upload new files now.")

st.markdown("---")
st.markdown(
    "<small>Developed with 💚 by Pavan Sri Sai Mondem, Siva Satyamsetti, Uma Satyam Mounika Sapireddy, Bhuvaneswari Devi Seru, Chandu Meela</small>",
    unsafe_allow_html=True,
                    )

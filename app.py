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
    "Extract Pages from PDF 🪓",
    "Merge PDFs 📄+📃",
    "Split PDF (1 to 2 📑 PDFs)",
    "Compress PDF 📉",
    "Insert Page Numbers 📝 to PDF"
])

# ✅ Generate Empty PDF
if operation == "Generate Empty PDF 🖨️":
    st.subheader("📄 Generate an Empty PDF")
    num_pages = st.number_input("Enter number of pages:", min_value=1, max_value=10000, value=1, step=1)

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

    # ✅ Split PDF (Newly Added)
    if operation == "Split PDF (1 to 2 📑 PDFs)":
        st.subheader("✂ Split PDF into Two Parts")
        uploaded_pdf = uploaded_files[0]  # Take the first uploaded file
        pdf_reader = PdfReader(uploaded_pdf)
        total_pages = len(pdf_reader.pages)

        if total_pages > 1:
            # ✅ Select the split point
            split_page = st.number_input("Enter the page number where you want to split:", 
                                         min_value=1, max_value=total_pages-1, value=total_pages//2)

            part1_writer, part2_writer = PdfWriter(), PdfWriter()

            # ✅ First Part
            for i in range(split_page):
                part1_writer.add_page(pdf_reader.pages[i])

            # ✅ Second Part
            for i in range(split_page, total_pages):
                part2_writer.add_page(pdf_reader.pages[i])

            # ✅ Save Outputs
            output1, output2 = BytesIO(), BytesIO()
            part1_writer.write(output1)
            part2_writer.write(output2)
            output1.seek(0)
            output2.seek(0)

            # ✅ Download Buttons
            st.download_button("📄 Download First Part", data=output1, file_name="Split_Part1.pdf", mime="application/pdf")
            st.download_button("📄 Download Second Part", data=output2, file_name="Split_Part2.pdf", mime="application/pdf")

        else:
            st.error("❌ The PDF must have at least 2 pages to split.")

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

    # ✅ Compress PDF
    elif operation == "Compress PDF 📉":
        pdf_reader = fitz.open(stream=uploaded_files[0].read(), filetype="pdf")
        output_pdf = BytesIO()
        pdf_reader.save(output_pdf, garbage=4, deflate=True)
        output_pdf.seek(0)
        st.download_button("📉 Download Compressed PDF", data=output_pdf, file_name="Compressed_PDF.pdf", mime="application/pdf")

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

# ✅ Footer
st.markdown('<div class="footer">© Pavan srisai mondem | Siva satyamsetti | Uma satya mounika sapireddy | Bhuvaneswari Devi seru | Chandu meela | Techwing Trainees 🧡</div>', unsafe_allow_html=True)

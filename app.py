import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# ✅ Load Custom CSS
def load_css():
    with open("assets/Style.css", "r") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

load_css()

# ✅ Display Logo at the Top
st.image("logo1.png", width=150)
st.markdown('<p class="title">📄 PDF & File Converter</p>', unsafe_allow_html=True)

# --- Show Main Options ---
operation = st.selectbox("Select an operation:", [
    "Generate Empty PDF",
    "Convert Any File to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF",
    "Compress PDF",
    "Insert Page Numbers",
    "Organize PDF (Drag & Drop)"
])

# ✅ Generate Empty PDF
if operation == "Generate Empty PDF":
    st.markdown('<p class="subheader">📝 Create an Empty PDF</p>', unsafe_allow_html=True)
    num_pages = st.number_input("Enter number of pages:", min_value=1, step=1)

    if st.button("Generate Empty PDF"):
        output_pdf = BytesIO()
        pdf_canvas = canvas.Canvas(output_pdf)
        for i in range(num_pages):
            pdf_canvas.drawString(100, 750, f"Page {i+1}")
            pdf_canvas.showPage()
        pdf_canvas.save()
        output_pdf.seek(0)
        file_name = st.text_input("Enter output file name:", value="Empty_PDF")
        st.download_button("💚 Download Empty PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

# ✅ Upload File Section
uploaded_files = st.file_uploader("Upload file(s)", type=["pdf", "png", "jpg", "jpeg", "docx", "pptx", "txt"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded!")

    # ✅ PDF Compression
    if operation == "Compress PDF":
        st.markdown('<p class="subheader">📉 Compress PDF</p>', unsafe_allow_html=True)

        pdf_reader = PdfReader(uploaded_files[0])
        pdf_writer = PdfWriter()

        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        pdf_writer.add_metadata({"/Producer": "PyPDF2 Compression"})

        output_pdf = BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)

        file_name = st.text_input("Enter output file name:", value="Compressed_PDF")
        st.download_button("💚 Download Compressed PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Insert Page Numbers (Fixed)
    if operation == "Insert Page Numbers":
        st.markdown('<p class="subheader">🔢 Insert Page Numbers</p>', unsafe_allow_html=True)

        pdf_reader = PdfReader(uploaded_files[0])
        output_pdf = BytesIO()
        pdf_writer = PdfWriter()

        for i, page in enumerate(pdf_reader.pages):
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(500, 20, f"Page {i + 1}")  # Add page number at bottom
            c.save()

            packet.seek(0)

            # Merge the page number with the existing page
            overlay_reader = PdfReader(packet)
            page.merge_page(overlay_reader.pages[0])
            pdf_writer.add_page(page)

        pdf_writer.write(output_pdf)
        output_pdf.seek(0)

        file_name = st.text_input("Enter output file name:", value="Numbered_PDF")
        st.download_button("💚 Download Numbered PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Organize PDF (Drag & Drop)
    if operation == "Organize PDF (Drag & Drop)":
        st.markdown('<p class="subheader">📂 Reorder PDF Pages</p>', unsafe_allow_html=True)

        pdf_reader = PdfReader(uploaded_files[0])
        total_pages = len(pdf_reader.pages)

        order = st.text_input(f"Enter new page order (1-{total_pages}), e.g., 3,1,2:")
        
        if st.button("Reorder & Save PDF"):
            try:
                pdf_writer = PdfWriter()
                new_order = [int(x) - 1 for x in order.split(",")]

                for i in new_order:
                    pdf_writer.add_page(pdf_reader.pages[i])

                output_pdf = BytesIO()
                pdf_writer.write(output_pdf)
                output_pdf.seek(0)

                file_name = st.text_input("Enter output file name:", value="Reordered_PDF")
                st.download_button("💚 Download Reordered PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"❌ Error reordering pages: {e}")

# ✅ Copyright Text at Bottom
st.markdown('<p class="small-text">© Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | Trainees from Techwing 🧡</p>', unsafe_allow_html=True)

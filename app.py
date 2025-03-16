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
    "Split PDF 1 to 2 pdf's",
    "Compress PDF",
    "Insert Page Numbers to pdf",
    "Organize PDF (Drag & Drop)"
])

# ✅ Upload File Section
uploaded_files = st.file_uploader("Upload file(s)", type=["pdf", "png", "jpg", "jpeg", "docx", "pptx", "txt"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded!")

    # ✅ Merge PDFs
    if operation == "Merge PDFs" and len(uploaded_files) > 1:
        st.markdown('<p class="subheader">📑 Merge Multiple PDFs</p>', unsafe_allow_html=True)

        pdf_writer = PdfWriter()

        for file in uploaded_files:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        output_pdf = BytesIO()
        pdf_writer.write(output_pdf)
        output_pdf.seek(0)

        file_name = st.text_input("Enter output file name:", value="Merged_PDF")
        st.download_button("💚 Download Merged PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Split PDF (1 to 2 PDFs)
    if operation == "Split PDF 1 to 2 pdf's" and len(uploaded_files) == 1:
        st.markdown('<p class="subheader">✂ Split PDF into Two Parts</p>', unsafe_allow_html=True)

        pdf_reader = PdfReader(uploaded_files[0])
        total_pages = len(pdf_reader.pages)

        if total_pages > 1:
            mid = total_pages // 2

            part1_writer = PdfWriter()
            part2_writer = PdfWriter()

            for i in range(mid):
                part1_writer.add_page(pdf_reader.pages[i])
            for i in range(mid, total_pages):
                part2_writer.add_page(pdf_reader.pages[i])

            output1 = BytesIO()
            part1_writer.write(output1)
            output1.seek(0)

            output2 = BytesIO()
            part2_writer.write(output2)
            output2.seek(0)

            st.download_button("📄 Download First Half", data=output1, file_name="Part1.pdf", mime="application/pdf")
            st.download_button("📄 Download Second Half", data=output2, file_name="Part2.pdf", mime="application/pdf")
        else:
            st.error("❌ The PDF must have at least 2 pages to split.")

    # ✅ Insert Page Numbers
    if operation == "Insert Page Numbers to pdf":
        st.markdown('<p class="subheader">🔢 Insert Page Numbers</p>', unsafe_allow_html=True)

        pdf_reader = PdfReader(uploaded_files[0])
        output_pdf = BytesIO()
        pdf_writer = PdfWriter()

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

        file_name = st.text_input("Enter output file name:", value="Numbered_PDF")
        st.download_button("💚 Download Numbered PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Convert Any File to PDF
    if operation == "Convert Any File to PDF":
        st.markdown('<p class="subheader">🔄 Convert File to PDF</p>', unsafe_allow_html=True)

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name.split(".")[0]
            file_extension = uploaded_file.name.split(".")[-1]

            output_pdf = BytesIO()

            if file_extension in ["png", "jpg", "jpeg"]:
                image = Image.open(uploaded_file)
                image.convert("RGB").save(output_pdf, format="PDF")
                output_pdf.seek(0)

            elif file_extension == "txt":
                pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
                pdf_canvas.setFont("Helvetica", 12)
                y_position = 750
                for line in uploaded_file.getvalue().decode().split("\n"):
                    pdf_canvas.drawString(100, y_position, line)
                    y_position -= 20
                pdf_canvas.save()
                output_pdf.seek(0)

            elif file_extension == "docx":
                doc = Document(uploaded_file)
                pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
                pdf_canvas.setFont("Helvetica", 12)
                y_position = 750
                for para in doc.paragraphs:
                    pdf_canvas.drawString(100, y_position, para.text)
                    y_position -= 20
                pdf_canvas.save()
                output_pdf.seek(0)

            elif file_extension == "pptx":
                ppt = Presentation(uploaded_file)
                pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
                pdf_canvas.setFont("Helvetica", 12)
                y_position = 750
                for slide in ppt.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            pdf_canvas.drawString(100, y_position, shape.text)
                            y_position -= 20
                pdf_canvas.save()
                output_pdf.seek(0)

            else:
                st.error(f"❌ Unsupported file format: {file_extension}")
                continue

            st.download_button(f"💚 Download {file_name}.pdf", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

# ✅ Copyright Text at Bottom
st.markdown('<p class="small-text">© Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela | Trainees from Techwing 🧡</p>', unsafe_allow_html=True)

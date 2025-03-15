import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# ✅ Load Custom CSS
def load_css():
    with open("assets/style.css", "r") as css_file:
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
    "Split PDF"
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
    for uploaded_file in uploaded_files:
        file_bytes = BytesIO(uploaded_file.getbuffer())
        st.success(f"✅ Uploaded: {uploaded_file.name}")

    # ✅ Convert Any File to PDF
    if operation == "Convert Any File to PDF":
        st.markdown('<p class="subheader">📂 Convert Any File to PDF</p>', unsafe_allow_html=True)
        
        for uploaded_file in uploaded_files:
            file_bytes = BytesIO(uploaded_file.getbuffer())

            # ✅ Convert Images to PDF
            if uploaded_file.type.startswith("image"):
                image = Image.open(file_bytes)
                output_pdf = BytesIO()
                image.save(output_pdf, "PDF", resolution=100.0)
                output_pdf.seek(0)
                file_name = st.text_input(f"Enter output file name for {uploaded_file.name}:", value="Converted_Image")
                st.download_button("💚 Download PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

            # ✅ Convert TXT to PDF
            elif uploaded_file.type == "text/plain":
                text_content = uploaded_file.read().decode("utf-8")
                output_pdf = BytesIO()
                pdf_canvas = canvas.Canvas(output_pdf)
                pdf_canvas.setFont("Helvetica", 12)
                y_position = 750
                for line in text_content.split("\n"):
                    pdf_canvas.drawString(50, y_position, line)
                    y_position -= 20
                pdf_canvas.save()
                output_pdf.seek(0)
                file_name = st.text_input(f"Enter output file name for {uploaded_file.name}:", value="Converted_TXT")
                st.download_button("💚 Download PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

            # ✅ Convert DOCX to PDF
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                try:
                    doc = Document(file_bytes)
                    output_pdf = BytesIO()
                    pdf_canvas = canvas.Canvas(output_pdf)
                    pdf_canvas.setFont("Helvetica", 12)
                    y_position = 750
                    for para in doc.paragraphs:
                        pdf_canvas.drawString(50, y_position, para.text)
                        y_position -= 20
                    pdf_canvas.save()
                    output_pdf.seek(0)
                    file_name = st.text_input(f"Enter output file name for {uploaded_file.name}:", value="Converted_Word")
                    st.download_button("💚 Download PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")
                except Exception as e:
                    st.error(f"❌ Error converting DOCX: {e}")

    # ✅ Extract Pages from PDF
    if operation == "Extract Pages from PDF":
        st.markdown('<p class="subheader">📑 Extract Pages from PDF</p>', unsafe_allow_html=True)
        pdf_file = uploaded_files[0]  # Take first uploaded PDF
        pdf_reader = PdfReader(BytesIO(pdf_file.getbuffer()))
        total_pages = len(pdf_reader.pages)
        pages_to_extract = st.text_input(f"Enter page numbers (1-{total_pages}), e.g., 1,3-5:")
        
        if st.button("Extract Pages"):
            output_pdf = BytesIO()
            pdf_writer = PdfWriter()
            try:
                pages = []
                for part in pages_to_extract.split(","):
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        pages.extend(range(start - 1, end))
                    else:
                        pages.append(int(part) - 1)

                for page_num in pages:
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                pdf_writer.write(output_pdf)
                output_pdf.seek(0)
                st.download_button("💚 Download Extracted PDF", data=output_pdf, file_name="Extracted_Pages.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ✅ Merge PDFs
    if operation == "Merge PDFs" and len(uploaded_files) > 1:
        st.markdown('<p class="subheader">🔗 Merge PDFs</p>', unsafe_allow_html=True)
        if st.button("Merge PDFs"):
            output_pdf = BytesIO()
            pdf_writer = PdfWriter()
            try:
                for pdf_file in uploaded_files:
                    pdf_reader = PdfReader(BytesIO(pdf_file.getbuffer()))
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                pdf_writer.write(output_pdf)
                output_pdf.seek(0)
                st.download_button("💚 Download Merged PDF", data=output_pdf, file_name="Merged.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"❌ Error merging PDFs: {e}")

    # ✅ Split PDF
    if operation == "Split PDF":
        st.markdown('<p class="subheader">✂️ Split PDF</p>', unsafe_allow_html=True)
        pdf_file = uploaded_files[0]
        pdf_reader = PdfReader(BytesIO(pdf_file.getbuffer()))
        total_pages = len(pdf_reader.pages)

        split_page_number = st.number_input(f"Enter page number (1-{total_pages}) to split at:", min_value=1, max_value=total_pages-1, step=1)

        if st.button("Split PDF"):
            try:
                part1 = PdfWriter()
                part2 = PdfWriter()
                
                for i in range(split_page_number):
                    part1.add_page(pdf_reader.pages[i])
                
                for i in range(split_page_number, total_pages):
                    part2.add_page(pdf_reader.pages[i])

                part1_output = BytesIO()
                part2_output = BytesIO()
                part1.write(part1_output)
                part2.write(part2_output)
                part1_output.seek(0)
                part2_output.seek(0)

                st.download_button("💚 Download First Part", data=part1_output, file_name="Part_1.pdf", mime="application/pdf")
                st.download_button("💚 Download Second Part", data=part2_output, file_name="Part_2.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"❌ Error splitting PDF: {e}")

# ✅ Copyright Text
st.markdown('<p class="small-text">© Content Owners: Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela</p>', unsafe_allow_html=True)

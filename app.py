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
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded!")

    # ✅ Convert Any File to PDF
    if operation == "Convert Any File to PDF":
        st.markdown('<p class="subheader">📂 Convert Any File to PDF</p>', unsafe_allow_html=True)

        uploaded_file = uploaded_files[0]
        file_bytes = BytesIO(uploaded_file.getbuffer())

        # ✅ Convert Images to PDF
        if uploaded_file.type.startswith("image"):
            image = Image.open(file_bytes)
            output_pdf = BytesIO()
            image.save(output_pdf, "PDF", resolution=100.0)
            output_pdf.seek(0)
            file_name = st.text_input("Enter output file name:", value="Converted_Image")
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
            file_name = st.text_input("Enter output file name:", value="Converted_TXT")
            st.download_button("💚 Download PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Extract Pages from PDF (Fixed Download)
    if operation == "Extract Pages from PDF":
        st.markdown('<p class="subheader">📑 Extract Pages from PDF</p>', unsafe_allow_html=True)

        pdf_reader = PdfReader(uploaded_files[0])
        total_pages = len(pdf_reader.pages)
        pages_input = st.text_input(f"Enter pages to extract (1-{total_pages}), e.g., 1,3-5:")
        
        if st.button("Extract Pages"):
            try:
                pdf_writer = PdfWriter()
                selected_pages = []
                
                for part in pages_input.split(","):
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        selected_pages.extend(range(start - 1, end))
                    else:
                        selected_pages.append(int(part) - 1)

                for page_num in selected_pages:
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                output_pdf = BytesIO()
                pdf_writer.write(output_pdf)
                output_pdf.seek(0)

                file_name = st.text_input("Enter output file name:", value="Extracted_Pages")
                st.download_button("💚 Download Extracted PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"❌ Error extracting pages: {e}")

    # ✅ Merge PDFs (Fixed Multi-File Selection)
    if operation == "Merge PDFs":
        st.markdown('<p class="subheader">📂 Merge Multiple PDFs</p>', unsafe_allow_html=True)

        if len(uploaded_files) < 2:
            st.warning("⚠ Upload at least two PDFs to merge.")
        else:
            if st.button("Merge PDFs"):
                try:
                    pdf_writer = PdfWriter()
                    for uploaded_file in uploaded_files:
                        pdf_reader = PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            pdf_writer.add_page(page)

                    output_pdf = BytesIO()
                    pdf_writer.write(output_pdf)
                    output_pdf.seek(0)

                    file_name = st.text_input("Enter output file name:", value="Merged_PDF")
                    st.download_button("💚 Download Merged PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

                except Exception as e:
                    st.error(f"❌ Error merging PDFs: {e}")

    # ✅ Split PDF (Now Works Properly)
    if operation == "Split PDF":
        st.markdown('<p class="subheader">✂ Split a PDF</p>', unsafe_allow_html=True)

        pdf_reader = PdfReader(uploaded_files[0])
        total_pages = len(pdf_reader.pages)
        split_page = st.number_input(f"Enter split page (1-{total_pages-1}):", min_value=1, max_value=total_pages-1, step=1)

        if st.button("Split PDF"):
            try:
                pdf_writer1, pdf_writer2 = PdfWriter(), PdfWriter()
                for i in range(total_pages):
                    if i < split_page:
                        pdf_writer1.add_page(pdf_reader.pages[i])
                    else:
                        pdf_writer2.add_page(pdf_reader.pages[i])

                output_pdf1, output_pdf2 = BytesIO(), BytesIO()
                pdf_writer1.write(output_pdf1)
                pdf_writer2.write(output_pdf2)
                output_pdf1.seek(0)
                output_pdf2.seek(0)
                
                st.download_button("💚 Download First Part", data=output_pdf1, file_name="Split_Part1.pdf", mime="application/pdf")
                st.download_button("💚 Download Second Part", data=output_pdf2, file_name="Split_Part2.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"❌ Error splitting PDF: {e}")

# ✅ Copyright Text at Bottom
st.markdown('<p class="small-text">© Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | Bhuvaneswari Devi Seru | Chandu Meela</p>', unsafe_allow_html=True)

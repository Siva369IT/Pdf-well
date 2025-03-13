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
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx", "doc", "pptx", "txt"])

if uploaded_file:
    file_bytes = BytesIO(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # ✅ Convert Any File to PDF
    if operation == "Convert Any File to PDF":
        st.markdown('<p class="subheader">📂 Convert Any File to PDF</p>', unsafe_allow_html=True)

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

        # ✅ Convert DOCX/DOC to PDF
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
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
                file_name = st.text_input("Enter output file name:", value="Converted_Word")
                st.download_button("💚 Download PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"❌ Error converting DOCX: {e}")

        # ✅ Convert PPT/PPTX to PDF
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            prs = Presentation(file_bytes)
            output_pdf = BytesIO()
            pdf_canvas = canvas.Canvas(output_pdf)
            pdf_canvas.setFont("Helvetica", 12)
            y_position = 750
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        pdf_canvas.drawString(50, y_position, shape.text)
                        y_position -= 20
            pdf_canvas.save()
            output_pdf.seek(0)
            file_name = st.text_input("Enter output file name:", value="Converted_PPT")
            st.download_button("💚 Download PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

# ✅ Copyright Text at Bottom
st.markdown(
    '<p class="small-text">© Content Owners: Pavan Sri Sai Mondem | Siva Satyamsetti | Uma Satyam Mounika Sapireddy | '
    'Bhuvaneswari Devi Seru | Chandu Meela</p>',
    unsafe_allow_html=True
        )

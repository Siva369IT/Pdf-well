import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from pptx import Presentation
from reportlab.pdfgen import canvas

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# Load Custom CSS
def local_css():
    st.markdown("""
        <style>
            .small-text { font-size: 12px; text-align: center; margin-top: 20px; color: #888; }
        </style>
    """, unsafe_allow_html=True)

local_css()

# ✅ Add Logo at the Top
st.image("logo1.png", width=150)

st.title("📄 PDF, Image & Word Converter Tool")

# --- First, Show Main Options ---
operation = st.selectbox("Select an operation:", [
    "Generate Empty PDF",
    "Convert Images to PDF",
    "Convert TXT to PDF",
    "Convert MS Word (DOCX) to PDF",
    "Convert PPT to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF"
])

# ✅ Generate Empty PDF
if operation == "Generate Empty PDF":
    st.subheader("📝 Create an Empty PDF")
    num_pages = st.number_input("Enter number of pages:", min_value=1, step=1)
    if st.button("Generate Empty PDF", use_container_width=True):
        output_pdf = BytesIO()
        pdf_canvas = canvas.Canvas(output_pdf)
        for i in range(num_pages):
            pdf_canvas.drawString(100, 750, f"Page {i+1}")
            pdf_canvas.showPage()
        pdf_canvas.save()
        output_pdf.seek(0)
        file_name = st.text_input("Enter output file name:", value="Empty_PDF")
        st.download_button("💚 Download Empty PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

# --- Upload File Section ---
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx", "pptx", "txt"])

if uploaded_file:
    file_bytes = BytesIO(uploaded_file.getbuffer())
    st.success(f"Uploaded {uploaded_file.name} successfully!")

    # ✅ Convert Multiple Images to Single PDF
    if operation == "Convert Images to PDF":
        st.subheader("🖼️ Convert Images to PDF")
        uploaded_images = st.file_uploader("Upload multiple images", accept_multiple_files=True, type=["png", "jpg", "jpeg"])
        if uploaded_images:
            pdf_bytes = BytesIO()
            image_list = [Image.open(img).convert("RGB") for img in uploaded_images]
            first_image = image_list[0]
            first_image.save(pdf_bytes, format="PDF", save_all=True, append_images=image_list[1:])
            pdf_bytes.seek(0)
            file_name = st.text_input("Enter output file name:", value="Images_to_PDF")
            st.download_button("💚 Download PDF", data=pdf_bytes, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Convert TXT to PDF
    elif operation == "Convert TXT to PDF" and uploaded_file.type == "text/plain":
        st.subheader("📄 Convert TXT File to PDF")
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

    # ✅ Convert MS Word (DOCX) to PDF
    elif operation == "Convert MS Word (DOCX) to PDF":
        st.subheader("📄 Convert MS Word (DOCX) to PDF")

        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
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

        else:
            st.error("❌ This file format is not supported. Please upload a valid DOCX file.")

    # ✅ Convert PPT to PDF
    elif operation == "Convert PPT to PDF" and uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        st.subheader("📄 Convert PPT to PDF")
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

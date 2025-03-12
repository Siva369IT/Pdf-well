import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
from docx import Document
from reportlab.pdfgen import canvas

st.set_page_config(page_title="PDF & File Converter", layout="wide")

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/Style.css")

# Title
st.title("📄 PDF, Image & Word Converter Tool")

# --- First, Show Main Options ---
operation = st.selectbox("Select an operation:", [
    "Generate Empty PDF",
    "Convert Images to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF"
])

# --- Generate Empty PDF ---
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
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "docx", "pptx"])

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

    # ✅ Extract Pages from PDF
    elif operation == "Extract Pages from PDF" and uploaded_file.type == "application/pdf":
        st.subheader("📄 Extract Pages from PDF")
        reader = PdfReader(file_bytes)
        total_pages = len(reader.pages)
        st.write(f"Total pages: {total_pages}")
        pages_to_extract = st.multiselect("Select pages to extract:", list(range(1, total_pages + 1)))
        if st.button("Extract Pages", use_container_width=True):
            writer = PdfWriter()
            for page_num in pages_to_extract:
                writer.add_page(reader.pages[page_num - 1])
            output_pdf = BytesIO()
            writer.write(output_pdf)
            output_pdf.seek(0)
            file_name = st.text_input("Enter output file name:", value="Extracted_Pages")
            st.download_button("💚 Download Extracted PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Merge PDFs
    elif operation == "Merge PDFs":
        st.subheader("🔗 Merge Multiple PDFs")
        uploaded_files = st.file_uploader("Upload PDFs to merge", accept_multiple_files=True, type=["pdf"])
        if uploaded_files:
            if st.button("Merge PDFs", use_container_width=True):
                writer = PdfWriter()
                for file in uploaded_files:
                    reader = PdfReader(BytesIO(file.getbuffer()))
                    for page in reader.pages:
                        writer.add_page(page)
                output_pdf = BytesIO()
                writer.write(output_pdf)
                output_pdf.seek(0)
                file_name = st.text_input("Enter output file name:", value="Merged_File")
                st.download_button("💚 Download Merged PDF", data=output_pdf, file_name=f"{file_name}.pdf", mime="application/pdf")

    # ✅ Split PDF
    elif operation == "Split PDF" and uploaded_file.type == "application/pdf":
        st.subheader("✂️ Split PDF into Multiple Files")
        reader = PdfReader(file_bytes)
        total_pages = len(reader.pages)
        st.write(f"Total pages: {total_pages}")

        split_pages = st.text_input("Enter pages to split (comma-separated):")
        if split_pages:
            try:
                split_pages = [int(x.strip()) for x in split_pages.split(",") if 1 <= int(x.strip()) <= total_pages]
                split_files = []
                
                for i, page_num in enumerate(split_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])
                    output_pdf = BytesIO()
                    writer.write(output_pdf)
                    output_pdf.seek(0)
                    split_files.append((f"Split_{i+1}.pdf", output_pdf))
                
                for file_name, pdf_data in split_files:
                    st.download_button(f"💚 Download {file_name}", data=pdf_data, file_name=file_name, mime="application/pdf")

            except ValueError:
                st.error("Invalid page numbers! Please enter valid numbers.")

# --- Apply Button Styling ---
st.markdown("""
    <style>
        div[data-testid="stButton"] button {
            background-color: red;
            color: white;
            font-size: 16px;
            width: 100%;
        }
        div[data-testid="stDownloadButton"] button {
            background-color: green;
            color: white;
            font-size: 16px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import zipfile
import fitz  # PyMuPDF for compression
from PIL import Image

st.set_page_config(page_title="PDF-Well Converter", page_icon="📄", layout="centered")

st.markdown("<h1 style='text-align: center; color: green;'>PDF-Well Converter</h1>", unsafe_allow_html=True)
st.write("")

operations = [
    "Generate Empty PDF",
    "Convert Any File to PDF",
    "Extract Pages from PDF",
    "Merge PDFs",
    "Split PDF",
    "Compress PDF",
    "Insert Page Numbers into PDF",
    "Images to PDF"
]

operation = st.selectbox("Select Operation", operations)

def generate_empty_pdf(pages):
    output = BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    for p in range(pages):
        text = f"Page {p + 1}"
        text_width = c.stringWidth(text, "Helvetica", 12)
        x = (width - text_width) / 2
        y = 30  # Bottom center
        c.drawString(x, y, text)
        c.showPage()
    c.save()
    output.seek(0)
    return output

def compress_pdf(input_pdf_bytes):
    pdf_document = fitz.open(stream=input_pdf_bytes, filetype="pdf")
    compressed_output = BytesIO()
    new_pdf = fitz.open()
    for page in pdf_document:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        mem_stream = BytesIO()
        img.save(mem_stream, format="JPEG", quality=50)
        img_bytes = mem_stream.getvalue()
        rect = fitz.Rect(0, 0, page.rect.width, page.rect.height)
        new_page = new_pdf.new_page(width=rect.width, height=rect.height)
        new_page.insert_image(rect, stream=img_bytes)
    new_pdf.save(compressed_output)
    compressed_output.seek(0)
    return compressed_output

def get_file_extension(uploaded_file):
    try:
        return uploaded_file.name.split('.')[-1].lower()
    except:
        return ""

if operation == "Generate Empty PDF":
    pages = st.number_input("Enter number of pages", min_value=1, max_value=500, value=1)
    if st.button("Generate PDF"):
        pdf_file = generate_empty_pdf(pages)
        st.download_button("Download Empty PDF", pdf_file, file_name="empty_pdf.pdf")

elif operation == "Convert Any File to PDF":
    st.info("Upload files: PNG, JPG, JPEG, TXT, DOCX, PPTX")
    uploaded_files = st.file_uploader("Upload your files", type=['png', 'jpg', 'jpeg', 'txt', 'docx', 'pptx'], accept_multiple_files=True)
    if uploaded_files:
        pdf_zip = BytesIO()
        with zipfile.ZipFile(pdf_zip, 'w') as zipf:
            for file in uploaded_files:
                ext = get_file_extension(file)
                pdf_buffer = BytesIO()
                if ext in ['png', 'jpg', 'jpeg']:
                    img = Image.open(file)
                    img = img.convert('RGB')
                    img.save(pdf_buffer, format='PDF')
                elif ext == 'txt':
                    c = canvas.Canvas(pdf_buffer, pagesize=letter)
                    c.drawString(100, 750, file.getvalue().decode('utf-8')[:1000])
                    c.showPage()
                    c.save()
                elif ext == 'docx':
                    from docx import Document
                    from docx2pdf import convert
                    import tempfile
                    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
                    temp_input.write(file.getvalue())
                    temp_input.close()
                    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    temp_output.close()
                    convert(temp_input.name, temp_output.name)
                    with open(temp_output.name, 'rb') as doc_pdf:
                        pdf_buffer = BytesIO(doc_pdf.read())
                elif ext == 'pptx':
                    from pptx import Presentation
                    presentation = Presentation(file)
                    c = canvas.Canvas(pdf_buffer, pagesize=letter)
                    for slide in presentation.slides:
                        c.drawString(50, 750, f"Slide {slide.slide_id}")
                        c.showPage()
                    c.save()
                pdf_buffer.seek(0)
                zipf.writestr(file.name.replace(ext, 'pdf'), pdf_buffer.read())
        pdf_zip.seek(0)
        st.download_button("Download All Converted PDFs (ZIP)", pdf_zip, file_name="converted_pdfs.zip")
        elif operation == "Extract Pages from PDF":
    uploaded_file = st.file_uploader("Upload PDF to extract pages", type=["pdf"])
    if uploaded_file:
        pages_input = st.text_input("Enter page numbers (comma separated): e.g., 1,2,5")
        if st.button("Extract Pages"):
            reader = PdfReader(BytesIO(uploaded_file.getvalue()))
            writer = PdfWriter()
            try:
                pages = [int(x.strip()) - 1 for x in pages_input.split(',')]
                for p in pages:
                    writer.add_page(reader.pages[p])
                output = BytesIO()
                writer.write(output)
                output.seek(0)
                st.download_button("Download Extracted PDF", output, file_name="extracted_pages.pdf")
            except Exception as e:
                st.error(f"Error: {e}")

elif operation == "Merge PDFs":
    pdf_files = st.file_uploader("Upload multiple PDFs to merge", type=["pdf"], accept_multiple_files=True)
    if pdf_files and st.button("Merge"):
        writer = PdfWriter()
        for pdf in pdf_files:
            reader = PdfReader(BytesIO(pdf.getvalue()))
            for page in reader.pages:
                writer.add_page(page)
        merged_output = BytesIO()
        writer.write(merged_output)
        merged_output.seek(0)
        st.download_button("Download Merged PDF", merged_output, file_name="merged.pdf")

elif operation == "Split PDF":
    uploaded_pdf = st.file_uploader("Upload PDF to split", type=["pdf"])
    split_option = st.radio("Split Option", ["Custom page ranges", "Each page into separate PDFs"])
    if uploaded_pdf and st.button("Split PDF"):
        reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
        if split_option == "Each page into separate PDFs":
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    page_bytes = BytesIO()
                    writer.write(page_bytes)
                    page_bytes.seek(0)
                    zipf.writestr(f"page_{i+1}.pdf", page_bytes.read())
            zip_buffer.seek(0)
            st.download_button("Download All Split Pages (ZIP)", zip_buffer, file_name="split_pages.zip")
        else:
            range_size = st.number_input("Split after how many pages?", min_value=1, max_value=reader.getNumPages(), value=1)
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i in range(0, len(reader.pages), range_size):
                    writer = PdfWriter()
                    for p in range(i, min(i+range_size, len(reader.pages))):
                        writer.add_page(reader.pages[p])
                    part_buffer = BytesIO()
                    writer.write(part_buffer)
                    part_buffer.seek(0)
                    zipf.writestr(f"part_{i//range_size+1}.pdf", part_buffer.read())
            zip_buffer.seek(0)
            st.download_button("Download Split PDFs (ZIP)", zip_buffer, file_name="split_custom_parts.zip")

elif operation == "Compress PDF":
    uploaded_pdf = st.file_uploader("Upload PDF to compress", type=["pdf"])
    if uploaded_pdf and st.button("Compress PDF"):
        compressed_pdf = compress_pdf(uploaded_pdf.getvalue())
        st.download_button("Download Compressed PDF", compressed_pdf, file_name="compressed.pdf")

elif operation == "Insert Page Numbers into PDF":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf and st.button("Insert Page Numbers"):
        reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
        output_pdf = BytesIO()
        c = canvas.Canvas(output_pdf, pagesize=letter)
        width, height = letter
        for i in range(len(reader.pages)):
            page_text = f"Page {i + 1}"
            text_width = c.stringWidth(page_text, "Helvetica", 12)
            c.drawString((width - text_width) / 2, 30, page_text)
            c.showPage()
        c.save()
        output_pdf.seek(0)
        st.download_button("Download PDF with Page Numbers", output_pdf, file_name="numbered.pdf")

elif operation == "Images to PDF":
    st.info("Upload multiple images to combine into a single PDF")
    image_files = st.file_uploader("Upload images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if image_files and st.button("Convert Images to Single PDF"):
        pdf_bytes = BytesIO()
        images = []
        for img_file in image_files:
            img = Image.open(img_file)
            images.append(img.convert('RGB'))
        if images:
            images[0].save(pdf_bytes, save_all=True, append_images=images[1:], format='PDF')
        pdf_bytes.seek(0)
        st.download_button("Download Combined PDF", pdf_bytes, file_name="images_combined.pdf")
        elif operation == "Extract Pages from PDF":
    uploaded_file = st.file_uploader("Upload PDF to extract pages", type=["pdf"])
    if uploaded_file:
        pages_input = st.text_input("Enter page numbers (comma separated): e.g., 1,2,5")
        if st.button("Extract Pages"):
            reader = PdfReader(BytesIO(uploaded_file.getvalue()))
            writer = PdfWriter()
            try:
                pages = [int(x.strip()) - 1 for x in pages_input.split(',')]
                for p in pages:
                    writer.add_page(reader.pages[p])
                output = BytesIO()
                writer.write(output)
                output.seek(0)
                st.download_button("Download Extracted PDF", output, file_name="extracted_pages.pdf")
            except Exception as e:
                st.error(f"Error: {e}")

elif operation == "Merge PDFs":
    pdf_files = st.file_uploader("Upload multiple PDFs to merge", type=["pdf"], accept_multiple_files=True)
    if pdf_files and st.button("Merge"):
        writer = PdfWriter()
        for pdf in pdf_files:
            reader = PdfReader(BytesIO(pdf.getvalue()))
            for page in reader.pages:
                writer.add_page(page)
        merged_output = BytesIO()
        writer.write(merged_output)
        merged_output.seek(0)
        st.download_button("Download Merged PDF", merged_output, file_name="merged.pdf")

elif operation == "Split PDF":
    uploaded_pdf = st.file_uploader("Upload PDF to split", type=["pdf"])
    split_option = st.radio("Split Option", ["Custom page ranges", "Each page into separate PDFs"])
    if uploaded_pdf and st.button("Split PDF"):
        reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
        if split_option == "Each page into separate PDFs":
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    page_bytes = BytesIO()
                    writer.write(page_bytes)
                    page_bytes.seek(0)
                    zipf.writestr(f"page_{i+1}.pdf", page_bytes.read())
            zip_buffer.seek(0)
            st.download_button("Download All Split Pages (ZIP)", zip_buffer, file_name="split_pages.zip")
        else:
            range_size = st.number_input("Split after how many pages?", min_value=1, max_value=reader.getNumPages(), value=1)
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for i in range(0, len(reader.pages), range_size):
                    writer = PdfWriter()
                    for p in range(i, min(i+range_size, len(reader.pages))):
                        writer.add_page(reader.pages[p])
                    part_buffer = BytesIO()
                    writer.write(part_buffer)
                    part_buffer.seek(0)
                    zipf.writestr(f"part_{i//range_size+1}.pdf", part_buffer.read())
            zip_buffer.seek(0)
            st.download_button("Download Split PDFs (ZIP)", zip_buffer, file_name="split_custom_parts.zip")

elif operation == "Compress PDF":
    uploaded_pdf = st.file_uploader("Upload PDF to compress", type=["pdf"])
    if uploaded_pdf and st.button("Compress PDF"):
        compressed_pdf = compress_pdf(uploaded_pdf.getvalue())
        st.download_button("Download Compressed PDF", compressed_pdf, file_name="compressed.pdf")

elif operation == "Insert Page Numbers into PDF":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf and st.button("Insert Page Numbers"):
        reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
        output_pdf = BytesIO()
        c = canvas.Canvas(output_pdf, pagesize=letter)
        width, height = letter
        for i in range(len(reader.pages)):
            page_text = f"Page {i + 1}"
            text_width = c.stringWidth(page_text, "Helvetica", 12)
            c.drawString((width - text_width) / 2, 30, page_text)
            c.showPage()
        c.save()
        output_pdf.seek(0)
        st.download_button("Download PDF with Page Numbers", output_pdf, file_name="numbered.pdf")

elif operation == "Images to PDF":
    st.info("Upload multiple images to combine into a single PDF")
    image_files = st.file_uploader("Upload images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    if image_files and st.button("Convert Images to Single PDF"):
        pdf_bytes = BytesIO()
        images = []
        for img_file in image_files:
            img = Image.open(img_file)
            images.append(img.convert('RGB'))
        if images:
            images[0].save(pdf_bytes, save_all=True, append_images=images[1:], format='PDF')
        pdf_bytes.seek(0)
        st.download_button("Download Combined PDF", pdf_bytes, file_name="images_combined.pdf")

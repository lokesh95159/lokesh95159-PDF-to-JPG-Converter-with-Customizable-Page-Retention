import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import random
import io
import os

st.title("PDF to JPG Converter and Saver")

# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    # Save the uploaded file to a temporary file
    temp_dir = "temp_files"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)  # Ensure temp directory exists
    
    temp_pdf_path = os.path.join(temp_dir, "uploaded_temp.pdf")
    with open(temp_pdf_path, "wb") as temp_file:
        temp_file.write(uploaded_file.read())

    # Read the uploaded PDF
    reader = PdfReader(temp_pdf_path)
    total_pages = len(reader.pages)

    if total_pages < 2:
        st.error("Please upload a PDF with at least 2 pages.")
    else:
        st.success(f"PDF with {total_pages} pages uploaded successfully!")
        value=random.randint(1, total_pages),  # Default to a random page
        # Ask user which page to remain unchanged
        random_page = st.number_input(
            "Enter the page number that should remain unchanged (1-based index):",
            min_value=1,
            max_value=total_pages,
            step=1  # Ensure the page number increments by 1
        ) - 1  # Convert to 0-based index

        st.info(f"Page {random_page + 1} will remain unchanged.")

        # Ask for a custom name for the output file
        output_filename = st.text_input(
            "Enter the name for the output file (without extension):",
            value="converted_output"  # Default name
        )
        output_filename = f"{output_filename}.pdf"  # Ensure it has the .pdf extension

        # Create a PDF writer for the output
        output_writer = PdfWriter()

        for page_index in range(total_pages):
            if page_index == random_page:
                # Add the unchanged page
                output_writer.add_page(reader.pages[page_index])
            else:
                # Get the dimensions of the original page
                page = reader.pages[page_index]
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)

                # Convert the page to an image with a higher DPI
                images = convert_from_path(
                    temp_pdf_path,
                    first_page=page_index + 1,
                    last_page=page_index + 1,
                    size=(int(page_width), int(page_height)),  # Match original PDF page size
                    dpi=300  # Higher DPI for better image quality
                )
                image = images[0].convert("RGB")

                # Save the image as a PDF in memory
                image_buffer = io.BytesIO()
                image.save(image_buffer, format="PDF")
                image_buffer.seek(0)

                # Add the image as a PDF page
                image_reader = PdfReader(image_buffer)
                output_writer.add_page(image_reader.pages[0])

        # Save the output PDF to a buffer
        output_buffer = io.BytesIO()
        output_writer.write(output_buffer)
        output_buffer.seek(0)

        # Provide the resulting file for download
        st.download_button(
            label="Download the Converted PDF",
            data=output_buffer,
            file_name=output_filename,
            mime="application/pdf",
        )
        st.success("PDF processing complete! The file is ready for download.")

    # Cleanup temporary files
    os.remove(temp_pdf_path)

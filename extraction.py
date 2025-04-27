import pdfplumber

def extract_columns(pdf_path, output_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            # Define bounding boxes for left and right columns
            left_bbox = (0, 0, page.width / 2, page.height)
            right_bbox = (page.width / 2, 0, page.width, page.height)

            # Extract text from each column
            left_text = page.within_bbox(left_bbox).extract_text()
            right_text = page.within_bbox(right_bbox).extract_text()

            # Combine the text from both columns
            if left_text:
                text += left_text + "\n"
            if right_text:
                text += right_text + "\n"

    # Save the extracted text to a file
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(text)

# Example usage
extract_columns("C:\\Users\\Lawrence Melvin\\Downloads\\Care_Heart.pdf",
                "C:\\Users\\Lawrence Melvin\\Downloads\\output.txt")
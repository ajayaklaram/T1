import fitz  # PyMuPDF
import re
import csv
import gradio as gr

# Function to extract all raw lines from the PDF for debugging
def extract_raw_lines(file):
    pdf_document = fitz.open(file.name)
    all_lines = []
    for page in pdf_document:
        text = page.get_text("text")
        lines = text.split("\n")
        all_lines.extend(lines)
    pdf_document.close()
    return all_lines

# Function to extract rows dynamically from the raw lines
def extract_rows(raw_lines):
    extracted_data = []
    current_entry = {}

    for line in raw_lines:
        # Match main POS row
        match = re.match(
            r"(?P<pos>\d+)\s+(?P<item_code>\d+.*?)\s+(?P<unit>[A-Z]+)\s+(?P<delivery_date>\d{2}-\d{2}-\d{4})\s+"
            r"(?P<quantity>\d+)\s+(?P<basic_price>\d+\.\d+)\s+(?P<discount>\d+)\s+(?P<currency>[A-Z]+)\s+"
            r"(?P<amount>\d+)\s+(?P<subtotal>\d+\.\d+)",
            line,
        )
        if match:
            # Save the parsed POS data
            current_entry = {
                "Pos.": match.group("pos"),
                "Item Code": match.group("item_code").strip(),
                "Unit": match.group("unit"),
                "Delivery Date": match.group("delivery_date"),
                "Quantity": int(match.group("quantity")),
                "Basic Price": float(match.group("basic_price")),
                "Discount": int(match.group("discount")),
                "Cur.": match.group("currency"),
                "Amount": float(match.group("amount")),
                "Sub Total": float(match.group("subtotal")),
            }
            extracted_data.append(current_entry)
            current_entry = {}
        # Match multiline descriptions for Item Code
        elif current_entry:
            current_entry["Item Code"] += " " + line.strip()

    return extracted_data

# Gradio function to process the PDF
def process_pdf(file):
    # Step 1: Extract raw lines from PDF
    raw_lines = extract_raw_lines(file)

    # Step 2: Extract rows dynamically
    extracted_data = extract_rows(raw_lines)

    # Step 3: Save to CSV
    if not extracted_data:
        return None, "No data found in the PDF. Please verify the format."

    output_csv = "extracted_data.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "Pos.",
                "Item Code",
                "Unit",
                "Delivery Date",
                "Quantity",
                "Basic Price",
                "Discount",
                "Cur.",
                "Amount",
                "Sub Total",
            ],
        )
        writer.writeheader()
        writer.writerows(extracted_data)

    return output_csv

# Gradio interface
interface = gr.Interface(
    fn=process_pdf,
    inputs=gr.File(label="Upload PDF File"),
    outputs=[gr.File(label="Download Extracted CSV"), gr.Textbox(label="Status")],
    title="POS Data Extractor with Debugging",
    description="Upload a PDF file to extract POS data dynamically and download as CSV. Includes debugging to inspect raw data."
)

# Launch the Gradio app
if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860)

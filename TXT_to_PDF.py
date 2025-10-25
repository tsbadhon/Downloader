import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Define the directory where files are located
directory = '/storage/emulated/0/YouTube/TxT2PDF/'

# Ask the user for the text file name interactively
file_name = input("Please enter the name of the text file: ").strip()

# Check if the user entered a file name; if not, exit
if not file_name:
    print("No file name entered. Exiting.")
    sys.exit(1)

# Automatically append '.txt' if the user didn't include it
if not file_name.endswith('.txt'):
    file_name += '.txt'

# Extract the base name without the extension
base_name = os.path.splitext(file_name)[0]

# Construct the full paths for the text file and the output PDF
text_file_path = os.path.join(directory, file_name)
pdf_file_path = os.path.join(directory, base_name + '.pdf')

# Read the text file
try:
    with open(text_file_path, 'r') as file:
        lines = file.read().split('\n')
except FileNotFoundError:
    print(f"Error: File {text_file_path} not found.")
    sys.exit(1)

# Create PDF
c = canvas.Canvas(pdf_file_path, pagesize=letter)
width, height = letter

# Define a list of colors for text
color_list = [colors.blue, colors.green, colors.purple, colors.red, colors.orange, colors.brown, colors.cyan, colors.magenta]

# Set initial page number
page_num = 1

# Set margins and available width
margin = 100
available_width = width - 2 * margin

# Draw the big title on the first page
c.setFont("Helvetica-Bold", 24)
title_text = base_name
c.drawCentredString(width / 2, height - 50, title_text)

# Set initial y-position for text content (below the title)
y_position = height - 100
line_height = 14

# Process each line of the text file
color_index = 0
for original_line in lines:
    if original_line.strip() == "":
        # Handle empty lines by adding space
        y_position -= line_height
        if y_position < 50:
            # Add footer to current page
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, 30, f"Page {page_num}")
            c.showPage()
            page_num += 1
            # Add header for new page
            c.setFont("Helvetica", 10)
            header_text = f"{base_name} - Page {page_num}"
            c.drawString(margin, height - 30, header_text)
            y_position = height - 50
    else:
        # Assign a color to the current line
        color = color_list[color_index % len(color_list)]
        remaining_line = original_line
        while remaining_line:
            # Find substring that fits within available width
            substring = ""
            for i in range(len(remaining_line)):
                if c.stringWidth(remaining_line[:i+1], "Helvetica", 12) > available_width:
                    break
                substring = remaining_line[:i+1]
            else:
                # Entire line fits
                draw_text = remaining_line
                remaining_line = ""
            if ' ' in substring and remaining_line:
                # Break at the last space for word wrapping
                break_index = substring.rfind(' ')
                draw_text = substring[:break_index]
                remaining_line = substring[break_index+1:] + remaining_line[len(substring):]
            else:
                draw_text = substring
                remaining_line = remaining_line[len(substring):]

            # Draw the text with the assigned color
            c.setFillColor(color)
            c.setFont("Helvetica", 12)
            c.drawString(margin, y_position, draw_text)
            y_position -= line_height

            # Check if a new page is needed
            if y_position < 50:
                # Add footer to current page
                c.setFont("Helvetica", 10)
                c.drawCentredString(width / 2, 30, f"Page {page_num}")
                c.showPage()
                page_num += 1
                # Add header for new page
                c.setFont("Helvetica", 10)
                header_text = f"{base_name} - Page {page_num}"
                c.drawString(margin, height - 30, header_text)
                y_position = height - 50
        color_index += 1

# Add footer to the last page
c.setFont("Helvetica", 10)
c.drawCentredString(width / 2, 30, f"Page {page_num}")
c.save()

print(f"PDF saved to {pdf_file_path}")
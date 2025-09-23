import pandas as pd
from fpdf import FPDF
import base64
import matplotlib.pyplot as plt
from io import BytesIO
import os
import tempfile

def create_and_embed_plot(df, group_by_field, graph_type):
    """
    Generates a matplotlib plot based on the grouped data and saves it to a temporary file.
    Returns the file path.
    """
    if group_by_field and group_by_field in df.columns:
        grouped_data = df.groupby(group_by_field).size()
        fig, ax = plt.subplots()

        if graph_type == 'bar':
            grouped_data.plot(kind='bar', ax=ax, color='skyblue')
        elif graph_type == 'pie':
            grouped_data.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.set_ylabel('') # Hide y-label for pie chart
        else:
            # Default to bar chart if an unsupported type is selected
            grouped_data.plot(kind='bar', ax=ax, color='skyblue')

        ax.set_title(f'Threat Logs Grouped by {group_by_field} ({graph_type.capitalize()} Chart)')
        
        if graph_type == 'bar':
            ax.set_xlabel(group_by_field)
            ax.set_ylabel('Count')
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()

        # Save to a temporary file and return the path
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        plt.savefig(temp_file.name, format='png')
        plt.close(fig)
        return temp_file.name
    return None

def generate_report_with_graphs(df, group_by_field, graph_type):
    """
    Generates a PDF report with embedded graphs from temporary files.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Comprehensive Threat Report', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Data Summary', 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 5, f"Total log entries: {len(df)}")
    pdf.multi_cell(0, 5, f"Report generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.ln(5)

    plot_path = None
    if group_by_field:
        plot_path = create_and_embed_plot(df, group_by_field, graph_type)
        if plot_path:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f'Threat Log Visualization ({group_by_field})', 0, 1)
            pdf.image(plot_path, x=15, w=180)
            pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Raw Log Data', 0, 1)
    pdf.set_font("Arial", '', 8)
    for index, row in df.iterrows():
        pdf.multi_cell(0, 4, f"Entry {index+1}: {row['log_message']}")

    pdf_output = pdf.output(dest='S').encode('latin-1')

    # Clean up the temporary file
    if plot_path and os.path.exists(plot_path):
        os.remove(plot_path)

    return pdf_output

def get_download_link(pdf_output):
    """
    Generates a download link for the PDF file.
    """
    b64 = base64.b64encode(pdf_output).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="threat_report.pdf">Download PDF Report</a>'
    return href

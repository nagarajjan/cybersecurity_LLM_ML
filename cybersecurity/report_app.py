import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64

def generate_simple_report(df, selected_criteria):
    """
    Generates a simple PDF report based on selected criteria from a DataFrame.
    """
    st.info(f"Generating report for entries matching criteria: {selected_criteria}...")

    # Filter the DataFrame based on the selected criteria
    if selected_criteria:
        # Assuming criteria is a column name for simplicity in this example
        # In a real app, this would involve more complex filtering logic
        if selected_criteria in df.columns:
             filtered_df = df[df[selected_criteria].notna()] # Example: filter non-empty values in the criteria column
        else:
             st.warning(f"Criteria column '{selected_criteria}' not found. Generating report for all data.")
             filtered_df = df
    else:
        filtered_df = df

    if filtered_df.empty:
        return "No data found matching the selected criteria to report on."

    # Initialize PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Generated Data Report', 0, 1, 'C')
    pdf.set_font("Arial", '', 12)

    # Add data to PDF
    for index, row in filtered_df.iterrows():
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Entry {index + 1}", 0, 1)
        pdf.set_font("Arial", '', 10)
        for col, value in row.items():
             pdf.multi_cell(0, 5, f"{col}: {value}")
        pdf.ln(5)

    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

# --- Streamlit App ---
st.title("📄 Report Generator")
st.markdown("Upload a CSV file and generate a report based on selected criteria.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.header("Uploaded Data Preview")
        st.sidebar.dataframe(df.head())

        st.subheader("Generate Report")
        st.info("Select criteria and generate a PDF report.")

        # Example: Allow user to select a column as criteria
        if not df.empty:
            available_columns = df.columns.tolist()
            selected_criteria_column = st.selectbox("Select criteria column (optional):", ["None"] + available_columns)
            criteria_to_use = selected_criteria_column if selected_criteria_column != "None" else None

            if st.button("Generate Report"):
                with st.spinner("Generating report..."):
                    pdf_output = generate_simple_report(df, criteria_to_use)
                    st.success("Report generated successfully!")

                    if isinstance(pdf_output, bytes):
                        # Create a download button for the generated PDF
                        b64 = base64.b64encode(pdf_output).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="generated_report.pdf">Download PDF Report</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    else:
                        st.info(pdf_output) # Display message if no data found
        else:
            st.warning("Uploaded CSV is empty.")

    except Exception as e:
        st.error(f"Error processing file: {e}")



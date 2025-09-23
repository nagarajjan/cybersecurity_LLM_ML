import streamlit as st
import pandas as pd
import os
import sys

# Add the project directory to the Python path to enable local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_pipeline_ml import load_data, preprocess_logs, DATA_DIR, FILE_PATH
from llm_threat_analyzer_st import setup_llm_rag, analyze_threat
from report_generator import generate_report_with_graphs, get_download_link

st.title("🛡️ Threat Intelligence and Analysis")
st.markdown("Use this interface to analyze threats from security logs using a powerful LLM-based RAG system.")

try:
    df_raw = load_data(FILE_PATH)
    df_processed = preprocess_logs(df_raw)

    if 'source_ip' not in df_processed.columns:
        st.error("Error: The 'source_ip' column was not created during preprocessing.")
        st.info("Check `data_pipeline_ml.py` and `threat_logs.csv` to ensure the log format is consistent.")
    else:
        source_ips = df_processed['source_ip'].unique()

        st.sidebar.header("Threat Log Data")
        st.sidebar.dataframe(df_processed)

        if len(source_ips) > 0:
            with st.form("threat_form"):
                st.subheader("Analyze a Specific Threat")
                selected_ip = st.selectbox("Select a Source IP:", source_ips)
                threat_type = st.text_input("Enter Threat Type:", value="brute_force")
                target_details = st.text_input("Enter Target Details:", value="admin account")
                submit_button = st.form_submit_button("Analyze Threat")

            if submit_button:
                alert_details = f"Threat type: {threat_type}, Source IP: {selected_ip}, Target: {target_details}."
                try:
                    with st.spinner("Setting up RAG system and analyzing threat..."):
                        rag_engine = setup_llm_rag()
                        analyze_threat(rag_engine, alert_details)
                        st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
                    st.warning("Ensure Ollama is running and the Llama 3 and embedding models are installed.")
                    st.info("Please run `ollama serve` and `ollama pull llama3` in your terminal.")

            st.markdown("---")
            st.subheader("Generate Complete Log Report")
            
            # Options for grouping and graph type
            report_group_by = st.selectbox("Group report graph by:", ["None", "source_ip", "threat_type", "user"])
            graph_type = st.selectbox("Select graph type:", ["bar", "pie"])

            if st.button("Generate Complete Report"):
                with st.spinner("Generating full report with graphs..."):
                    pdf_output = generate_report_with_graphs(df_processed, report_group_by, graph_type)
                    download_link = get_download_link(pdf_output)
                    st.markdown(download_link, unsafe_allow_html=True)
                    st.success("Report generated and ready for download!")
        else:
            st.warning("No source IPs found in the data after preprocessing.")

except FileNotFoundError as e:
    st.error(e)
    st.warning("Please ensure you have a 'data' directory with 'threat_logs.csv' inside.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
    st.warning("Check your `data_pipeline_ml.py` and `threat_logs.csv` file for consistency.")

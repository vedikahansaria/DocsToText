import streamlit as st
import os
import tempfile
from markitdown import MarkItDown

# --- Page Configuration ---
st.set_page_config(
    page_title="Universal Doc Converter",
    page_icon="📄",
    layout="centered"
)

# --- App Title & Description ---
st.title("📄 Universal Document Reader")
st.markdown("""
    Convert **Word, Excel, PowerPoint, PDF, and HTML** files into clean **Markdown** or **Text**.
    Simply drag and drop your files below.
""")

# --- Helper Function: Save Uploaded File to Temp ---
def save_uploaded_file(uploaded_file):
    """
    Saves the uploaded streamlit file to a temporary file on disk.
    """
    try:
        _, file_extension = os.path.splitext(uploaded_file.name)
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# --- Helper Function: Format File Size ---
def format_size(size_in_bytes):
    """
    Converts bytes to readable formats (KB, MB).
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

# --- Main Logic ---

# 1. File Uploader
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=['docx', 'xlsx', 'pptx', 'pdf', 'html', 'txt', 'csv', 'json', 'xml'], 
    accept_multiple_files=True
)

if uploaded_files:
    # Initialize the Engine
    md = MarkItDown()

    st.write("---")
    st.subheader("📝 Conversion Results")

    for uploaded_file in uploaded_files:
        # Create an expander for each file
        with st.expander(f"File: {uploaded_file.name}", expanded=True):
            
            # Save to temp disk
            temp_path = save_uploaded_file(uploaded_file)
            
            if temp_path:
                try:
                    with st.spinner(f"Converting {uploaded_file.name}..."):
                        
                        # --- THE ENGINE: Convert ---
                        result = md.convert(temp_path)
                        text_content = result.text_content

                        # --- CALCULATIONS: Size Comparison ---
                        # 1. Get original size from the temp file on disk
                        original_size = os.path.getsize(temp_path)
                        
                        # 2. Get converted size (length of string in bytes)
                        converted_size = len(text_content.encode('utf-8'))
                        
                        # 3. Calculate percentage reduction
                        if original_size > 0:
                            reduction_percent = ((original_size - converted_size) / original_size) * 100
                        else:
                            reduction_percent = 0

                    # --- Success UI: TABS ---
                    st.success("Conversion Successful!")
                    
                    # Create two tabs
                    tab_preview, tab_stats = st.tabs(["📄 Preview & Download", "📊 File Size Comparison"])

                    # TAB 1: PREVIEW & DOWNLOAD
                    with tab_preview:
                        st.text_area(
                            "Preview:", 
                            value=text_content, 
                            height=250,
                            key=f"preview_{uploaded_file.name}"
                        )

                        base_name = os.path.splitext(uploaded_file.name)[0]
                        md_filename = f"{base_name}_converted.md"
                        txt_filename = f"{base_name}_converted.txt"

                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="⬇️ Download Markdown (.md)",
                                data=text_content,
                                file_name=md_filename,
                                mime="text/markdown",
                                key=f"dl_md_{uploaded_file.name}"
                            )
                        with col2:
                            st.download_button(
                                label="⬇️ Download Text (.txt)",
                                data=text_content,
                                file_name=txt_filename,
                                mime="text/plain",
                                key=f"dl_txt_{uploaded_file.name}"
                            )

                    # TAB 2: FILE SIZE COMPARISON
                    with tab_stats:
                        # Create data for the table
                        data = {
                            "Metric": ["Original File Size", "Converted (.txt) Size"],
                            "Size": [format_size(original_size), format_size(converted_size)]
                        }
                        
                        # Display Table
                        st.table(data)

                        # Display Highlighted Metric
                        st.markdown(f"### 📉 Space Saved: **{reduction_percent:.1f}%**")
                        st.caption(f"The text version is {reduction_percent:.1f}% smaller than the original document.")

                except Exception as e:
                    st.error(f"⚠️ Could not read **{uploaded_file.name}**.")
                    st.error(f"Detailed Error: {e}")
                
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

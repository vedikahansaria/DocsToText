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
    Saves the uploaded streamlit file to a temporary file on disk
    so MarkItDown can read it by path.
    """
    try:
        # Get the suffix (extension) from the original file
        _, file_extension = os.path.splitext(uploaded_file.name)
        
        # Create a named temporary file (delete=False to keep it for processing)
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

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
        # Create an expander for each file to keep UI clean
        with st.expander(f"File: {uploaded_file.name}", expanded=True):
            
            # Save to temp disk
            temp_path = save_uploaded_file(uploaded_file)
            
            if temp_path:
                try:
                    # Show a spinner while processing
                    with st.spinner(f"Converting {uploaded_file.name}..."):
                        
                        # --- THE ENGINE: Convert the file ---
                        # Note: MarkItDown handles the underlying logic for supported formats
                        result = md.convert(temp_path)
                        text_content = result.text_content

                    # --- Success UI ---
                    st.success("Conversion Successful!")
                    
                    # Preview Area
                    st.text_area(
                        "Preview:", 
                        value=text_content, 
                        height=250,
                        key=f"preview_{uploaded_file.name}"
                    )

                    # Prepare Filenames for Download
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    md_filename = f"{base_name}_converted.md"
                    txt_filename = f"{base_name}_converted.txt"

                    # Download Buttons (Columns for layout)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="⬇️ Download as Markdown (.md)",
                            data=text_content,
                            file_name=md_filename,
                            mime="text/markdown",
                            key=f"dl_md_{uploaded_file.name}"
                        )
                    
                    with col2:
                        st.download_button(
                            label="⬇️ Download as Text (.txt)",
                            data=text_content,
                            file_name=txt_filename,
                            mime="text/plain",
                            key=f"dl_txt_{uploaded_file.name}"
                        )

                except Exception as e:
                    # --- Error Handling ---
                    st.error(f"⚠️ Could not read **{uploaded_file.name}**. Please check the format.")
                    # Optional: Print actual error to console for debugging
                    print(f"Error processing {uploaded_file.name}: {e}")
                
                finally:
                    # Cleanup: Remove the temp file from disk
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

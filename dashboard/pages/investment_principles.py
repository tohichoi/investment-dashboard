from pathlib import Path
import streamlit as st


def load_markdown_file(file_path: Path):
    """지정된 경로의 마크다운 파일을 로드하여 Streamlit에 표시합니다."""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
            st.markdown(markdown_content, unsafe_allow_html=True)
    else:
        st.error(f"파일을 찾을 수 없습니다: {file_path}")

def investment_principles_index():
    p = Path(__file__).parent.parent / 'data' / 'documents' / 'Investment Principles.md'
    load_markdown_file(p)


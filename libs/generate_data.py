import time
import requests

import pandas as pd
import streamlit as st
import os
import re
import zipfile
import os
import streamlit as st
from libs.common import run_command
from libs.config import generate_data_vision, generate_data_vision_ocr, generate_data_vision_di
from theodoretools.url import url_to_name


def create_zip(directory, output_path):
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith('.txt'):
                    filepath = os.path.join(foldername, filename)
                    zipf.write(filepath, os.path.relpath(filepath, directory))


def generate_data(rag_version: str):
    st.markdown(f"## Attention")
    st.markdown(f"- Do not process txt files")
    st.markdown(f"- PDF will be converted to txt")
    st.markdown(f"- xlsx/csv will be converted to txt")
    st.markdown(f"- If xlsx/csv contains a `doc_url` column, the relevant files will be automatically downloaded, and xlsx/csv itself will be excluded")
    
    st.markdown(f"--------------")
    options = [
        generate_data_vision,
        generate_data_vision_ocr,
        generate_data_vision_di
        ]
    pdf_vision_option = st.radio('Please select a method to process the PDF:',
                                 key=f"db_{rag_version}",
                                 options=options)

    if st.button('Start Generate' , key=f"generate_btn_{rag_version}"):
        for root, dirs, files in os.walk(f"/app/projects/{rag_version}/original"):
            for file in files:
                file_path = os.path.join(root, file)
                prepare_file(file_path, file, rag_version)
        for root, dirs, files in os.walk(f"/app/projects/{rag_version}/input"):
            for file in files:
                file_path = os.path.join(root, file)
                convert_file(file_path, file, rag_version, pdf_vision_option)
        st.success("Data generated successfully.")

    st.markdown(f"--------------")
    if st.button("Download generated files", key=f"downloads_input_files_{rag_version}"):
        directory_to_zip = f'/app/projects/{rag_version}/input'
        output_zip_path = f'/tmp/{rag_version}.zip'
        create_zip(directory_to_zip, output_zip_path)
        with open(output_zip_path, "rb") as f:
            st.download_button(
                label="Download",
                data=f,
                file_name=f"{rag_version}.zip",
                mime="application/zip"
            )
        
    if st.button("Clear generated files", key=f"delete_all_input_files_{rag_version}"):
        run_command(f"rm -rf /app/projects/{rag_version}/input/*")
        time.sleep(3)
        st.success("All files deleted.")

    if st.button("Clear PDF cached files", key=f"delete_all_cached_files_{rag_version}"):
        run_command(f"rm -rf /app/projects/{rag_version}/pdf_cache/*")
        time.sleep(3)
        st.success("All files deleted.")


def convert_file(file_path, file, rag_version, pdf_vision_option):
    
    if file.endswith('.xlsx') or file.endswith('.csv'):
        st.write(f"converting {file}")
        excel_to_txt(file_path, rag_version)

    if file.endswith('.pdf'):
        st.write(f"converting {file}")
        pdf_to_txt(file_path, rag_version, pdf_vision_option)
    

def excel_to_txt(file_path, rag_version):
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as file:
        excel_data = pd.ExcelFile(file.read())
        with open(f"/app/projects/{rag_version}/input/{file_name}.txt", 'w', encoding='utf-8') as f:
            for sheet_name in excel_data.sheet_names:
                f.write(f"{sheet_name}\n\n") 
                df = excel_data.parse(sheet_name)
                for index, row in df.iterrows():
                    for column in df.columns:
                        if not row[column]:
                            continue
                        f.write(f"【{column}】: {row[column]} ") 
                    f.write(f"\n\n") 


def prepare_file(file_path, file, rag_version):
        if file.endswith('.xlsx') or file.endswith('.csv'):
            if has_download_files(file_path):
                download_files_from_xlsx_csv(file_path, file, rag_version)
            else:
                run_command(f"cp -r '{file_path}' /app/projects/{rag_version}/input/")

        if file.endswith('.txt'):
            run_command(f"cp -r '{file_path}' /app/projects/{rag_version}/input/")

        if file.endswith('.pdf'):
            run_command(f"cp -r '{file_path}' /app/projects/{rag_version}/input/")

        # if file.endswith('.zip'):
        #     deal_zip(file_path, rag_version)


def has_download_files(file_path: str):
    if not file_path.endswith('.xlsx') and not file_path.endswith('.csv'):
        return False

    with open(file_path, "rb") as f:
        df = pd.read_excel(f.read())
        with st.spinner(f"Processing ..."):
            for index, row in df.iterrows():
                if 'doc_url' in row:
                    return True
    return False


def download_files_from_xlsx_csv(file_path, file, rag_version):
    if not file_path.endswith('.xlsx') and not file_path.endswith('.csv'):
        return

    with open(file_path, "rb") as f:
        df = pd.read_excel(f.read())
        st.write(df)
        df_count = len(df) - 1
        with st.spinner(f"Processing ..."):
            for index, row in df.iterrows():
                if 'doc_url' in row:
                    doc_url = row['doc_url']
                    download_file(doc_url, index, df_count, rag_version)


def download_file(doc_url, index, df_count, rag_version):
    file_name = url_to_name(doc_url)
    os.makedirs(f"/app/projects/{rag_version}/input", exist_ok=True)     
    file_path = os.path.join(f"/app/projects/{rag_version}/input", file_name)  

    if os.path.exists(file_path):
        st.write(f"[{index}/{df_count}] File already exists: {file_path}")
        return

    st.write(f"[{index}/{df_count}] Downloading {doc_url}")

    try:
        response = requests.get(doc_url, stream=True)
        response.raise_for_status() 
       
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        st.write(f"[{index}/{df_count}] Downloaded: {file_path}")
    except requests.RequestException as e:
        st.write(f"[{index}/{df_count}] Downloaded Error: {e}")


def pdf_to_txt(pdf_path:str, rag_version:str, pdf_vision_option):
    import libs.pdf_txt as pdf_txt

    try:
        pdf_txt.save_pdf_pages_as_images(pdf_path, rag_version, pdf_vision_option)
        st.write(f"PDF to txt {pdf_path}")
    except Exception as e:
        st.error(f"PDF to txt error: {pdf_path} \n {e}")


def replace_image_tag(match):
    image_path = match.group(1)
    file_path = f"{image_path}.desc"

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            return f"此处是文本插图：{content}"

    return match.group(1)


def replace_classify(markdown_text: str):
    markdown_pattern = r'!\[.*?\]\((.*?)\)'
    html_pattern = r'<img .*?src="(.*?)".*?>'
    markdown_text = re.sub(markdown_pattern, replace_image_tag, markdown_text)
    markdown_text = re.sub(html_pattern, replace_image_tag, markdown_text)
    return markdown_text


def download_image(image_url, output_dir, image_index):
    image_extension = image_url.split('.')[-1].split('?')[0]

    image_extension = image_extension.replace(',', '')
    image_extension = image_extension.replace('&', '')
    image_extension = image_extension.replace('=', '')
    image_extension = image_extension.replace('.', '')

    image_filename = f'image_{image_index}.{image_extension}'
    image_path = os.path.join(output_dir, image_filename)

    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(image_path, 'wb') as image_file:
            image_file.write(response.content)
        return image_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_url}: {e}")
        return None


def read_pdf(file_path):
    import PyPDF2
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

import logging
import time
import tracemalloc
import streamlit as st
import zipfile
import os
import re
import base64
from dotenv import load_dotenv
from streamlit.runtime.uploaded_file_manager import UploadedFile

from libs.common import get_original_dir, list_files_and_sizes, run_command
from pathlib import Path
from  libs.common import debug

tracemalloc.start()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()


def list_uploaded_files(container, project_name: str):
    files = list_files_and_sizes(get_original_dir(project_name))
    if len(files) > 0:
        container = container.container(border=True)
        container.write(f"Files uploaded `{len(files)}`")
        container.write(files)


def upload_file(project_name: str):
    
    file_list_container = st.empty()

    st.info(f"Tip: The same file name will be overwritten.")
    uploaded_files = st.file_uploader(
        label="upload",
        type=[
            'pdf',
            'txt',
            'xlsx',
            'csv',
            'md',
                # 'jpeg',
                # 'jpg',
                # 'png',
            ],
        accept_multiple_files=True,
        label_visibility="hidden",
        key=f"file_uploader_{project_name}",
    )
    
    if st.button("Delete all files", key=f"delete_all_files_{project_name}", icon="🗑️"):
        run_command(f"rm -rf /app/projects/{project_name}/original/*")
        time.sleep(3)
        st.success("All files deleted.")
        list_uploaded_files(file_list_container, project_name)
    
    list_uploaded_files(file_list_container, project_name)

    if len(uploaded_files) > 0:
        debug(uploaded_files)
        
        Path(f"/app/projects/{project_name}/original").mkdir(parents=True, exist_ok=True)
        Path(f"/app/projects/{project_name}/input").mkdir(parents=True, exist_ok=True)
                
        for uploaded_file in uploaded_files:
            with open(f"/app/projects/{project_name}/original/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.read())
                # make file permissions to another user can write
                os.chmod(f"/app/projects/{project_name}/original/{uploaded_file.name}", 0o666)

        list_uploaded_files(file_list_container, project_name)
        st.success('File uploaded successfully.')


def deal_zip(uploaded_file: UploadedFile, session_id: str):
    extract_dir = f'/tmp/{session_id}/input/'
    if uploaded_file is not None:

        # Ensure the extraction directory exists
        os.makedirs(extract_dir, exist_ok=True)

        # Unzip the file directly from the upload buffer
        with zipfile.ZipFile(uploaded_file) as zip_ref:
            zip_ref.extractall(extract_dir)

        # List extracted files
        files = os.listdir(extract_dir)
        for f in files:
            if f.endswith(".md"):
                deal_md(extract_dir, f)


def deal_md(extract_dir, file_name):
    file_path = f"{extract_dir}{file_name}"
    with open(file_path, 'r') as file:
        md_content = file.read()

        with st.expander(f"{file_path} Original"):
            st.text(md_content)

        updated_md_content = extract_images_from_md(md_content, extract_dir)
        updated_md_content = replace_classify(updated_md_content)

        new_file = f"{file_path}.txt"
        with open(new_file, 'w', encoding='utf-8') as md_file:
            md_file.write(updated_md_content)
            with st.expander(f"{new_file} New"):
                st.text(updated_md_content)


def extract_images_from_md(md_content, extract_dir):
    markdown_image_pattern = r'!\[.*?\]\((.*?)\)'
    html_image_pattern = r'<img\s+.*?src=["\'](.*?)["\']'

    markdown_matches = re.findall(markdown_image_pattern, md_content)
    html_matches = re.findall(html_image_pattern, md_content)

    all_matches = markdown_matches + html_matches

    Path(extract_dir).mkdir(parents=True, exist_ok=True)

    updated_md_content = md_content
    for match in all_matches:
        if match.startswith('data:image'):
            base64_pattern = r'data:image/(.*?);base64,(.*)'
            image_format, base64_data = re.findall(base64_pattern, match)[0]
            image_data = base64.b64decode(base64_data)
            image_filename = f'image_{all_matches.index(match) + 1}.{image_format}'
            image_path = os.path.join(extract_dir, image_filename)
            with open(image_path, 'wb') as image_file:
                image_file.write(image_data)
                rek_image(image_path)
                updated_md_content = updated_md_content.replace(match, image_path)
        elif match.startswith('http') or match.startswith('https'):
            image_path = download_image(match, extract_dir, all_matches.index(match) + 1)
            if image_path:
                rek_image(image_path)
                updated_md_content = updated_md_content.replace(match, image_path)
        else:
            image_path = match
            if not match.startswith(extract_dir):
                image_path = f"{extract_dir}{match}"
            rek_image(image_path)
            updated_md_content = updated_md_content.replace(match, image_path)

    return updated_md_content


def get_image_description(client, encoded_string, image_extension, prompt, model_choice):
    response = client.chat.completions.create(
        model=model_choice,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{image_extension};base64,{encoded_string}"}
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content


def rek_image(image_path: str):
    image_classifying_path = f"{image_path}.desc"

    # if image_classifying_path exists, then open it content as string
    if os.path.exists(image_classifying_path):
        with open(image_classifying_path, 'r') as image_file:
            return image_file.read()

    if not os.path.exists(image_path):
        st.write(f"Image not found: {image_path}")
        return ""

    image_extension = image_path.split('.')[-1].split('?')[0]
    with open(image_path, 'rb') as image_file:
        with st.spinner(f'Classifying {image_path} ...'):
            image_data = image_file.read()

            encoded_string = base64.b64encode(image_data).decode('utf-8')
            if encoded_string:
                try:
                    description = get_image_description(
                        client,
                        encoded_string,
                        image_extension,
                        'What’s in this image? please use chinese.',
                        "gpt-4o")

                    # with st.expander(f"{image_path} Description"):
                    #     st.image(image_path, width=450, caption=description)
                    #     sleep(3)

                    # write description to image_classifying_path
                    with open(image_classifying_path, 'w') as t_file:
                        t_file.write(description)

                    return description
                except Exception as e:
                    st.error(f"Error: {e}")

    return ""


import fitz
from openai import AzureOpenAI
import os
import base64
import streamlit as st
from libs.blob import upload_file
from libs.save_settings import get_setting_file
import libs.config as config
import concurrent.futures
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

client = AzureOpenAI(
    api_version=config.data_azure_api_version,
    azure_endpoint=config.data_azure_api_base,
    azure_deployment=config.data_azure_chat_deployment_name,
    api_key=config.data_azure_api_key,
)


def image_to_base64(image_path:str):
    with open(image_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_encoded


class PageTask:

    def __init__(self, doc, pdf_path, project_name, pdf_vision_option, page_num):
        self.doc = doc
        self.pdf_name = os.path.basename(pdf_path)
        self.project_name = project_name
        self.pdf_vision_option = pdf_vision_option
        self.pdf_vision_option_format = pdf_vision_option.replace(" ", "")
        self.base_name = f"/app/projects/{project_name}/pdf_cache"
        self.img_path = f"{self.base_name}/{self.pdf_name}_page_{page_num + 1}.png"
        self.txt_path = f"{self.base_name}/{self.pdf_name}_page_{page_num + 1}.png.txt"
        self.ai_txt_path = f"{self.base_name}/{self.pdf_name}_page_{page_num + 1}.png.{self.pdf_vision_option_format}.txt"
        self.page_num = page_num
    
    def page_to_image(self):
        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap(dpi=150)
        pix.save(self.img_path)
        upload_file(self.project_name, self.img_path)

    def page_to_txt(self):
        page_txt = self.doc[self.page_num].get_text("text")
        # with open(self.txt_path, "w") as txt_file:
        #     txt_file.write(page_txt)
        #     st.write(f"[{self.page_num}/{self.doc.page_count}] {self.txt_path}")
        return page_txt
    
    def get_ai_txt(self):
        # use cache if exists
        if os.path.exists(self.ai_txt_path):
            with open(self.ai_txt_path, "r") as f:
                return "", f.read()

        self.page_to_image()
        
        prompt, ai_txt = "", ""
        
        try:
            if self.pdf_vision_option == config.generate_data_vision:
                prompt, ai_txt = self.gpt_vision_txt()
            
            if self.pdf_vision_option == config.generate_data_vision_txt:
                prompt, ai_txt = self.gpt_vision_txt_by_txt()
            
            if self.pdf_vision_option == config.generate_data_vision_image:
                prompt, ai_txt = self.gpt_vision_txt_by_image()

            if self.pdf_vision_option == config.generate_data_vision_azure:
                prompt, ai_txt = self.gpt_vision_txt_azure()
                
            if self.pdf_vision_option == config.generate_data_vision_di:
                ai_txt = di_analyze_read(self.img_path)
        
            # set cache
            with open(self.ai_txt_path, "w") as txt_file:
                txt_file.write(ai_txt)
                st.write(f"[{self.page_num}/{self.doc.page_count}] {self.ai_txt_path}")
        except Exception as e:
            st.warning(f"[{self.page_num}/{self.doc.page_count}] `{self.pdf_name}` generated an exception: {e}")
        
        return prompt, ai_txt

    def gpt_vision_txt_azure(self):
        base64_string = image_to_base64(self.img_path)

        prompt = config.pdf_gpt_vision_prompt_azure.format(page_txt=self.page_to_txt())

        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                                "url": f"data:image/png;base64,{base64_string}" ,
                            }
                        },
                    ]
                }
                
            ],
            model=config.azure_chat_model_id,
        )
        ai_txt = completion.choices[0].message.content

        return prompt, ai_txt

    def gpt_vision_txt(self):
        base64_string = image_to_base64(self.img_path)
        settings_file = f"/app/projects/{self.project_name}/prompts/pdf_gpt_vision_prompt.txt"
        prompt = get_setting_file(settings_file, config.pdf_gpt_vision_prompt).format(page_txt=self.page_to_txt())

        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                                "url": f"data:image/png;base64,{base64_string}" ,
                            }
                        },
                    ]
                }
                
            ],
            model=config.azure_chat_model_id,
        )
        ai_txt = completion.choices[0].message.content

        return prompt, ai_txt

    def gpt_vision_txt_by_txt(self):
        base64_string = image_to_base64(self.img_path)
        settings_file = f"/app/projects/{self.project_name}/prompts/pdf_gpt_vision_prompt_by_text.txt"
        prompt = get_setting_file(settings_file, config.pdf_gpt_vision_prompt_by_text).format(page_txt=self.page_to_txt())

        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                            "url": f"data:image/png;base64,{base64_string}" ,
                        }
                    },
                    ]
                }
                
            ],
            model=config.azure_chat_model_id,
        )
        ai_txt = completion.choices[0].message.content

        return prompt, ai_txt

    def gpt_vision_txt_by_image(self):
        base64_string = image_to_base64(self.img_path)
        
        settings_file = f"/app/projects/{self.project_name}/prompts/pdf_gpt_vision_prompt_by_image.txt"
        prompt = get_setting_file(settings_file, config.pdf_gpt_vision_prompt_by_image).format(page_txt=self.page_to_txt())
        
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                            "url": f"data:image/png;base64,{base64_string}" ,
                        }
                    },
                    ]
                }
                
            ],
            model=config.azure_chat_model_id,
        )
        ai_txt = completion.choices[0].message.content

        return prompt, ai_txt

    
def save_pdf_pages_as_images(pdf_path:str, project_name:str, pdf_vision_option: str):
    pdf_file_name = os.path.basename(pdf_path)
    pdf_ai_txt_path = f"{pdf_path}.{pdf_vision_option.replace(" ", "")}.txt"
    base_dir = f"/app/projects/{project_name}/pdf_cache"
    os.makedirs(base_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    
    upload_file(project_name, pdf_path)

    def process_page(page_num):
        pt = PageTask(doc, pdf_path, project_name, pdf_vision_option, page_num)
        return pt.get_ai_txt()
    
    # get txt by parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_page = {executor.submit(process_page, page_num): page_num for page_num in range(doc.page_count)}
        for future in concurrent.futures.as_completed(future_to_page):
            page_num = future_to_page[future]
            try:
                future.result()
                st.write(f"[{page_num}/{doc.page_count}] `{pdf_file_name}` done")
            except Exception as exc:
                st.warning(f"[{page_num}/{doc.page_count}] `{pdf_file_name}` generated an exception: {exc}")

    # write full txt by order
    with open(pdf_ai_txt_path, "w") as f:
        f.write("\n")

    for page_num in range(doc.page_count):
        pt = PageTask(doc, pdf_path, project_name, pdf_vision_option, page_num)
        with open(pdf_ai_txt_path, "a") as f:
            f.write("\n\n")
            prompt, ai_txt = pt.get_ai_txt()
            if ai_txt:
                f.write(ai_txt)


def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])


def di_analyze_read(img_path: str):

    endpoint = config.di_url
    key = config.di_key

    # open the file
    with open(img_path, "rb") as file:
        file_data = file.read()

        # print(file_data)

        document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(key)
        )
        
        poller = document_analysis_client.begin_analyze_document(
                "prebuilt-read",
                document=file_data
                )
        result = poller.result()
        
        for idx, style in enumerate(result.styles):
            print(
                "Document contains {} content".format(
                    "handwritten" if style.is_handwritten else "no handwritten"
                )
            )

        for page in result.pages:
            print("----Analyzing Read from page #{}----".format(page.page_number))
            print(
                "Page has width: {} and height: {}, measured with unit: {}".format(
                    page.width, page.height, page.unit
                )
            )

            for line_idx, line in enumerate(page.lines):
                print(
                    "...Line # {} has text content '{}' within bounding box '{}'".format(
                        line_idx,
                        line.content,
                        format_bounding_box(line.polygon),
                    )
                )

            for word in page.words:
                print(
                    "...Word '{}' has a confidence of {}".format(
                        word.content, word.confidence
                    )
                )

        print("====================================")
        return result.content

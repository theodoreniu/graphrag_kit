import fitz
from PIL import Image
from openai import AzureOpenAI
import os
import base64
import streamlit as st
import libs.config as config
import concurrent.futures
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

client = AzureOpenAI(
    api_version=config.azure_api_version,
    azure_endpoint=config.azure_api_base,
    azure_deployment=config.azure_chat_deployment_name,
    api_key=config.azure_api_key,
)

def image_to_base64(image_path:str):
    with open(image_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_encoded

class PageTask:
    def __init__(self,doc,pdf_path, rag_version, pdf_vision_option, page_num):
        self.doc =doc
        self.pdf_name = os.path.basename(pdf_path)
        self.rag_version = rag_version   
        self.pdf_vision_option = pdf_vision_option
        self.pdf_vision_option_foramt = pdf_vision_option.replace(" ", "")
        self.base_name = f"/app/index/{config.tenant_name}/{rag_version}/pdf_cache"
        self.img_path = f"{self.base_name}/{self.pdf_name}_page_{page_num + 1}.png"
        self.txt_path = f"{self.base_name}/{self.pdf_name}_page_{page_num + 1}.png.txt"
        self.ai_txt_path = f"{self.base_name}/{self.pdf_name}_page_{page_num + 1}.png.{self.pdf_vision_option_foramt}.txt"
        self.page_num = page_num
    
    def page_to_image(self):
        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap(dpi=150)
        pix.save(self.img_path)
        return self.img_path

    def page_to_txt(self):
        page_txt = self.doc[self.page_num].get_text("text")
        with open(self.txt_path, "w") as txt_file:
            txt_file.write(page_txt )
            st.write(f"[{self.page_num}/{self.doc.page_count}] {self.txt_path}")
        return page_txt
    
    def page_to_txt_vision(self):
        return fix_txt_postion(self.img_path, self.page_to_txt())

    def page_to_txt_di(self):
        return analyze_read(self.img_path)
    
    def get_ai_txt(self):
        if os.path.exists(self.ai_txt_path):
            with open(self.ai_txt_path, "r") as f:
                return f.read()

        self.page_to_image()

        if self.pdf_vision_option.startswith("Azure AI Document Intelligence"):
            ai_txt = self.page_to_txt_di()
        else:
            ai_txt = self.page_to_txt_vision()

        with open(self.ai_txt_path, "w") as txt_file:
            txt_file.write(ai_txt)
            st.write(f"[{self.page_num}/{self.doc.page_count}] {self.ai_txt_path}")
        
        return ai_txt
    
def save_pdf_pages_as_images(pdf_path:str, rag_version:str, pdf_vision_option):
    pdf_ai_txt_path = f"{pdf_path}.txt"
    base_dir = f"/app/index/{config.tenant_name}/{rag_version}/pdf_cache"
    os.makedirs(base_dir, exist_ok=True)

    doc = fitz.open(pdf_path)

    def process_page(page_num):
        pt = PageTask(doc, pdf_path, rag_version, pdf_vision_option, page_num)
        return pt.get_ai_txt()
    
    # get txt by parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_page = {executor.submit(process_page, page_num): page_num for page_num in range(doc.page_count)}
        for future in concurrent.futures.as_completed(future_to_page):
            page_num = future_to_page[future]
            try:
                future.result()
                st.write(f"[{page_num}/{doc.page_count}] done")
            except Exception as exc:
                st.warning(f"[{page_num}/{doc.page_count}] generated an exception: {exc}")

    # write full txt by order
    with open(pdf_ai_txt_path, "w") as f:
        f.write("\n")

    for page_num in range(doc.page_count):
        pt = PageTask(doc, pdf_path, rag_version, pdf_vision_option, page_num)
        with open(pdf_ai_txt_path, "a") as f:
            f.write("\n\n")
            f.write(pt.get_ai_txt())


def fix_txt_postion(img_path: str, page_txt: str):
    base64_string = image_to_base64(img_path)
    
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                "type": "text", 
                "text": f"我给你一张截图，是一个产品使用说明书的pdf的某一页的截图，同时，我把这个截图里的所有文字也给你，但是文字的排版和位置可能是错乱的，不是人类阅读产品手册的顺序和位置，但是文字是没有错误的没有多余的。 请你运用视觉能力，全面的观察分析这个截图的每一处排版和每一块文字，然后把文字还原成有结构的、位置正确的文本。把文字放在该放的段落里，也就是人类阅读顺序的位置里。你一定不要增加其他任何的文字，也不要自己创造。一定不要生成任何多余的文字(甚至不要返回你做了什么，你一定只需要返回整理之后的文字)。总之，你要分析图像，然后把没有结构的散乱的文字还原成有结构的文字。 一定不要生成原始文字里没有的文字或者句子。截图里的所有原始文字如下：\n\n {page_txt}"
            },
            {
                "type": "image_url",
                "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_string}" ,
                    }
                },
                ]
            }
            
        ],
        model=config.azure_chat_model_id,
    )
    ai_txt = completion.choices[0].message.content
    print(ai_txt)

    return ai_txt


def format_bounding_box(bounding_box):
    if not bounding_box:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in bounding_box])


def analyze_read(img_path: str):

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


    return ""
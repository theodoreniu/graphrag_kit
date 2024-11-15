import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app_version = "0.0.7"
graphrag_version = "0.4.1"
app_started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
app_name = os.getenv('APP_NAME', 'graphrag')
app_tip = os.getenv('APP_TIP', '')

is_debug = os.getenv('DEBUG_MODE') == 'true'
api_key = os.getenv('API_KEY', 'api_key')
update_time = os.getenv('UPDATE_TIME', time.strftime("%Y-%m-%d %H:%M:%S"))

azure_api_key = os.getenv('AZURE_API_KEY', '')
azure_api_base = os.getenv('AZURE_API_BASE', '')
azure_api_version = os.getenv('AZURE_API_VERSION', '')
azure_chat_model_id = os.getenv('AZURE_CHAT_MODEL_ID', 'gpt-4o-mini')
azure_chat_deployment_name = os.getenv('AZURE_CHAT_DEPLOYMENT_NAME', 'gpt-4o-mini')

azure_embedding_api_key = os.getenv('AZURE_EMBEDDING_API_KEY', '')
azure_embedding_api_base = os.getenv('AZURE_EMBEDDING_API_BASE', '')
azure_embedding_api_version = os.getenv('AZURE_EMBEDDING_API_VERSION', '')
azure_embedding_model_id = os.getenv('AZURE_EMBEDDING_MODEL_ID', 'text-embedding-3-small')
azure_embedding_deployment_name = os.getenv('AZURE_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-3-small')

data_azure_api_key = os.getenv('DATA_AZURE_API_KEY', '')
data_azure_api_base = os.getenv('DATA_AZURE_API_BASE', '')
data_azure_api_version = os.getenv('DATA_AZURE_API_VERSION', '')
data_azure_chat_model_id = os.getenv('DATA_AZURE_CHAT_MODEL_ID', 'gpt-4o-mini')
data_azure_chat_deployment_name = os.getenv('DATA_AZURE_CHAT_DEPLOYMENT_NAME', 'gpt-4o-mini')

search_azure_api_key = os.getenv('SEARCH_AZURE_API_KEY', '')
search_azure_api_base = os.getenv('SEARCH_AZURE_API_BASE', '')
search_azure_api_version = os.getenv('SEARCH_AZURE_API_VERSION', '')
search_azure_chat_model_id = os.getenv('SEARCH_AZURE_CHAT_MODEL_ID', 'gpt-4o-mini')
search_azure_chat_deployment_name = os.getenv('SEARCH_AZURE_CHAT_DEPLOYMENT_NAME', 'gpt-4o-mini')

ai_search_url = os.getenv('AI_SEARCH_URL', '')
ai_search_key = os.getenv('AI_SEARCH_KEY', '')

di_url = os.getenv('DOCUMENT_INTELLIGENCE_URL', '')
di_key = os.getenv('DOCUMENT_INTELLIGENCE_KEY', '')

disable_pgvector = os.getenv('DISABLE_PGVECTOR', False)
disable_aisearch = os.getenv('DISABLE_AI_SEARCH', False)

generate_data_vision = 'GPT Vision'
generate_data_vision_txt = 'GPT Vision (as text)'
generate_data_vision_image = 'GPT Vision (as image)'
generate_data_vision_di = 'Azure AI Document Intelligence (as image)'

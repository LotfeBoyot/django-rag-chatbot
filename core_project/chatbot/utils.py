import os
from django.conf import settings
from pypdf import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# 1. تحميل المتغيرات والـ API Key
load_dotenv()

# 2. إعداد Client DeepSeek (عشان الشات والردود)
# ده اللي كان ناقص وبيعمل Error
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# 2. إعداد موديل الـ Embedding المحلي (زي ما هو)
model = SentenceTransformer('all-MiniLM-L6-v2')

# ... (باقي الدوال get_embedding و process_file زي ما هي بالظبط متمسحش حاجة)
def get_embedding(text):
    return model.encode(text).tolist()

def process_file(file_path):
    """
    دالة ذكية بتقرأ الملف سواء كان PDF أو TXT
    """
    print(f"📂 Processing file: {file_path}")
    text = ""

    # لو الملف Text (وده الأفضل للعربي)
    if file_path.endswith('.txt'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            # لو فشل الـ utf-8 نجرب ترميز تاني
            with open(file_path, 'r', encoding='cp1256') as f:
                text = f.read()
            
    # لو الملف PDF
    elif file_path.endswith('.pdf'):
        reader = PdfReader(file_path)
        for page in reader.pages:
            extract = page.extract_text()
            if extract:
                text += extract + "\n"

    # التقطيع (Chunking)
    chunk_size = 500
    chunks = []
    
    for i in range(0, len(text), chunk_size):
        chunk_text = text[i:i+chunk_size]
        
        # تجاهل الفقرات الصغيرة أوي
        if len(chunk_text) < 30:
            continue
            
        try:
            # هنا بننادي الدالة المحلية
            vector = get_embedding(chunk_text)
            chunks.append({
                'content': chunk_text,
                'embedding': vector
            })
            print(f"✅ Processed chunk {len(chunks)}")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    return chunks
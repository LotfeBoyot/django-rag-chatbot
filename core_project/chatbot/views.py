from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import DocumentChunk
from .utils import get_embedding, client # تأكد إن utils متعدلة لـ Groq
from pgvector.django import CosineDistance
from django.shortcuts import render

@csrf_exempt
@require_POST
def chat_endpoint(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        print(f"🔍 Searching for: {user_message}")

        # 1. تحويل سؤال اليوزر لـ Vector
        user_vector = get_embedding(user_message)

        # 2. البحث الدلالي
        relevant_chunks = DocumentChunk.objects.annotate(
            distance=CosineDistance('embedding', user_vector)
        ).order_by('distance')[:3]

        context_text = "\n\n".join([chunk.content for chunk in relevant_chunks])
        
        print(f"📄 Context Found:\n{context_text[:200]}...")

        # 3. الـ Prompt (زودت حتة صغيرة عشان يرد بالعربي دايماً)
        system_prompt = f"""
        You are a helpful AI assistant for a company called Boyot (formerly TechNova).
        
        CRITICAL INSTRUCTIONS:
        1. **Language:** You must answer strictly in the SAME language as the user. 
           - If the user speaks Arabic, reply ONLY in Arabic. 
           - If the user speaks English, reply ONLY in English.
           - DO NOT use words from other languages (like Vietnamese, Russian, etc.).
           
        2. **Greeting:** If the user greets you (e.g., "Hi", "Hello", "ازيك"), answer politely and introduce yourself as "Boyot Assistant".
        
        3. **Knowledge:** Answer questions about the company based ONLY on the CONTEXT below.
           - If the answer is not in the CONTEXT, say "I don't know" (in the user's language).
        
        CONTEXT:
        {context_text}
        """

        # 4. الاتصال بـ Groq (التعديل هنا) 👇
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # 👈 ده اسم الموديل المجاني السريع
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                stream=False
            )
            bot_reply = response.choices[0].message.content
            
        except Exception as e:
            bot_reply = f"⚠️ AI Error: {str(e)}\n\n💡 Found Context:\n{context_text}"

        return JsonResponse({'response': bot_reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def chat_page(request):
    # تأكد إن المسار ده صح حسب مكان ملف الـ HTML عندك
    return render(request, 'chatbot/chat_interface.html')
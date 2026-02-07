from django.db import models
from pgvector.django import VectorField  

# 1. Document Model (To upload PDF/JSON files)
class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="File Title")
    file = models.FileField(upload_to='documents/', verbose_name="File")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 2. Document Chunk Model (The core data for AI)
class DocumentChunk(models.Model):
    # Link chunk to the original document
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    
    # The actual text text of this part
    content = models.TextField(verbose_name="Chunk Content")
    
    # The Vector is the "semantic fingerprint" of the text.
    # 1536 dimensions is standard for OpenAI models (text-embedding-3-small).
    # If we switch to another model (like generic HuggingFace), we might change this to 768.
    # embedding = VectorField(dimensions=1536)
    embedding = VectorField(dimensions=384) 

    def __str__(self):
        return f"Chunk of {self.document.title}"

# 3. Chat Session Model (To separate users/conversations)
class ChatSession(models.Model):
    # This ID will be provided by the client (Laravel) or generated here
    session_id = models.CharField(max_length=255, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id}"

# 4. Chat Message Model (Conversation History)
class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Ordering by creation time to maintain the conversation context correctly
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}..."
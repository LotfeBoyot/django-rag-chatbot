from django.contrib import admin
from .models import Document, DocumentChunk, ChatSession, ChatMessage

# 1. Document Admin
class DocumentChunkInline(admin.TabularInline):
    # This allows us to see the chunks belonging to a document directly inside the Document page
    model = DocumentChunk
    extra = 0 # Don't show empty extra rows
    readonly_fields = ('content', 'embedding') # Prevent editing chunks manually for safety

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    inlines = [DocumentChunkInline] # Show chunks inside the document page

# 2. Chat Session Admin
class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('sender', 'message', 'created_at')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'started_at')
    inlines = [ChatMessageInline] # Show messages inside the session page

# Registering the other models just in case we need to see them separately
admin.site.register(DocumentChunk)
admin.site.register(ChatMessage)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document, DocumentChunk
from .utils import process_file
import os

@receiver(post_save, sender=Document)
def create_embeddings(sender, instance, created, **kwargs):

    if created:
        print(f"New file detected: {instance.title}. Processing...")
        
        file_path = instance.file.path
    
        try:
            chunks_data = process_file(file_path)
            
            chunks_to_create = []
            for chunk in chunks_data:
                chunks_to_create.append(
                    DocumentChunk(
                        document=instance,
                        content=chunk['content'],
                        embedding=chunk['embedding']
                    )
                )
            
            DocumentChunk.objects.bulk_create(chunks_to_create)
            print(f"Successfully created {len(chunks_to_create)} chunks for {instance.title}")
            
        except Exception as e:
            print(f"Error processing file: {e}")
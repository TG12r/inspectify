from django.shortcuts import render, get_object_or_404
from .models import Category, Document
from django.db.models import Q

def index(request):
    """
    Main repository view. Lists all categories and recent documents.
    """
    categories = Category.objects.all()
    recent_docs = Document.objects.filter(is_public=True).order_by('-uploaded_at')[:5]
    
    # Simple search
    query = request.GET.get('q')
    if query:
        recent_docs = Document.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_public=True
        ).distinct()

    return render(request, 'repository/index.html', {
        'categories': categories,
        'recent_docs': recent_docs,
        'query': query
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    documents = category.documents.filter(is_public=True)
    
    return render(request, 'repository/category_detail.html', {
        'category': category,
        'documents': documents
    })

def document_detail(request, slug):
    document = get_object_or_404(Document, slug=slug)
    
    # Increment view count
    document.views += 1
    document.save()
    
    return render(request, 'repository/document_detail.html', {
        'document': document
    })

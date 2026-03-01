from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Document
from django.db.models import Q
from .forms import DocumentUploadForm, CategoryCreateForm


def _can_upload_documents(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return getattr(user, 'can_upload_repository_documents', lambda: False)()

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
        'query': query,
        'can_upload_documents': _can_upload_documents(request.user),
    })


@login_required
def upload_document(request):
    if not _can_upload_documents(request.user):
        return HttpResponseForbidden('No tienes permisos para subir documentos.')

    category_created = None

    if request.method == 'POST':
        if 'create_category' in request.POST:
            category_form = CategoryCreateForm(request.POST, prefix='cat')
            form = DocumentUploadForm(prefix='doc')

            if category_form.is_valid():
                new_category = category_form.save()
                category_created = new_category
                form = DocumentUploadForm(prefix='doc', initial={'category': new_category.pk})
                category_form = CategoryCreateForm(prefix='cat')
        else:
            form = DocumentUploadForm(request.POST, request.FILES, prefix='doc')
            category_form = CategoryCreateForm(prefix='cat')

            if form.is_valid():
                document = form.save(commit=False)
                document.uploaded_by = request.user
                document.save()
                return redirect('document_detail', slug=document.slug)
    else:
        form = DocumentUploadForm(prefix='doc')
        category_form = CategoryCreateForm(prefix='cat')

    return render(request, 'repository/upload.html', {
        'form': form,
        'category_form': category_form,
        'category_created': category_created,
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

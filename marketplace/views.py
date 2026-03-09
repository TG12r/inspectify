from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import MarketplaceItem
from .forms import MarketplaceItemForm

def marketplace_list(request):
    items = MarketplaceItem.objects.order_by('-created_at')
    return render(request, 'marketplace/list.html', {'items': items})

def marketplace_detail(request, pk):
    item = get_object_or_404(MarketplaceItem, pk=pk)
    return render(request, 'marketplace/detail.html', {'item': item})

@login_required
def marketplace_create(request):
    if request.method == 'POST':
        form = MarketplaceItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            return redirect('marketplace:detail', pk=item.pk)
    else:
        form = MarketplaceItemForm()
    return render(request, 'marketplace/create.html', {'form': form})


@login_required
def marketplace_edit(request, pk):
    item = get_object_or_404(MarketplaceItem, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = MarketplaceItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('marketplace:detail', pk=item.pk)
    else:
        form = MarketplaceItemForm(instance=item)
    return render(request, 'marketplace/create.html', {'form': form, 'edit_mode': True, 'item': item})


@login_required
def marketplace_mark_sold(request, pk):
    item = get_object_or_404(MarketplaceItem, pk=pk, seller=request.user)
    item.vendido = True
    item.save()
    return redirect('marketplace:detail', pk=item.pk)


@login_required
def my_marketplace_items(request):
    items = MarketplaceItem.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_items.html', {'items': items})

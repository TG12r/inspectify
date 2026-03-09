
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models_servicios import ServicioFreelance
from .models_valoraciones import ServicioFreelanceValoracion
from .forms_servicios import ServicioFreelanceForm
from .forms_valoraciones import ServicioFreelanceValoracionForm

def servicios_list(request):
    servicios = ServicioFreelance.objects.order_by('-creado')
    q = request.GET.get('q')
    if q:
        servicios = servicios.filter(titulo__icontains=q)
    return render(request, 'marketplace/servicios_list.html', {'servicios': servicios, 'q': q})

def servicios_detail(request, pk):
    servicio = get_object_or_404(ServicioFreelance, pk=pk)
    valoraciones = servicio.valoraciones.all()
    puede_valorar = False
    if request.user.is_authenticated and hasattr(request.user, 'pk'):
        try:
            puede_valorar = not valoraciones.filter(usuario=request.user).exists() and request.user != servicio.usuario
        except ValueError:
            # Si hay datos corruptos, ignora el error y no permite valorar
            puede_valorar = False
    if request.method == 'POST' and puede_valorar:
        form = ServicioFreelanceValoracionForm(request.POST)
        if form.is_valid():
            valoracion = form.save(commit=False)
            valoracion.servicio = servicio
            valoracion.usuario = request.user
            valoracion.save()
            messages.success(request, '¡Gracias por tu valoración!')
            return redirect('marketplace:servicios_detail', pk=servicio.pk)
    else:
        form = ServicioFreelanceValoracionForm()
    return render(request, 'marketplace/servicios_detail.html', {
        'servicio': servicio,
        'valoraciones': valoraciones,
        'form_valoracion': form if puede_valorar else None,
        'puede_valorar': puede_valorar,
    })

@login_required
def servicios_create(request):
    if request.method == 'POST':
        form = ServicioFreelanceForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.usuario = request.user
            servicio.save()
            messages.success(request, 'Servicio publicado correctamente.')
            return redirect('marketplace:servicios_detail', pk=servicio.pk)
    else:
        form = ServicioFreelanceForm()
    return render(request, 'marketplace/servicios_form.html', {'form': form})

@login_required
def servicios_edit(request, pk):
    servicio = get_object_or_404(ServicioFreelance, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = ServicioFreelanceForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado.')
            return redirect('marketplace:servicios_detail', pk=servicio.pk)
    else:
        form = ServicioFreelanceForm(instance=servicio)
    return render(request, 'marketplace/servicios_form.html', {'form': form, 'edit_mode': True, 'servicio': servicio})

@login_required
def mis_servicios(request):
    servicios = ServicioFreelance.objects.filter(usuario=request.user).order_by('-creado')
    return render(request, 'marketplace/mis_servicios.html', {'servicios': servicios})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q

from .models import Connection
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def send_request(request, user_id):
    receiver = get_object_or_404(User, pk=user_id)

    if receiver == request.user:
        return HttpResponse("No puedes conectar contigo mismo.", status=400)

    # Check if connection already exists in either direction
    existing = Connection.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).first()

    if existing:
        # Return current status button (idempotent)
        return _render_connection_status(request, existing)

    connection = Connection.objects.create(sender=request.user, receiver=receiver)
    return _render_connection_status(request, connection)


@login_required
def manage_request(request, connection_id, action):
    connection = get_object_or_404(Connection, pk=connection_id, receiver=request.user)

    if action == 'accept':
        connection.status = 'ACCEPTED'
        connection.save()
    elif action == 'reject':
        connection.status = 'REJECTED'
        connection.save()

    # Return updated button for the request list
    return HttpResponse(f"""
        <span class="text-sm px-3 py-1 rounded-full bg-{'emerald' if action == 'accept' else 'slate'}-500/20 text-{'emerald' if action == 'accept' else 'slate'}-400 border border-{'emerald' if action == 'accept' else 'slate'}-500/30">
            {'Aceptada' if action == 'accept' else 'Rechazada'}
        </span>
    """)


@login_required
def my_connections(request):
    # Accepted connections (in either direction)
    accepted = Connection.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status='ACCEPTED'
    ).select_related('sender__profile', 'receiver__profile')

    # Pending requests RECEIVED by me
    pending_received = Connection.objects.filter(
        receiver=request.user,
        status='PENDING'
    ).select_related('sender__profile')

    # Pending requests SENT by me
    pending_sent = Connection.objects.filter(
        sender=request.user,
        status='PENDING'
    ).select_related('receiver__profile')

    return render(request, 'core/connections.html', {
        'accepted': accepted,
        'pending_received': pending_received,
        'pending_sent': pending_sent,
    })


def _render_connection_status(request, connection):
    """Helper to render a status badge for the connect button (HTMX response)."""
    status = connection.status

    if status == 'ACCEPTED':
        html = """<span class="text-sm px-3 py-1.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            Conectado
        </span>"""
    elif status == 'PENDING' and connection.sender == request.user:
        html = """<span class="text-sm px-3 py-1.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1">
            <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Solicitud Enviada
        </span>"""
    elif status == 'PENDING' and connection.receiver == request.user:
        html = f"""<a href="/connections/manage/{connection.pk}/accept/" class="text-sm px-3 py-1.5 rounded-full bg-blue-600 hover:bg-blue-700 text-white transition-colors">
            Aceptar Solicitud
        </a>"""
    else:
        html = """<span class="text-slate-400 text-sm">Rechazada</span>"""

    return HttpResponse(html)

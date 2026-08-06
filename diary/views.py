from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from catalog.models import Fragrance
from .models import ScentLog
from .forms import ScentLogForm


def index(request):
    """Display the authenticated user's fragrance wear logs."""
    if not request.user.is_authenticated:
        logs = ScentLog.objects.none()
        total_logs = 0
    else:
        logs = ScentLog.objects.filter(user=request.user).select_related(
            'user', 'fragrance', 'fragrance__house'
        )
        total_logs = logs.count()

    context = {
        'logs': logs,
        'total_logs': total_logs,
    }
    return render(request, 'diary/index.html', context)


def entry_detail(request, pk):
    """Detailed view for an individual wear log entry."""
    log = get_object_or_404(
        ScentLog.objects.select_related('user', 'fragrance', 'fragrance__house'),
        pk=pk
    )
    return render(request, 'diary/entry_detail.html', {'log': log})


@login_required
def scent_log_create(request):
    """Create a wear log entry for a fragrance.

    Supports both regular HTML form POST and AJAX submissions from the modal.
    """
    initial_data = {}
    fragrance_id = request.GET.get('fragrance')
    if fragrance_id:
        fragrance = get_object_or_404(Fragrance, pk=fragrance_id)
        initial_data['fragrance'] = fragrance

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = ScentLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/diary/{log.pk}/',
                })
            return redirect('diary:entry_detail', pk=log.pk)
        else:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                }, status=400)
    else:
        form = ScentLogForm(initial=initial_data)

    return render(request, 'diary/scent_log_form.html', {'form': form})


@login_required
def scent_log_update(request, pk):
    """Update a user's own wear log entry."""
    log = get_object_or_404(ScentLog, pk=pk)
    if log.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You can only edit your own wear logs.")

    if request.method == 'POST':
        form = ScentLogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            return redirect('diary:entry_detail', pk=log.pk)
    else:
        form = ScentLogForm(instance=log)

    return render(request, 'diary/scent_log_form.html', {'form': form, 'log': log})


@login_required
def scent_log_delete(request, pk):
    """Delete a user's own wear log entry."""
    log = get_object_or_404(ScentLog, pk=pk)
    if log.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You can only delete your own wear logs.")

    if request.method == 'POST':
        log.delete()
        return redirect('diary:index')

    return render(request, 'diary/scent_log_confirm_delete.html', {'log': log})

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ScentLog
from .serializers import (
    ScentLogListSerializer,
    ScentLogDetailSerializer,
    ScentLogWriteSerializer,
)


class IsOwnerOrStaff(permissions.BasePermission):
    """Only the log owner or staff can modify/delete."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff


class ScentLogListCreateView(generics.ListCreateAPIView):
    """
    GET  — list the authenticated user's diary entries (paginated).
    POST — create a new diary entry (user is auto-assigned).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ScentLogWriteSerializer
        return ScentLogListSerializer

    def get_queryset(self):
        return (
            ScentLog.objects.filter(user=self.request.user)
            .select_related('user', 'fragrance', 'fragrance__house')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ScentLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — view a single diary entry (any authenticated user).
    PUT/PATCH — update (owner or staff only).
    DELETE — delete (owner or staff only).
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ScentLogWriteSerializer
        return ScentLogDetailSerializer

    def get_queryset(self):
        return (
            ScentLog.objects.select_related('user', 'fragrance', 'fragrance__house')
        )

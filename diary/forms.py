from django import forms
from .models import ScentLog


class ScentLogForm(forms.ModelForm):
    """Form for recording a fragrance wear session."""
    class Meta:
        model = ScentLog
        fields = [
            'fragrance', 'wear_date', 'rating', 'occasion',
            'sprays', 'sillage_rating', 'longevity_hours',
            'review_text', 'is_favorite',
        ]
        widgets = {
            'fragrance': forms.Select(attrs={'class': 'form-input rounded-lg'}),
            'wear_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input rounded-lg',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': 0.5, 'max': 5.0, 'step': 0.5,
                'placeholder': '0.5 - 5.0',
            }),
            'occasion': forms.Select(attrs={'class': 'form-input rounded-lg'}),
            'sprays': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': 1, 'max': 20,
            }),
            'sillage_rating': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': 1, 'max': 5,
                'placeholder': '1 (Intimate) - 5 (Beast)',
            }),
            'longevity_hours': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': 1, 'max': 24,
                'placeholder': 'Hours',
            }),
            'review_text': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-input rounded-lg',
                'placeholder': 'How did it make you feel? What did you notice throughout the day?',
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 accent-amber',
            }),
        }

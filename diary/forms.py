from django import forms
from .models import ScentLog
from catalog.models import Fragrance


class ScentLogForm(forms.ModelForm):
    """Form for recording a fragrance wear session."""

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Gather IDs of fragrances in the user's wardrobe
            wardrobe_ids = list(user.wardrobe.values_list('fragrance_id', flat=True))
            
            # Keep currently selected fragrance if editing
            extra_ids = []
            if self.instance and self.instance.fragrance_id:
                extra_ids.append(self.instance.fragrance_id)
            
            # Keep initial fragrance if logging directly from detail page
            initial_fragrance = self.initial.get('fragrance')
            if initial_fragrance:
                if isinstance(initial_fragrance, int):
                    extra_ids.append(initial_fragrance)
                elif hasattr(initial_fragrance, 'id'):
                    extra_ids.append(initial_fragrance.id)
            
            # Keep submitted fragrance if form is bound (e.g. POST request)
            if self.is_bound:
                submitted_fragrance = self.data.get('fragrance')
                if submitted_fragrance:
                    try:
                        extra_ids.append(int(submitted_fragrance))
                    except (ValueError, TypeError):
                        pass
            
            allowed_ids = list(set(wardrobe_ids + extra_ids))
            self.fields['fragrance'].queryset = Fragrance.objects.filter(id__in=allowed_ids).select_related('house')
        else:
            self.fields['fragrance'].queryset = Fragrance.objects.none()

    class Meta:
        model = ScentLog
        fields = [
            'fragrance', 'wear_date', 'rating', 'occasion',
            'sprays', 'sillage_rating', 'longevity_hours',
            'review_text', 'is_favorite',
        ]
        widgets = {
            'fragrance': forms.Select(attrs={
                'class': 'form-input',
            }),
            'wear_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0.5, 'max': 5.0, 'step': 0.5,
                'placeholder': '0.5 - 5.0',
            }),
            'occasion': forms.Select(attrs={
                'class': 'form-input',
            }),
            'sprays': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1, 'max': 20,
            }),
            'sillage_rating': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1, 'max': 5,
                'placeholder': '1 (Intimate) - 5 (Beast)',
            }),
            'longevity_hours': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1, 'max': 24,
                'placeholder': 'Hours',
            }),
            'review_text': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-input',
                'placeholder': 'How did it make you feel? What did you notice throughout the day?',
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 accent-amber',
            }),
        }

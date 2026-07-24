from django import forms
from .models import House, Note, Fragrance


class HouseForm(forms.ModelForm):
    """Form for creating or updating a perfume house."""

    class Meta:
        model = House
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'House Name'}),
        }


class NoteForm(forms.ModelForm):
    """Form for creating or updating an individual fragrance note."""

    class Meta:
        model = Note
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Note Name'}),
        }


class FragranceForm(forms.ModelForm):
    """Form for creating or updating a fragrance composition entry."""

    class Meta:
        model = Fragrance
        fields = [
            'name',
            'house',
            'gender',
            'release_year',
            'top_notes',
            'heart_notes',
            'base_notes',
            'source_image_url',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fragrance Name'}),
            'house': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024'}),
            'top_notes': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'heart_notes': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'base_notes': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
            'source_image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/image.jpg'}),
        }


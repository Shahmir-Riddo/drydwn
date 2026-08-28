from django import forms
from .models import House, Note, Fragrance, FragranceRequest


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


class FragranceRequestForm(forms.ModelForm):
    """Form for users to request a fragrance to be added to the catalogue."""

    class Meta:
        model = FragranceRequest
        fields = [
            'fragrance_name',
            'house_name',
            'gender',
            'release_year',
            'notes_description',
            'reference_url',
        ]
        labels = {
            'fragrance_name': 'Fragrance Name',
            'house_name': 'House / Brand',
            'gender': 'Target Audience',
            'release_year': 'Release Year',
            'notes_description': 'Additional Details',
            'reference_url': 'Reference Link',
        }
        widgets = {
            'fragrance_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Baccarat Rouge 540',
            }),
            'house_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Maison Francis Kurkdjian',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-input',
            }),
            'release_year': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 2015',
                'min': '1900',
                'max': '2030',
            }),
            'notes_description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Known notes, concentration type, or any details that help us identify the fragrance…',
            }),
            'reference_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://www.fragrantica.com/perfume/...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make gender have a blank default choice
        self.fields['gender'].choices = [('', 'Select…')] + list(Fragrance.GENDER_CHOICES)
        self.fields['gender'].required = False


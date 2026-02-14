from django import forms
from .models import CarpetType, Media, Review, Advertisement
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class CarpetTypeForm(forms.ModelForm):
    class Meta:
        model = CarpetType
        fields = ['name', 'description', 'price_per_m2']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gilam nomi'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tavsif'}),
            'price_per_m2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Narx'}),
        }

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Foydalanuvchi nomi",
        max_length=150,
        help_text="Faqat harflar, raqamlar va @/./+/-/_ belgilari ishlatilishi mumkin."
    )
    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput,
        help_text="Parol kamida 8 ta belgidan iborat bo‘lishi, shaxsiy ma’lumotlarga o‘xshamasligi va raqamlar bilan cheklanmasligi kerak."
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlash",
        widget=forms.PasswordInput,
        help_text="Yuqoridagi parolni takror kiriting."
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = [
            'title',
            'description',
            'media_type',
            'image',
            'video_file',
            'video_url',
            'duration',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'media_type': forms.Select(attrs={'class': 'form-control', 'id': 'media_type_select'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00:03:45'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        image = cleaned_data.get('image')
        video_file = cleaned_data.get('video_file')
        video_url = cleaned_data.get('video_url')

        if media_type == 'photo':
            if not image:
                raise forms.ValidationError("Rasm tanlangan bo‘lsa, rasm faylini yuklashing kerak.")
            # Video maydoni ishlamasligi ixtiyoriy
            cleaned_data['video_file'] = None
            cleaned_data['video_url'] = ''

        elif media_type == 'video':
            if not (video_file or video_url):
                raise forms.ValidationError("Video tanlangan bo‘lsa, video fayl yoki video URL qo‘shish kerak.")
            # Rasm maydoni ishlamasligi ixtiyoriy
            cleaned_data['image'] = None

            # Video fayl validatsiyasi
            if video_file:
                ext = video_file.name.split('.')[-1].lower()
                valid_extensions = ['mp4', 'mov', 'avi', 'mkv']
                if ext not in valid_extensions:
                    raise forms.ValidationError("Faqat .mp4, .mov, .avi, .mkv formatidagi fayllar qabul qilinadi.")
                if video_file.size > 50*1024*1024:
                    raise forms.ValidationError("Video fayl hajmi 50MB dan oshmasligi kerak.")

        return cleaned_data



# ____________________sharx__________________________________


class ReviewForm(forms.ModelForm):
    rating = forms.FloatField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '1',
            'max': '5',
            'step': '0.5',
            'class': 'rating-slider'
        }),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Sharhingizni yozing...',
                'class': 'form-control'
            }),
        }
        labels = {
            'rating': 'Baholash',
            'comment': 'Sharh'
        }


from django import forms
from .models import Advertisement

class AdForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'description', 'ad_type', 'image', 'video', 'duration_days']

    def clean(self):
        cleaned = super().clean()
        image = cleaned.get("image")
        video = cleaned.get("video")

        if image and video:
            raise forms.ValidationError("Faqat rasm yoki video tanlang, bittasini")
        if not image and not video:
            raise forms.ValidationError("Rasm yoki video kiritilishi shart")
            
        return cleaned

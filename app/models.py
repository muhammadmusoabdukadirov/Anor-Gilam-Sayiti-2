from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth import get_user_model
import random


# Gilam turlari modeli
class CarpetType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Gilam turi nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    price_per_m2 = models.IntegerField(verbose_name="1 m² narxi (so`m)")

    class Meta:
        verbose_name = "Gilam turi"
        verbose_name_plural = "Gilam turlari"

    def __str__(self):
        return self.name

phone_validator = RegexValidator(
    regex=r'^\+998\d{9}$',  # +998 bilan boshlanib, 9 ta raqam
    message="Telefon raqam quyidagi formatda bo'lishi kerak: +998901234567"
)

# Buyurtmalar modeli
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('processing', 'Jarayonda'),
        ('completed', 'Tugatilgan'),
    ]

    name = models.CharField(max_length=100, verbose_name="Ism familiya")
    phone = models.CharField(max_length=20, validators=[phone_validator], verbose_name="Telefon raqam")
    address = models.CharField(max_length=255, verbose_name="Manzil")
    carpet_type = models.ForeignKey(
        CarpetType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Gilam turi"
    )
    other_carpet_name = models.CharField(
        max_length=100, blank=True, verbose_name="Boshqa gilam nomi",
        help_text="Agar ro`yxatda bo`lmasa, o`zingiz gilam nomini kiriting"
    )
    date = models.DateField(verbose_name="Buyurtma kuni")
    comment = models.TextField(blank=True, verbose_name="Izoh")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Holat"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"{self.name} — {self.phone}"



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


class VisitLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f"{self.user.username if self.user else 'Guest'} - {self.timestamp}"
    
# video / rasim uchun
class Media(models.Model):
    MEDIA_CHOICES = (
        ('video', 'Video'),
        ('photo', 'Rasm'),
    )
    title = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    media_type = models.CharField(max_length=10, choices=MEDIA_CHOICES, verbose_name="Turi")
    image = models.ImageField(upload_to='media/photos/', blank=True, null=True, verbose_name="Rasm")
    video_file = models.FileField(upload_to='media/videos/', blank=True, null=True, verbose_name="Video fayl")  # yangi
    video_url = models.URLField(blank=True, null=True, verbose_name="Video havolasi (YouTube / Drive)")
    duration = models.CharField(max_length=20, blank=True, null=True, verbose_name="Video davomiyligi (faqat video uchun)")
    views = models.PositiveIntegerField(default=0, verbose_name="Ko‘rishlar soni (faqat video uchun)")
    likes = models.PositiveIntegerField(default=0, verbose_name="Layklar soni")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo‘yilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Oxirgi yangilanish")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Mediyalar"
        ordering = ['-created_at']

class Sovga(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Sovg'a nomi")
    tasvir = models.TextField(blank=True, verbose_name="Sovg'a tasviri")
    foiz = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Yutuq foizi (%)"
    )
    katak_raqami = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Katak raqami"
    )
    rangi = models.CharField(max_length=7, default="#3498db", verbose_name="Katak rangi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    yaratilgan_vaqt = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sovg'a"
        verbose_name_plural = "Sovg'alar"
        ordering = ['katak_raqami']
    
    def __str__(self):
        return f"{self.nomi} (katak {self.katak_raqami}) - {self.foiz}%"

class BarabanSpin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spins')
    sovga = models.ForeignKey(Sovga, on_delete=models.SET_NULL, null=True, blank=True)
    spin_vaqti = models.DateTimeField(auto_now_add=True)
    keyingi_spin_vaqti = models.DateTimeField()
    
    class Meta:
        ordering = ['-spin_vaqti']
    
    def __str__(self):
        sovga_nomi = self.sovga.nomi if self.sovga else "Yutuq yo'q"
        return f"{self.user.username} - {sovga_nomi} - {self.spin_vaqti.strftime('%d.%m.%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        if not self.keyingi_spin_vaqti:
            from django.utils import timezone
            from datetime import timedelta
            self.keyingi_spin_vaqti = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)


User = get_user_model()

class Yutuq(models.Model):
    """Foydalanuvchilarning yutuqlari"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='yutuqlar')
    sovga = models.ForeignKey('Sovga', on_delete=models.SET_NULL, null=True, blank=True, related_name='yutuqlar')
    spin_vaqti = models.DateTimeField(auto_now_add=True)
    yutib_oldingi = models.BooleanField(default=True)
    ishlatildi = models.BooleanField(default=False, verbose_name="Yutuq ishlatildimi?")
    ishlatilgan_vaqt = models.DateTimeField(null=True, blank=True)
    izoh = models.TextField(blank=True, verbose_name="Qo'shimcha izoh")
    
    class Meta:
        ordering = ['-spin_vaqti']
        verbose_name = "Yutuq"
        verbose_name_plural = "Yutuqlar"
    
    def __str__(self):
        if self.yutib_oldingi and self.sovga:
            return f"{self.user.username} - {self.sovga.nomi}"
        return f"{self.user.username} - Yutuq yo'q"
    
    def save(self, *args, **kwargs):
        if self.ishlatildi and not self.ishlatilgan_vaqt:
            self.ishlatilgan_vaqt = timezone.now()
        super().save(*args, **kwargs)


# __________________________sharx____________________________________________

# models.py fayliga qo'shing
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField(verbose_name="Baholash (1-5)", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(verbose_name="Sharh", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
    
    def __str__(self):
        return f"{self.user.username} - {self.rating} ★"
    
    def get_stars(self):
        """Yulduzchalar ro'yxatini qaytaradi"""
        full_stars = int(self.rating)
        half_star = self.rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        return {
            'full': range(full_stars),
            'half': half_star,
            'empty': range(empty_stars)
        }
    


# ____________________________________


from django.db import models
from django.utils import timezone
from datetime import timedelta

class Advertisement(models.Model):

    AD_TYPE_CHOICES = (
        ('image', 'Rasm'),
        ('video', 'Video'),
        ('text', 'Matn'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES)

    image = models.ImageField(upload_to='ads/images/', blank=True, null=True)
    video = models.FileField(upload_to='ads/videos/', blank=True, null=True)

    expires_at = models.DateTimeField(null=True, blank=True)

    color = models.CharField(max_length=20, default="#ff6a00")

    views = models.PositiveIntegerField(default=0)
    duration_days = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        if self.expires_at:
            return timezone.now() <= self.expires_at
        return True

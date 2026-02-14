from django.contrib import admin
from .models import CarpetType, Order,Profile, Media, Sovga, BarabanSpin, Advertisement

admin.site.register(CarpetType)
admin.site.register(Order)
admin.site.register(Profile)



@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'is_active', 'created_at')
    list_filter = ('media_type', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('views',)


@admin.register(Sovga)
class SovgaAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'foiz', 'katak_raqami', 'rangi', 'is_active', 'yaratilgan_vaqt')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'rangi')
    search_fields = ('nomi',)
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('nomi', 'tasvir', 'foiz', 'is_active')
        }),
        ("Barabanda joylashish", {
            'fields': ('katak_raqami', 'rangi'),
            'description': "Barabanda sovg'a qaysi katakda va qanday rangda ko'rinishini belgilang"
        }),
    )

@admin.register(BarabanSpin)
class BarabanSpinAdmin(admin.ModelAdmin):
    list_display = ('user', 'sovga', 'spin_vaqti', 'keyingi_spin_vaqti', 'can_spin')
    list_filter = ('spin_vaqti',)
    search_fields = ('user__username', 'sovga__nomi')
    readonly_fields = ('spin_vaqti', 'keyingi_spin_vaqti')
    
    def can_spin(self, obj):
        return obj.can_spin_again()
    can_spin.boolean = True
    can_spin.short_description = "Yana spin qila oladimi?"




@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'ad_type', 'views', 'created_at')
    readonly_fields = ('views', 'created_at')

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

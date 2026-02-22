from django.shortcuts import render, redirect, get_object_or_404
from .forms import CarpetTypeForm, SimpleUserCreationForm, MediaForm, ReviewForm, AdForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q, Avg, Count
from .telegram_bot import send_telegram_message
from django.contrib.auth.models import User
from .models import CarpetType, VisitLog, Order, Media, VisitLog, Sovga, BarabanSpin, User, Yutuq, Review, Advertisement
from django.contrib.admin.views.decorators import staff_member_required
import random
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import json
from . import forms



def index(request):
    carpets = CarpetType.objects.all()

    # 🔥 Bugungi sana
    today = timezone.now().date()
    start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_today = timezone.make_aware(datetime.combine(today, datetime.max.time()))

    # 🔥 Bugungi kirishlarni hisoblash
    today_visits = VisitLog.objects.filter(timestamp__range=(start_of_today, end_of_today))

    # 🔥 Bugun kirgan foydalanuvchilar
    today_logged_in_users = today_visits.filter(user__isnull=False).values('user').distinct()
    today_logged_in_user_ids = [item['user'] for item in today_logged_in_users]
    today_users = User.objects.filter(id__in=today_logged_in_user_ids)

    # 🔥 To'liq statistikani hisoblash
    stats = {
        # Bugungi kirishlar statistikasi
        'today_visits': today_visits.count(),
        'guests_today': today_visits.filter(user__isnull=True).count(),
        'users_today': today_logged_in_users.count(),
        'admins_today': today_users.filter(is_superuser=True).count(),
        'staff_today': today_users.filter(is_staff=True, is_superuser=False).count(),
        'customers_today': today_users.filter(is_staff=False, is_superuser=False).count(),

        # Buyurtmalar statistikasi
        'new_orders': Order.objects.filter(created_at__date=today, status='new').count(),
        'processing_orders': Order.objects.filter(created_at__date=today, status='processing').count(),
        'completed_orders': Order.objects.filter(created_at__date=today, status='completed').count(),

        # Umumiy buyurtmalar (ixtiyoriy)
        'total_orders': Order.objects.all().count(),
        'total_new_orders': Order.objects.filter(status='new').count(),
        'total_processing_orders': Order.objects.filter(status='processing').count(),
        'total_completed_orders': Order.objects.filter(status='completed').count(),
    }

    # 🔥 Media bo‘limlari
    videos = Media.objects.filter(media_type='video', is_active=True)
    photos = Media.objects.filter(media_type='photo', is_active=True)

    context = {
        'carpets': carpets,
        'stats': stats,
        'today_date': today,
        'videos': videos,    # video bo‘limi
        'photos': photos,    # rasm bo‘limi
    }

    return render(request, 'app/index.html', context)


# ---------------------------------CREATE_ORDER------------------------------------

def create_order(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        carpet_type_id = request.POST.get("carpet_type")
        other_carpet_name = request.POST.get("other_carpet_name")
        date = request.POST.get("date")
        comment = request.POST.get("comment")

        carpet_type = CarpetType.objects.get(id=carpet_type_id) if carpet_type_id else None

        order = Order.objects.create(
            name=name,
            phone=phone,
            address=address,
            carpet_type=carpet_type,
            other_carpet_name=other_carpet_name,
            date=date,
            comment=comment
        )

        # 📩 Botga ketadigan xabar
        message = f"""
📦 *Yangi buyurtma!*

👤 Ism: *{name}*
📞 Telefon: *{phone}*
📍 Manzil: *{address}*
🧼 Gilam turi: *{carpet_type.name if carpet_type else other_carpet_name}*
📅 Sana: *{date}*
📝 Izoh: {comment}
"""

        # 🔥 Qo‘shimcha faylga yozilgan funksiya chaqirilyapti
        send_telegram_message(message)

        messages.success(request, "Buyurtma muvaffaqiyatli yuborildi!")
        return redirect('index')

    return redirect('index')



def clients(request):
    orders = Order.objects.all().order_by('-id')

    # Statistika hisoblash
    total_orders = orders.count()
    new_orders = orders.filter(status='new').count()
    processing_orders = orders.filter(status='processing').count()
    completed_orders = orders.filter(status='completed').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'new_orders': new_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
    }
    return render(request, 'app/clients.html', context)


# AJAX orqali status yangilash
@csrf_exempt
def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        status = request.POST.get('status')

        if status in ['new', 'processing', 'completed']:
            order.status = status
            order.save()
            return JsonResponse({'success': True, 'status': status})
    return JsonResponse({'success': False}, status=400)

@require_POST
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('clients')

# -------------------------SOZLAMALAR--------------------------------------------

def boshqaruv(request):

    register_form = SimpleUserCreationForm()
    login_form = AuthenticationForm()

    if request.method == "POST":
        action = request.POST.get("action")

        # ================= REGISTER =================
        if action == "register":
            register_form = SimpleUserCreationForm(request.POST)
            login_form = AuthenticationForm()

            if register_form.is_valid():
                user = register_form.save()
                login(request, user)

                messages.success(request, f"Xush kelibsiz, {user.username}! 🎉")
                return redirect("boshqaruv")

            else:
                for error in register_form.errors.values():
                    messages.error(request, error)

        # ================= LOGIN =================
        elif action == "login":
            login_form = AuthenticationForm(request, data=request.POST)
            register_form = SimpleUserCreationForm()

            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)

                messages.success(request, f"Xush kelibsiz, {user.username}! 👋")
                return redirect("boshqaruv")

            else:
                for error in login_form.errors.values():
                    messages.error(request, error)

        # ================= LOGOUT =================
        elif action == "logout":
            logout(request)
            messages.success(request, "Tizimdan chiqdingiz 👋")
            return redirect("boshqaruv")

    context = {
        "register_form": register_form,
        "login_form": login_form,
    }

    return render(request, "app/boshqaruv.html", context)

@login_required
def sozlamalar(request):
    add_form = CarpetTypeForm(request.POST or None, prefix="add")
    update_form = None
    selected_carpet = None

    if add_form.is_valid() and 'add-name' in request.POST:
        new_carpet = add_form.save()
        messages.success(request, f"{new_carpet.name} muvaffaqiyatli qo'shildi!")
        return redirect('sozlamalar')

    if 'update-id' in request.POST and request.POST['update-id']:
        carpet_id = request.POST.get('update-id')
        selected_carpet = get_object_or_404(CarpetType, id=carpet_id)
        update_form = CarpetTypeForm(request.POST, instance=selected_carpet, prefix="update")

        if 'update-name' in request.POST and update_form.is_valid():
            updated_carpet = update_form.save()
            messages.success(request, f"{updated_carpet.name} muvaffaqiyatli yangilandi!")
            return redirect('sozlamalar')
    else:
        update_form = CarpetTypeForm(prefix="update")

    if 'delete-id' in request.POST and request.POST['delete-id']:
        carpet_id = request.POST.get('delete-id')
        selected_carpet = get_object_or_404(CarpetType, id=carpet_id)
        carpet_name = selected_carpet.name
        selected_carpet.delete()
        messages.success(request, f"{carpet_name} muvaffaqiyatli o'chirildi!")
        return redirect('sozlamalar')

    context = {
        'add_form': add_form,
        'update_form': update_form,
        'carpets': CarpetType.objects.all(),
    }
    return render(request, 'app/sozlamalar.html', context)

@login_required(login_url='boshqaruv')
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':

        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        profile.phone = request.POST.get('phone')

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        user.save()
        profile.save()

        messages.success(request, "Profil muvaffaqiyatli yangilandi!")
        return redirect('profile')

    return render(request, 'app/profile.html')


def get_dashboard_stats():
    today = timezone.now().date()
    start_of_today = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_today = timezone.make_aware(datetime.combine(today, datetime.max.time()))

    # Bugungi kirishlar
    today_visits = VisitLog.objects.filter(timestamp__range=(start_of_today, end_of_today))

    # Bugun kirmagan foydalanuvchilarni aniqlash
    today_logged_in_users = today_visits.filter(user__isnull=False).values('user').distinct()
    today_logged_in_user_ids = [item['user'] for item in today_logged_in_users]

    # Bugun kirgan foydalanuvchilar turkumlari
    today_users = User.objects.filter(id__in=today_logged_in_user_ids)

    stats = {
        'today_visits': today_visits.count(),
        'guests_today': today_visits.filter(user__isnull=True).count(),
        'users_today': today_logged_in_users.count(),
        'new_orders': Order.objects.filter(status='new').count(),
        'processing_orders': Order.objects.filter(status='processing').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),

        # Bugungi faol foydalanuvchilar ro'yxati (qo'shimcha)
        'today_active_users': today_users.values('username', 'email')[:10]
    }

    return stats


def admin_required(user):
    return user.is_superuser

@login_required
@user_passes_test(admin_required)
def video_rasim(request, pk=None):
    if pk:
        media = get_object_or_404(Media, pk=pk)
        form = MediaForm(request.POST or None, request.FILES or None, instance=media)
        action = 'edit'
    else:
        media = None
        form = MediaForm(request.POST or None, request.FILES or None)
        action = 'add'

    if request.method == 'POST' and form.is_valid():
        media_instance = form.save(commit=False)

        if media_instance.media_type == 'photo' and media_instance.image:
            media_instance.image.name = f'photos/{media_instance.image.name}'
        elif media_instance.media_type == 'video' and media_instance.video_url:
            pass

        media_instance.save()
        return redirect('video_rasim')

    media_list = Media.objects.all()

    context = {
        'form': form,
        'media_list': media_list,
        'action': action,
        'media': media,
    }
    return render(request, 'app/video_rasim.html', context)


def video_list(request):
    videos = Media.objects.filter(media_type='video').order_by('-created_at')
    
    # Pagination - har safar 15 ta video
    paginator = Paginator(videos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'videos': page_obj.object_list,
        'title': '🎬 Video Galereya',
        'is_video_page': True
    }
    return render(request, 'app/video_list.html', context)

# ============ VIDEO BOSHQARISH ============


def add_video(request, pk=None):
    """Video qo'shish yoki tahrirlash"""
    video = None
    action = 'add'
    
    if pk:
        video = get_object_or_404(Media, pk=pk, media_type='video')
        action = 'edit'
    
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            video_instance = form.save(commit=False)
            video_instance.media_type = 'video'
            video_instance.save()
            
            message = "Video muvaffaqiyatli yangilandi!" if pk else "Video muvaffaqiyatli qo'shildi!"
            messages.success(request, message)
            return redirect('video_list')
    else:
        form = MediaForm(instance=video)
    
    videos = Media.objects.filter(media_type='video').order_by('-created_at')
    
    context = {
        'form': form,
        'videos': videos,
        'action': action,
        'current_video': video,
    }
    
    return render(request, 'app/video_list.html', context)

@staff_member_required
def delete_video(request, pk):
    """Videoni o'chirish"""
    video = get_object_or_404(Media, pk=pk, media_type='video')
    title = video.title
    video.delete()
    messages.success(request, f'"{title}" videosi o\'chirildi!')
    return redirect('video_list')

# ============ RASM BOSHQARISH ============


def photo_list(request):
    """Rasmlar ro'yxati"""
    photos = Media.objects.filter(media_type='photo').order_by('-created_at')
    
    context = {
        'photos': photos,
    }
    
    return render(request, 'app/photo_list.html', context)


def add_photo(request, pk=None):
    """Rasm qo'shish yoki tahrirlash"""
    photo = None
    action = 'add'
    
    if pk:
        photo = get_object_or_404(Media, pk=pk, media_type='photo')
        action = 'edit'
    
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            photo_instance = form.save(commit=False)
            photo_instance.media_type = 'photo'
            photo_instance.save()
            
            message = "Rasm muvaffaqiyatli yangilandi!" if pk else "Rasm muvaffaqiyatli qo'shildi!"
            messages.success(request, message)
            return redirect('photo_list')
    else:
        form = MediaForm(instance=photo)
    
    photos = Media.objects.filter(media_type='photo').order_by('-created_at')
    
    context = {
        'form': form,
        'photos': photos,
        'action': action,
        'current_photo': photo,
    }
    
    return render(request, 'app/add_edit_photo.html', context)

@staff_member_required
def delete_photo(request, pk):
    """Rasmni o'chirish"""
    photo = get_object_or_404(Media, pk=pk, media_type='photo')
    title = photo.title
    photo.delete()
    messages.success(request, f'"{title}" rasm o\'chirildi!')
    return redirect('photo_list')

# ============ UMUMIY MEDIA ============

@staff_member_required
def delete_media(request, pk):
    """Har qanday media ni o'chirish"""
    media = get_object_or_404(Media, pk=pk)
    title = media.title
    media_type = media.media_type
    media.delete()
    messages.success(request, f'"{title}" {media_type} o\'chirildi!')
    return redirect('video_rasim')
# --------------------------baraban -------------------------------
from django.utils import timezone
from datetime import timedelta
import random

@login_required
def baraban(request):
    """Baraban sahifasi"""
    try:
        # Faol sovg'alarni olish
        sovgalar = Sovga.objects.filter(is_active=True).order_by('katak_raqami')
        
        # Foydalanuvchining oxirgi spinini olish
        last_spin = BarabanSpin.objects.filter(user=request.user).order_by('-spin_vaqti').first()
        
        # Spin qila olishini tekshirish
        can_spin = True
        remaining_time = 0
        
        if last_spin:
            now = timezone.now()
            if now < last_spin.keyingi_spin_vaqti:
                can_spin = False
                remaining_time = int((last_spin.keyingi_spin_vaqti - now).total_seconds())
        
        context = {
            'user': request.user,
            'sovgalar': sovgalar,
            'last_spin': last_spin,
            'can_spin': can_spin,
            'remaining_time': remaining_time,
        }
        
        return render(request, 'app/baraban.html', context)
        
    except Exception as e:
        messages.error(request, f"Xatolik: {str(e)}")
        return redirect('index')


@csrf_exempt
@login_required
def spin_baraban(request):
    """Barabanni aylantirish"""
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Faqat POST so\'rov qabul qilinadi'})
        
        # Foydalanuvchining oxirgi spinini tekshirish
        last_spin = BarabanSpin.objects.filter(user=request.user).order_by('-spin_vaqti').first()
        
        if last_spin:
            now = timezone.now()
            if now < last_spin.keyingi_spin_vaqti:
                qolgan = last_spin.keyingi_spin_vaqti - now
                soat = qolgan.seconds // 3600
                daqiqa = (qolgan.seconds % 3600) // 60
                soniya = qolgan.seconds % 60
                return JsonResponse({
                    'success': False,
                    'error': f'Siz hali {soat:02d}:{daqiqa:02d}:{soniya:02d} vaqt o\'tmagan'
                })
        
        # Faol sovg'alarni olish
        active_sovgalar = Sovga.objects.filter(is_active=True)
        
        if not active_sovgalar.exists():
            return JsonResponse({
                'success': False,
                'error': 'Hozircha sovg\'alar mavjud emas'
            })
        
        # Yutuqni tasodifiy tanlash
        # 1. Barcha sovg'alarni foizlari bo'yicha ro'yxatga joylash
        prizes_list = []
        for sovga in active_sovgalar:
            prizes_list.extend([sovga] * sovga.foiz)
        
        # 2. Agar foizlar yig'indisi 100 dan kam bo'lsa, "Yutuq yo'q" qo'shish
        total_foiz = sum(s.foiz for s in active_sovgalar)
        if total_foiz < 100:
            # "Yutuq yo'q" uchun ma'lumot
            no_prize_count = 100 - total_foiz
            for _ in range(no_prize_count):
                prizes_list.append({
                    'nomi': "Yutuq yo'q",
                    'katak_raqami': random.randint(1, 10),
                    'is_no_prize': True
                })
        
        # 3. Tasodifiy tanlash
        selected = random.choice(prizes_list)
        
        # 4. Natijani aniqlash
        if isinstance(selected, dict) and selected.get('is_no_prize'):
            sovga_obj = None
            sovga_nomi = "Yutuq yo'q"
            katak_raqami = selected['katak_raqami']
        else:
            sovga_obj = selected
            sovga_nomi = selected.nomi
            katak_raqami = selected.katak_raqami
        
        # 5. Yangi spin yaratish
        next_spin_time = timezone.now() + timedelta(hours=24)
        BarabanSpin.objects.create(
            user=request.user,
            sovga=sovga_obj,
            spin_vaqti=timezone.now(),
            keyingi_spin_vaqti=next_spin_time
        )
        
        return JsonResponse({
            'success': True,
            'sovga': sovga_nomi,
            'katak': katak_raqami,
            'next_spin_time': next_spin_time.strftime('%Y-%m-%d %H:%M:%S'),
            'message': f"Tabriklaymiz! Siz {sovga_nomi} sovg'asini yutdingiz!" if sovga_obj else "Bu safar omad yorilmadi. Keyingi imkoniyatingizda omad!"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server xatosi: {str(e)}'
        })
    

@staff_member_required
def sovga_management(request):
    """Sovg'alarni boshqarish"""
    try:
        if request.method == 'POST':
            # Yangi sovg'a qo'shish
            if 'add_sovga' in request.POST:
                nomi = request.POST.get('nomi', '').strip()
                foiz = request.POST.get('foiz', '10')
                katak_raqami = request.POST.get('katak_raqami', '1')
                rangi = request.POST.get('rangi', '#3498db')
                
                # Validatsiya
                if not nomi:
                    messages.error(request, "Sovg'a nomini kiriting!")
                    return redirect('sovga_management')
                
                try:
                    foiz = int(foiz)
                    katak_raqami = int(katak_raqami)
                except ValueError:
                    messages.error(request, "Foiz va katak raqamini to'g'ri kiriting!")
                    return redirect('sovga_management')
                
                # Katak raqamini tekshirish
                if katak_raqami < 1 or katak_raqami > 10:
                    messages.error(request, "Katak raqami 1 dan 10 gacha bo'lishi kerak!")
                    return redirect('sovga_management')
                
                # Foizni tekshirish
                if foiz < 1 or foiz > 100:
                    messages.error(request, "Foiz 1 dan 100 gacha bo'lishi kerak!")
                    return redirect('sovga_management')
                
                # Katak bandligini tekshirish
                existing_sovga = Sovga.objects.filter(katak_raqami=katak_raqami, is_active=True).first()
                if existing_sovga:
                    messages.error(request, f"Katak {katak_raqami} band! Iltimos, boshqa katak tanlang.")
                    return redirect('sovga_management')
                
                # Foizlar yig'indisini tekshirish
                total_foiz = sum(s.foiz for s in Sovga.objects.filter(is_active=True))
                if total_foiz + foiz > 100:
                    messages.error(request, f"Foizlar yig'indisi 100% dan oshib ketadi! Qolgan foiz: {100 - total_foiz}%")
                    return redirect('sovga_management')
                
                # Sovg'ani yaratish
                Sovga.objects.create(
                    nomi=nomi,
                    foiz=foiz,
                    katak_raqami=katak_raqami,
                    rangi=rangi,
                    is_active=True
                )
                
                messages.success(request, f"✅ '{nomi}' sovg'asi katak {katak_raqami} ga qo'shildi!")
                return redirect('sovga_management')
            
            # Sovg'ani o'chirish
            elif 'sovga_id' in request.POST:
                sovga_id = request.POST.get('sovga_id')
                try:
                    sovga = Sovga.objects.get(id=sovga_id)
                    sovga_nomi = sovga.nomi
                    sovga.delete()
                    messages.success(request, f"✅ '{sovga_nomi}' sovg'asi o'chirildi!")
                except Sovga.DoesNotExist:
                    messages.error(request, "Sovg'a topilmadi!")
                
                return redirect('sovga_management')
        
        # FAQAT AKTIV SOVG'ALARNI OLISH
        sovgalar = Sovga.objects.filter(is_active=True).order_by('katak_raqami')
        total_foiz = sum(s.foiz for s in sovgalar)
        
        # Bo'sh kataklarni aniqlash
        occupied_kids = [s.katak_raqami for s in sovgalar]
        available_kids = [i for i in range(1, 11) if i not in occupied_kids]
        
        context = {
            'sovgalar': sovgalar,
            'total_percentage': total_foiz,
            'remaining_percentage': 100 - total_foiz,
            'available_kids': available_kids,
            'occupied_kids': occupied_kids
        }
        
        return render(request, 'app/sovga.html', context)
        
    except Exception as e:
        messages.error(request, f"Xatolik: {str(e)}")
        return redirect('index')    
    
# _________________________foydalanuvchilardiki___________________________________

@staff_member_required
def foydalanuvchilar_list(request):
    """Foydalanuvchilar ro'yxati"""
    q = request.GET.get('q', '')
    
    if q:
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        ).order_by('-date_joined')
    else:
        users = User.objects.all().order_by('-date_joined')
    
    # Har bir foydalanuvchi uchun statistikalar
    user_stats = []
    for user in users:
        total_spins = BarabanSpin.objects.filter(user=user).count()
        total_wins = BarabanSpin.objects.filter(user=user, sovga__isnull=False).count()
        user_stats.append({
            'user': user,
            'total_spins': total_spins,
            'total_wins': total_wins,
            'win_rate': (total_wins / total_spins * 100) if total_spins > 0 else 0
        })
    
    paginator = Paginator(user_stats, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'q': q,
        'total_users': User.objects.count()
    }
    
    return render(request, 'app/foydalanuvchilar.html', context)

@staff_member_required
def foydalanuvchi_detail(request, user_id):
    """Foydalanuvchi tafsilotlari"""
    try:
        user = User.objects.get(id=user_id)
        
        # Baraban spinlari
        baraban_spins = BarabanSpin.objects.filter(user=user).select_related('sovga')
        
        # Yutuqlar (Yutuq modelidan)
        yutuqlar = Yutuq.objects.filter(user=user).select_related('sovga')
        
        # Statistikalar
        total_spins = baraban_spins.count()
        total_wins = baraban_spins.filter(sovga__isnull=False).count()
        total_used = yutuqlar.filter(ishlatildi=True).count()
        
        context = {
            'user': user,
            'baraban_spins': baraban_spins,
            'yutuqlar': yutuqlar,
            'total_spins': total_spins,
            'total_wins': total_wins,
            'total_used': total_used,
            'win_rate': (total_wins / total_spins * 100) if total_spins > 0 else 0
        }
        
        return render(request, 'app/foydalanuvchi_detail.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "Foydalanuvchi topilmadi")
        return redirect('foydalanuvchilar_list')

@staff_member_required
def get_yutuq_info(request, yutuq_id):
    """Yutuq ma'lumotlarini olish"""
    try:
        yutuq = Yutuq.objects.get(id=yutuq_id)
        return JsonResponse({
            'success': True,
            'izoh': yutuq.izoh,
            'ishlatildi': yutuq.ishlatildi,
            'sovga_nomi': yutuq.sovga.nomi if yutuq.sovga else "Yutuq yo'q",
            'user': yutuq.user.username,
            'vaqt': yutuq.spin_vaqti.strftime("%d.%m.%Y %H:%M")
        })
    except Yutuq.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Yutuq topilmadi'})

@staff_member_required
def update_yutuq(request):
    """Yutuqni yangilash"""
    if request.method == 'POST':
        try:
            yutuq_id = request.POST.get('yutuq_id')
            izoh = request.POST.get('izoh', '')
            ishlatildi = request.POST.get('ishlatildi') == 'on'
            
            yutuq = Yutuq.objects.get(id=yutuq_id)
            yutuq.izoh = izoh
            yutuq.ishlatildi = ishlatildi
            if ishlatildi and not yutuq.ishlatilgan_vaqt:
                yutuq.ishlatilgan_vaqt = timezone.now()
            yutuq.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Faqat POST so\'rov'})

@staff_member_required
def mark_yutuq_used(request, yutuq_id):
    """Yutuqni ishlatilgan deb belgilash"""
    try:
        yutuq = Yutuq.objects.get(id=yutuq_id)
        yutuq.ishlatildi = True
        yutuq.ishlatilgan_vaqt = timezone.now()
        yutuq.save()
        
        return JsonResponse({'success': True})
    except Yutuq.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Yutuq topilmadi'})

# ______________________sharx_________________________________________

def reviews_list(request):
    """Barcha sharhlarni ko'rsatish"""
    reviews = Review.objects.filter(is_active=True).select_related('user').order_by('-created_at')
    
    # Reyting statistikasi
    stats = Review.objects.filter(is_active=True).aggregate(
        total=Count('id'),
        average=Avg('rating'),
        five_star=Count('id', filter=Q(rating=5)),
        four_star=Count('id', filter=Q(rating__gte=4, rating__lt=5)),
        three_star=Count('id', filter=Q(rating__gte=3, rating__lt=4)),
        two_star=Count('id', filter=Q(rating__gte=2, rating__lt=3)),
        one_star=Count('id', filter=Q(rating__gte=1, rating__lt=2))
    )
    
    # Har bir foydalanuvchining o'z sharhi bor-yo'qligini tekshirish
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, is_active=True).first()
    
    # Formani tayyorlash
    form = ReviewForm()
    
    context = {
        'reviews': reviews,
        'stats': stats,
        'user_review': user_review,
        'form': form,
    }
    
    return render(request, 'app/reviews.html', context)

@login_required
def add_review(request):
    """Yangi sharh qo'shish"""
    if request.method == 'POST':
        # Foydalanuvchida oldin sharh borligini tekshirish
        existing_review = Review.objects.filter(user=request.user, is_active=True).first()
        if existing_review:
            return JsonResponse({
                'success': False,
                'error': 'Siz allaqachon sharh qoldirgansiz!'
            })
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Sharhingiz muvaffaqiyatli qo\'shildi!',
                'review_id': review.id
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Formani to\'ldirishda xatolik!'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Faqat POST so\'rov qabul qilinadi'
    })

@login_required
def edit_review(request, review_id):
    """Sharhni tahrirlash"""
    try:
        review = Review.objects.get(id=review_id, user=request.user)
        
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Sharh muvaffaqiyatli yangilandi!'
                })
        else:
            form = ReviewForm(instance=review)
            
        return JsonResponse({
            'success': False,
            'error': 'Xatolik!'
        })
        
    except Review.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sharh topilmadi yoki sizga ruxsat yo\'q!'
        })

@login_required
def delete_review(request, review_id):
    """Sharhni o'chirish (faol emas qilish)"""
    try:
        review = Review.objects.get(id=review_id, user=request.user)
        review.is_active = False
        review.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Sharh o\'chirildi!'
        })
        
    except Review.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sharh topilmadi yoki sizga ruxsat yo\'q!'
        })

def get_review_stats(request):
    """Reyting statistikasini olish (AJAX uchun)"""
    stats = Review.objects.filter(is_active=True).aggregate(
        total=Count('id'),
        average=Avg('rating'),
    )
    
    # Har bir yulduz uchun foizlarni hisoblash
    total_reviews = stats['total'] or 1  # 0 ga bo'linishdan saqlanish
    
    rating_counts = {
        '5': Review.objects.filter(rating=5, is_active=True).count(),
        '4': Review.objects.filter(rating__gte=4, rating__lt=5, is_active=True).count(),
        '3': Review.objects.filter(rating__gte=3, rating__lt=4, is_active=True).count(),
        '2': Review.objects.filter(rating__gte=2, rating__lt=3, is_active=True).count(),
        '1': Review.objects.filter(rating__gte=1, rating__lt=2, is_active=True).count(),
    }
    
    rating_percentages = {}
    for key, count in rating_counts.items():
        rating_percentages[key] = (count / total_reviews) * 100
    
    return JsonResponse({
        'success': True,
        'stats': {
            'total': stats['total'],
            'average': float(stats['average'] or 0),
            'rating_counts': rating_counts,
            'rating_percentages': rating_percentages,
        }
    })


def get_review(request, review_id):
    """AJAX uchun sharh ma'lumotlarini olish"""
    try:
        review = Review.objects.get(id=review_id)
        if request.user != review.user:
            return JsonResponse({
                'success': False,
                'error': 'Sizga ruxsat yo\'q!'
            })
            
        return JsonResponse({
            'success': True,
            'review': {
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime("%d.%m.%Y %H:%M")
            }
        })
        
    except Review.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sharh topilmadi!'
        })
    

def active_ads(request):
    ads = Advertisement.objects.all()
    active_ads = [ad for ad in ads if ad.is_active()]
    return render(request, 'app/ads.html', {'ads': active_ads})


def ad_detail(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)

    if ad.is_active():
        ad.views += 1
        ad.save()

    return render(request, 'ad_detail.html', {'ad': ad})



def create_ad(request):
    if request.method == "POST":
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ads')
    else:
        form = AdForm()

    return render(request, "app/create_ad.html", {"form": form})


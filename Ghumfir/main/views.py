from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
from datetime import datetime
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

User = get_user_model()

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    context = {'display_footer': True, 'bg_transparent': True}
    return render(request, "main/home.html", context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login Successful!')
            return redirect('dashboard')
        else: 
            messages.error(request, 'Email or Password is incorrect! Please try again.')
    
    context = {}
    return render(request, 'main/login.html', context)

def signupPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            first_name = request.POST.get('fname')
            last_name = request.POST.get('lname')
            password1 = request.POST.get('pass1')
            password2 = request.POST.get('pass2')

            if password1 != password2:
                messages.error(request, "Passwords don't match! Please try again.")

                return render(request, "main/signup.html")

            try:
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password1
                )
                user = authenticate(request, username=email, password=password1)
                if user is not None:
                    login(request, user)
                    messages.success(request, "Account created successfully.")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Something went wrong while logging in.")
            
            except Exception as e:
                messages.error(request, f"Registration failed: {e}")
                return render(request, "main/signup.html")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('signup')

    return render(request, "main/signup.html")

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect('home')

@login_required(login_url='login')
def dashboard(request):
    if request.method == "GET":
        q = request.GET.get('q', '')

    guides = GuideProfile.objects.order_by('-rating')[:4]
    for guide in guides:
        guide.stars = range(round(guide.rating))

    context = {"guides": guides, 'display_footer': True, "top_header": True}

    return render(request, "main/dashboard.html", context)

def memoryCapsule(request):
    q = request.GET.get('q', '')

    memories = Memory.objects.filter(
        Q(location_name__icontains=q)
    ).prefetch_related('media')

    memory_data = []
    for memory in memories:
        images = memory.media.all()
        if images.exists():
            memory_data.append({
                'memory': memory,
                'images': images,
            })

    memory_count = memories.count()

    context = {
        "memory_data": memory_data,
        "search_query": q,
        "memory_count": memory_count,
        "top_header": True
    }
    return render(request, "main/memory_capsule.html", context)

@login_required(login_url='login')
def add_memory(request):
    user = request.user

    if request.method == 'POST':
        location_name = request.POST.get('location_name')
        files = request.FILES.getlist('files')

        memory = Memory.objects.create(
            user=request.user,
            location_name=location_name
        )

        for file in files:
            media_type = 'video' if file.content_type.startswith('video') else 'image'
            MemoryMedia.objects.create(memory=memory, file=file, media_type=media_type)

        user.points += 5
        user.save()
        return redirect('dashboard')

    return render(request, 'main/add_memory.html')

@login_required(login_url='login')
@csrf_exempt 
def upload_sos_video(request):
    if request.method == "POST" and request.FILES.get("video"):
        user = request.user if request.user.is_authenticated else None
        video_file = request.FILES["video"]

        folder = os.path.join(settings.MEDIA_ROOT, "sos_videos")
        os.makedirs(folder, exist_ok=True)

        filename = f"sos_{user.id if user else 'unknown'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
        filepath = os.path.join(folder, filename)

        with open(filepath, "wb+") as dest:
            for chunk in video_file.chunks():
                dest.write(chunk)

        if user:
            contacts = EmergencyEmail.objects.filter(user=user)
            if contacts.exists():
                for contact in contacts:
                    send_sos_email(contact.emergency_email, filepath, user)
            else:
                print("⚠️ No emergency email found for this user.")
        else:
            print("⚠️ Anonymous upload — cannot find emergency email.")

        return JsonResponse({"status": "success", "message": "SOS video saved & sent."})
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

def send_sos_email(to_email, filepath, user):
    try:
        subject = f"SOS Alert from {user.email if user else 'Unknown User'}"
        body = "An SOS alert has been triggered. The recorded video/audio is attached."
        email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.attach_file(filepath)
        email.send()
        print(f"✅ SOS email sent to {to_email}")
    except Exception as e:
        print("❌ Email sending failed:", e)

@login_required(login_url='login')
def updateProfile(request):
    user = request.user 

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile_no = request.POST.get('mobile_no')
        profile_picture = request.FILES.get('profile_picture')

        user.first_name = first_name
        user.last_name = last_name
        user.mobile_no = mobile_no

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('dashboard')

    context = {
        'user': user
    }
    return render(request, 'main/user_profile.html', context)


@login_required(login_url='login')
def become_guide(request):
    user = request.user
    if hasattr(user, 'guideprofile'):
        return redirect('dashboard')  

    if request.method == 'POST':
        primary_location = request.POST.get('primary_location')
        secondary_location = request.POST.get('secondary_location')
        experience = request.POST.get('experience')
        rating = request.POST.get('rating')
        description = request.POST.get('description')
        languages = request.POST.get('languages')
        specialization = request.POST.get('specialization')
        rate_per_hour = request.POST.get('rate_per_hour')
        licenced = request.POST.get('licenced') == 'on'
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile_no = request.POST.get('mobile_no')
        profile_picture = request.FILES.get('profile_picture')

        user.first_name = first_name
        user.last_name = last_name
        user.mobile_no = mobile_no

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()

        guide = GuideProfile.objects.create(
            user=user,
            primary_location=primary_location,
            secondary_location=secondary_location,
            experience=experience,
            description=description,
            languages=languages,
            specialization=specialization,
            rate_per_hour=rate_per_hour,
            Licenced=licenced
        )
        messages.success(request, "Guide Profile created successfully!")
        return redirect('dashboard') 

    EXPERIENCE_YEARS = GuideProfile.EXPERIENCE_YEARS
    return render(request, 'main/become_guide.html', {'experience_choices': EXPERIENCE_YEARS})

def guideListing(request):
    q = request.GET.get('q', '')

    guides = GuideProfile.objects.filter(
        Q(primary_location__icontains=q) |
        Q(secondary_location__icontains=q) |
        Q(user__first_name__icontains=q) |
        Q(languages__icontains=q) |
        Q(user__last_name__icontains=q)
    )

    for guide in guides:
        guide.stars = range(round(guide.rating))

    guide_count = guides.count()

    context = {"guides": guides, 'display_footer': True, 'guide_count': guide_count, "search_query": q, "top_header": True}
    return render(request, "main/guide_listing.html", context)

def guideProfile(request, pk):
    guide = GuideProfile.objects.get(id=pk)
    context = {'guide': guide}
    return render(request, 'main/guide_profile.html', context)

def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    return render(request, 'main/place_detail.html', {'place': place})

def places_listing(request):
    q1 = request.GET.get('q1', '').strip()
    q2 = request.GET.get('q2', '').strip()
    q3 = request.GET.get('q3', '').strip()

    # List of searchable text fields
    search_fields = [
        'name', 'region', 'destination_type', 'best_season', 'starting_point',
        'route_overview', 'ending_point', 'transportation_access', 'lodges_hotels',
        'food_availability', 'adventure_type', 'cultural_attractions', 'language_customs',
        'local_community', 'not_to_miss_spots', 'photography_hotspots', 'unique_traditions',
        'wildlife_highlights'
    ]

    # Build Q object for a single keyword (matches any field)
    def q_for_keyword(keyword):
        q_obj = Q()
        for field in search_fields:
            q_obj |= Q(**{f"{field}__icontains": keyword})
        return q_obj

    # Combine all keywords using OR
    combined_query = Q()
    for keyword in [q1, q2, q3]:
        if keyword:
            combined_query |= q_for_keyword(keyword)

    # Filter places
    places = Place.objects.filter(combined_query).distinct()

    # Convert to list of dictionaries for template
    places_list = list(
        places.values('id', 'name', 'region', 'latitude', 'longitude')
    )

    context = {'places': places_list, "top_header": True}
    return render(request, 'main/place_listing.html', context)
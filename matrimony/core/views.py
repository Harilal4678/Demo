from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, UserProfileForm, PartnerPreferenceForm, SearchForm
from .models import UserProfile, PartnerPreference

def home(request):
    return render(request, 'core/home.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def profile_setup(request):
    try:
        profile = request.user.userprofile
        form = UserProfileForm(instance=profile)
    except UserProfile.DoesNotExist:
        form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=getattr(request.user, 'userprofile', None))
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect('preference_setup')

    return render(request, 'core/profile_setup.html', {'form': form})


@login_required
def preference_setup(request):
    try:
        preference = request.user.partnerpreference
        form = PartnerPreferenceForm(instance=preference)
    except PartnerPreference.DoesNotExist:
        form = PartnerPreferenceForm()

    if request.method == 'POST':
        form = PartnerPreferenceForm(request.POST, instance=getattr(request.user, 'partnerpreference', None))
        if form.is_valid():
            pref = form.save(commit=False)
            pref.user = request.user
            pref.save()
            return redirect('home')

    return render(request, 'core/preference_setup.html', {'form': form})


def search_profiles(request):
    form = SearchForm(request.GET or None)
    profiles = UserProfile.objects.exclude(user=request.user)

    try:
        current_user_profile = UserProfile.objects.get(user=request.user)
        opposite_gender = 'female' if current_user_profile.gender == 'male' else 'male'
        profiles = profiles.filter(gender=opposite_gender)
    except UserProfile.DoesNotExist:
        profiles = UserProfile.objects.none()  # If user profile not set up yet

    if form.is_valid():
        min_age = form.cleaned_data.get('min_age')
        max_age = form.cleaned_data.get('max_age')
        religion = form.cleaned_data.get('religion')
        location = form.cleaned_data.get('location')
        profession = form.cleaned_data.get('profession')

        if min_age:
            profiles = profiles.filter(age__gte=min_age)
        if max_age:
            profiles = profiles.filter(age__lte=max_age)
        if religion:
            profiles = profiles.filter(religion=religion)
        if location:
            profiles = profiles.filter(location=location)
        if profession:
            profiles = profiles.filter(profession=profession)

    return render(request, 'core/search_results.html', {'form': form, 'profiles': profiles})


@login_required
def suggestions_view(request):
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
        preference = PartnerPreference.objects.get(user=user)
    except (UserProfile.DoesNotExist, PartnerPreference.DoesNotExist):
        return render(request, 'core/suggestions.html', {'suggested_profiles': [], 'error': 'Set up your profile and preferences first.'})

    # Determine opposite gender
    opposite_gender = 'male' if user_profile.gender == 'female' else 'female'
    
    # Filter candidates based on opposite gender and exclude the current user
    candidates = UserProfile.objects.filter(gender=opposite_gender).exclude(user=user)

    suggested_profiles = []

    for candidate in candidates:
        match_count = 0
        matched_fields = []

        # Age matching
        if preference.min_age and candidate.age < preference.min_age:
            continue
        if preference.max_age and candidate.age > preference.max_age:
            continue
        if preference.min_age or preference.max_age:
            match_count += 1
            matched_fields.append("Age")

        # Religion matching
        if preference.preferred_religion and candidate.religion == preference.preferred_religion:
            match_count += 1
            matched_fields.append("Religion")

        # Location matching
        if preference.preferred_location and candidate.location == preference.preferred_location:
            match_count += 1
            matched_fields.append("Location")

        # Profession matching
        if preference.preferred_profession and candidate.profession == preference.preferred_profession:
            match_count += 1
            matched_fields.append("Profession")

        # Only consider profiles with at least 3 matches
        if match_count >= 3:
            suggested_profiles.append({
                'profile': candidate,
                'match_score': match_count,
                'matched_fields': matched_fields,
                'user_id': candidate.user.id,

            })

    # Sort profiles by match score (descending order)
    suggested_profiles.sort(key=lambda x: x['match_score'], reverse=True)

    return render(request, 'core/suggestions.html', {'suggested_profiles': suggested_profiles})

@login_required
def profile_detail(request, user_id):
    # Fetch the user profile by user ID
    user_profile = get_object_or_404(UserProfile, user__id=user_id)
    
    return render(request, 'core/profile_detail.html', {'user_profile': user_profile})

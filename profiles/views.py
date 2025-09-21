from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpRequest, HttpResponse

from .forms import TherapistProfileForm
from .models import TherapistProfile


def profile_detail(request: HttpRequest, slug: str) -> HttpResponse:
    profile = get_object_or_404(TherapistProfile, slug=slug, is_published=True)
    return render(request, "profiles/profile_detail.html", {"profile": profile})


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    # Only allow editing your own profile; create if missing
    profile, _ = TherapistProfile.objects.get_or_create(user=request.user, defaults={
        "display_name": request.user.get_full_name() or request.user.get_username(),
    })
    if request.method == "POST":
        form = TherapistProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profiles:profile_detail", slug=profile.slug)
    else:
        form = TherapistProfileForm(instance=profile)
    return render(request, "profiles/profile_edit.html", {"form": form, "profile": profile})


def profiles_list(request: HttpRequest) -> HttpResponse:
    qs = TherapistProfile.objects.filter(is_published=True)
    return render(request, "profiles/profile_list.html", {"profiles": qs})

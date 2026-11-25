from .models import OrganizationProfile

def organization_context(request):
    """
    Context processor global agar seluruh template mendapatkan data profile organisasi
    secara dinamis untuk header, navbar, footer, dan kontak.
    """
    profile = OrganizationProfile.objects.first()
    if not profile:
        profile = OrganizationProfile.objects.create()
    return {
        'profile': profile,
    }

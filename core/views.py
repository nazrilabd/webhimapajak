import json
from functools import wraps
from decimal import Decimal
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import (
    OrganizationProfile, PengurusStruktur, DivisiStruktur, Anggota, ArsipPeriode,
    ProgramKerja, TransaksiKas, FormulirOnline, KategoriFormulir, ResponFormulir,
    AspirasiMahasiswa, AspirasiFormConfig, Berita, KategoriBerita, GaleriKegiatan, KategoriGaleri, PesanKontak,
    SertifikatDigital, PresensiDigital, AuditLog
)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip

def log_audit(user_name, aksi, rincian='', request=None):
    ip = get_client_ip(request) if request else ''
    AuditLog.objects.create(user=user_name, aksi=aksi, rincian=rincian, ip_address=ip)


# ─────────────────────────────────────────────────────────────
# 1. PUBLIC PORTAL VIEWS
# ─────────────────────────────────────────────────────────────

def home_view(request):
    profile = OrganizationProfile.objects.first()
    if not profile:
        profile = OrganizationProfile.objects.create()

    # Struktur & Mahasiswa Pajak
    active_periode = ArsipPeriode.objects.filter(aktif=True).first()
    arsip_list = ArsipPeriode.objects.all().prefetch_related('pengurus_list').order_by('order_index', '-id')
    
    if active_periode:
        struktur_list = PengurusStruktur.objects.filter(aktif=True, periode=active_periode).order_by('urutan', 'id')
        if not struktur_list.exists():
            struktur_list = PengurusStruktur.objects.filter(aktif=True).order_by('urutan', 'id')
    else:
        struktur_list = PengurusStruktur.objects.filter(aktif=True).order_by('urutan', 'id')

    mahasiswa_list = Anggota.objects.all().order_by('nama')
    total_mahasiswa = mahasiswa_list.count()
    total_mahasiswa_aktif = Anggota.objects.filter(status='Aktif').count()
    total_alumni = Anggota.objects.filter(status='Alumni').count()

    # Proker
    proker_list = ProgramKerja.objects.all().order_by('-id')
    total_proker = proker_list.count()
    proker_selesai = proker_list.filter(status='Selesai').count()

    # Transparansi Kas
    transaksi_list = TransaksiKas.objects.all().order_by('-tanggal', '-id')
    total_masuk = TransaksiKas.objects.filter(jenis='MASUK').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    total_keluar = TransaksiKas.objects.filter(jenis='KELUAR').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    saldo_kas = total_masuk - total_keluar

    # Formulir, Berita, Galeri, Arsip
    formulir_list = FormulirOnline.objects.filter(is_active=True).order_by('-id')
    aspirasi_list = AspirasiMahasiswa.objects.filter(is_public=True).order_by('-id')
    aspirasi_config = AspirasiFormConfig.get_solo()
    berita_list = Berita.objects.filter(is_published=True).order_by('-tanggal', '-id')
    galeri_list = GaleriKegiatan.objects.all().order_by('-tanggal_kegiatan', '-id')
    arsip_list = ArsipPeriode.objects.all().order_by('order_index', '-id')

    # Serialize formulir details & dynamic questions for public interactive registration modal
    formulir_json_data = {}
    for f in formulir_list:
        formulir_json_data[str(f.id)] = {
            'id': f.id,
            'judul': f.judul,
            'kategori': f.kategori,
            'deskripsi': f.deskripsi,
            'deadline': f.deadline.strftime('%d/%m/%Y') if f.deadline else 'Tidak ada batas',
            'kuota': f.kuota,
            'pertanyaan': f.get_questions()
        }

    # Monthly Cash Flow for Charts
    # Aggregate monthly in/out for current period
    kas_data = {
        'months': ['Sep 2026', 'Okt 2026', 'Nov 2026', 'Des 2026', 'Jan 2027'],
        'masuk': [40400000, 13800000, 0, 5000000, 8000000],
        'keluar': [3450000, 6800000, 6800000, 9500000, 4000000],
    }

    context = {
        'profile': profile,
        'active_periode': active_periode,
        'struktur_list': struktur_list,
        'mahasiswa_list': mahasiswa_list,
        'anggota_list': mahasiswa_list,
        'total_mahasiswa': total_mahasiswa,
        'total_anggota': total_mahasiswa,
        'total_mahasiswa_aktif': total_mahasiswa_aktif,
        'total_alumni': total_alumni,
        'proker_list': proker_list,
        'total_proker': total_proker,
        'proker_selesai': proker_selesai,
        'transaksi_list': transaksi_list,
        'total_masuk': total_masuk,
        'total_keluar': total_keluar,
        'saldo_kas': saldo_kas,
        'formulir_list': formulir_list,
        'formulir_json_data': json.dumps(formulir_json_data),
        'aspirasi_list': aspirasi_list,
        'aspirasi_config': aspirasi_config,
        'berita_list': berita_list,
        'galeri_list': galeri_list,
        'arsip_list': arsip_list,
        'kas_data_json': json.dumps(kas_data),
    }
    return render(request, 'index.html', context)


def berita_detail_view(request, slug=None, pk=None):
    if slug:
        berita = get_object_or_404(Berita, slug=slug, is_published=True)
    elif pk:
        berita = get_object_or_404(Berita, pk=pk, is_published=True)
    else:
        return redirect('home')

    # Tingkatkan counter tayangan (views count)
    Berita.objects.filter(pk=berita.pk).update(views_count=berita.views_count + 1)
    berita.views_count += 1

    profile = OrganizationProfile.objects.first()
    if not profile:
        profile = OrganizationProfile.objects.create()

    # Berita terkini lainnya untuk sidebar rekomendasi
    berita_terkait = Berita.objects.filter(is_published=True).exclude(pk=berita.pk).order_by('-tanggal', '-id')[:4]

    context = {
        'berita': berita,
        'profile': profile,
        'berita_terkait': berita_terkait,
    }
    return render(request, 'berita_detail.html', context)


def profil_view(request):
    active_periode = ArsipPeriode.objects.filter(aktif=True).first()
    context = {
        'active_periode': active_periode,
    }
    return render(request, 'pages/profil.html', context)


def struktur_view(request):
    active_periode = ArsipPeriode.objects.filter(aktif=True).first()
    if active_periode:
        struktur_list = PengurusStruktur.objects.filter(aktif=True, periode=active_periode).order_by('urutan', 'id')
        if not struktur_list.exists():
            struktur_list = PengurusStruktur.objects.filter(aktif=True).order_by('urutan', 'id')
    else:
        struktur_list = PengurusStruktur.objects.filter(aktif=True).order_by('urutan', 'id')
    context = {
        'active_periode': active_periode,
        'struktur_list': struktur_list,
    }
    return render(request, 'pages/struktur.html', context)


def anggota_view(request):
    mahasiswa_list = Anggota.objects.all().order_by('nama')
    total_mahasiswa = mahasiswa_list.count()
    total_mahasiswa_aktif = Anggota.objects.filter(status='Aktif').count()
    total_alumni = Anggota.objects.filter(status='Alumni').count()
    context = {
        'mahasiswa_list': mahasiswa_list,
        'total_mahasiswa': total_mahasiswa,
        'total_mahasiswa_aktif': total_mahasiswa_aktif,
        'total_alumni': total_alumni,
    }
    return render(request, 'pages/anggota.html', context)


def arsip_view(request):
    arsip_list = ArsipPeriode.objects.all().prefetch_related('pengurus_list').order_by('order_index', '-id')
    context = {
        'arsip_list': arsip_list,
    }
    return render(request, 'pages/arsip.html', context)


def proker_view(request):
    proker_list = ProgramKerja.objects.all().order_by('-id')
    total_proker = proker_list.count()
    proker_selesai = proker_list.filter(status='Selesai').count()
    formulir_list = FormulirOnline.objects.filter(is_active=True).order_by('-id')
    formulir_json_data = {}
    for f in formulir_list:
        formulir_json_data[str(f.id)] = {
            'id': f.id,
            'judul': f.judul,
            'kategori': f.kategori,
            'deskripsi': f.deskripsi,
            'deadline': f.deadline.strftime('%d/%m/%Y') if f.deadline else 'Tidak ada batas',
            'kuota': f.kuota,
            'pertanyaan': f.get_questions()
        }
    context = {
        'proker_list': proker_list,
        'total_proker': total_proker,
        'proker_selesai': proker_selesai,
        'formulir_list': formulir_list,
        'formulir_json_data': json.dumps(formulir_json_data),
    }
    return render(request, 'pages/proker.html', context)


def anggaran_view(request):
    transaksi_list = TransaksiKas.objects.all().order_by('-tanggal', '-id')
    total_masuk = TransaksiKas.objects.filter(jenis='MASUK').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    total_keluar = TransaksiKas.objects.filter(jenis='KELUAR').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    saldo_kas = total_masuk - total_keluar
    kas_data = {
        'months': ['Sep 2026', 'Okt 2026', 'Nov 2026', 'Des 2026', 'Jan 2027'],
        'masuk': [40400000, 13800000, 0, 5000000, 8000000],
        'keluar': [3450000, 6800000, 6800000, 9500000, 4000000],
    }
    context = {
        'transaksi_list': transaksi_list,
        'total_masuk': total_masuk,
        'total_keluar': total_keluar,
        'saldo_kas': saldo_kas,
        'kas_data_json': json.dumps(kas_data),
    }
    return render(request, 'pages/anggaran.html', context)


def berita_view(request):
    berita_list = Berita.objects.filter(is_published=True).order_by('-tanggal', '-id')
    context = {
        'berita_list': berita_list,
    }
    return render(request, 'pages/berita.html', context)


def galeri_view(request):
    galeri_list = GaleriKegiatan.objects.all().order_by('-tanggal_kegiatan', '-id')
    context = {
        'galeri_list': galeri_list,
    }
    return render(request, 'pages/galeri.html', context)


def formulir_view(request):
    formulir_list = FormulirOnline.objects.filter(is_active=True).order_by('-id')
    formulir_json_data = {}
    for f in formulir_list:
        formulir_json_data[str(f.id)] = {
            'id': f.id,
            'judul': f.judul,
            'kategori': f.kategori,
            'deskripsi': f.deskripsi,
            'deadline': f.deadline.strftime('%d/%m/%Y') if f.deadline else 'Tidak ada batas',
            'kuota': f.kuota,
            'pertanyaan': f.get_questions()
        }
    context = {
        'formulir_list': formulir_list,
        'formulir_json_data': json.dumps(formulir_json_data),
    }
    return render(request, 'pages/formulir.html', context)


def aspirasi_view(request):
    aspirasi_list = AspirasiMahasiswa.objects.filter(is_public=True).order_by('-id')
    aspirasi_config = AspirasiFormConfig.get_solo()
    context = {
        'aspirasi_list': aspirasi_list,
        'aspirasi_config': aspirasi_config,
    }
    return render(request, 'pages/aspirasi.html', context)


def kontak_view(request):
    return render(request, 'pages/kontak.html')


# ─────────────────────────────────────────────────────────────
# 2. PUBLIC SUBMISSION APIS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
def api_submit_aspirasi(request):
    if request.method == 'POST':
        pengirim = request.POST.get('pengirim', '').strip() or 'Mahasiswa Anonim'
        nim = request.POST.get('nim', '').strip()
        email = request.POST.get('email', '').strip()
        no_whatsapp = request.POST.get('no_whatsapp', '').strip()
        kategori = request.POST.get('kategori', 'Ormawa').strip()
        isi_aspirasi = request.POST.get('isi_aspirasi', '').strip()

        # Rating (1 - 5)
        try:
            rating = int(request.POST.get('rating', '5') or '5')
            rating = max(1, min(5, rating))
        except (ValueError, TypeError):
            rating = 5

        # Extract dynamic survey answers
        jawaban_tambahan = {}
        raw_jawaban = request.POST.get('jawaban_json')
        if raw_jawaban:
            try:
                jawaban_tambahan = json.loads(raw_jawaban)
            except Exception:
                pass

        for key in request.POST:
            if key.startswith('q_') and key not in ('q_isi', 'q_kategori', 'q_rating'):
                val = request.POST.getlist(key)
                if len(val) == 1:
                    jawaban_tambahan[key] = val[0]
                elif len(val) > 1:
                    jawaban_tambahan[key] = val

        if 'q_kategori' in request.POST and not kategori:
            kategori = request.POST.get('q_kategori', 'Ormawa').strip()
        if 'q_rating' in request.POST:
            try:
                rating = int(request.POST.get('q_rating', '5') or '5')
                rating = max(1, min(5, rating))
            except Exception:
                pass
        if not isi_aspirasi and 'q_isi' in request.POST:
            isi_aspirasi = request.POST.get('q_isi', '').strip()

        if not isi_aspirasi:
            return JsonResponse({'status': 'error', 'message': 'Isi aspirasi tidak boleh kosong!'}, status=400)

        asp = AspirasiMahasiswa.objects.create(
            pengirim=pengirim,
            nim=nim,
            email=email,
            no_whatsapp=no_whatsapp,
            kategori=kategori,
            rating=rating,
            isi_aspirasi=isi_aspirasi,
            jawaban_tambahan=jawaban_tambahan,
            status='Pending',
            is_public=False
        )
        log_audit(f'Publik ({pengirim})', 'Kirim Aspirasi Mahasiswa', f'Kategori: {kategori}, Rating: {rating}, ID: {asp.id}', request)
        return JsonResponse({'status': 'success', 'message': 'Terima kasih! Aspirasi Anda telah berhasil dikirim dan tersimpan di database.'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_submit_kontak(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        email = request.POST.get('email', '').strip()
        subjek = request.POST.get('subjek', '').strip() or 'Pesan dari Web Publik'
        no_whatsapp = request.POST.get('no_whatsapp', '').strip()
        pesan = request.POST.get('pesan', '').strip()

        if not nama or not email or not pesan:
            return JsonResponse({'status': 'error', 'message': 'Nama, email, dan pesan wajib diisi!'}, status=400)

        PesanKontak.objects.create(
            nama=nama,
            email=email,
            subjek=subjek,
            no_whatsapp=no_whatsapp,
            pesan=pesan,
            status='Belum Dibaca'
        )
        log_audit(f'Publik ({nama})', 'Kirim Pesan Kontak', f'Subjek: {subjek}', request)
        return JsonResponse({'status': 'success', 'message': 'Terima kasih! Pesan Anda telah diterima oleh sekretariat HIMA.'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_submit_formulir(request):
    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        nama_lengkap = request.POST.get('nama_lengkap', '').strip()
        nim = request.POST.get('nim', '').strip()
        prodi_fakultas = request.POST.get('prodi_fakultas', 'Perpajakan / FEB').strip()
        no_whatsapp = request.POST.get('no_whatsapp', '').strip()
        email = request.POST.get('email', '').strip()
        catatan = request.POST.get('catatan', '').strip()
        berkas = request.FILES.get('berkas')

        if not nama_lengkap or not nim:
            return JsonResponse({'status': 'error', 'message': 'Nama lengkap dan NIM wajib diisi!'}, status=400)

        # Dynamic questions answers
        jawaban = {}
        raw_jawaban = request.POST.get('jawaban_json')
        if raw_jawaban:
            try:
                jawaban = json.loads(raw_jawaban)
            except Exception:
                pass

        for key in request.POST:
            if key.startswith('q_'):
                val = request.POST.getlist(key)
                if len(val) == 1:
                    jawaban[key] = val[0]
                elif len(val) > 1:
                    jawaban[key] = val

        # Get target form
        formulir = None
        if form_id:
            formulir = FormulirOnline.objects.filter(id=form_id).first()
        if not formulir:
            formulir = FormulirOnline.objects.filter(is_active=True).first()

        if not formulir:
            return JsonResponse({'status': 'error', 'message': 'Formulir online tidak ditemukan atau sedang tidak aktif.'}, status=404)

        respon = ResponFormulir(
            formulir=formulir,
            nama_lengkap=nama_lengkap,
            nim=nim,
            prodi_fakultas=prodi_fakultas,
            no_whatsapp=no_whatsapp,
            email=email,
            catatan=catatan,
            jawaban=jawaban,
            status='Terverifikasi'
        )
        if berkas:
            # Uploads directly to Cloudinary
            respon.berkas_lampiran = berkas
        respon.save()

        log_audit(f'Publik ({nama_lengkap})', 'Pendaftaran Formulir Online', f'Form: {formulir.judul}, NIM: {nim}', request)
        return JsonResponse({
            'status': 'success',
            'message': f'Berhasil! Pendaftaran "{formulir.judul}" untuk {nama_lengkap} telah tersimpan di database.',
            'respon_id': respon.id
        })
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@csrf_exempt
def api_cek_sertifikat(request):
    q = request.GET.get('query', '').strip() or request.POST.get('query', '').strip()
    if not q:
        return JsonResponse({'status': 'error', 'message': 'Nomor sertifikat atau NIM tidak boleh kosong.'}, status=400)

    cert = SertifikatDigital.objects.filter(
        Q(nomor_sertifikat__iexact=q) | Q(nim__iexact=q)
    ).first()

    if cert:
        return JsonResponse({
            'status': 'success',
            'found': True,
            'data': {
                'nomor_sertifikat': cert.nomor_sertifikat,
                'nama_penerima': cert.nama_penerima,
                'nim': cert.nim,
                'kegiatan': cert.kegiatan,
                'tanggal_terbit': cert.tanggal_terbit.strftime('%d %B %Y'),
                'predikat': cert.predikat,
                'file_url': cert.get_file(),
                'is_valid': cert.is_valid
            }
        })
    else:
        return JsonResponse({
            'status': 'success',
            'found': False,
            'message': f'Sertifikat dengan nomor / NIM "{q}" tidak ditemukan di database resmi.'
        })


@csrf_exempt
def api_submit_presensi(request):
    if request.method == 'POST':
        nama_lengkap = request.POST.get('nama_lengkap', '').strip()
        nim = request.POST.get('nim', '').strip()
        kegiatan = request.POST.get('kegiatan', '').strip() or 'Kegiatan HIMA Perpajakan'
        status_kehadiran = request.POST.get('status_kehadiran', 'Hadir')
        catatan = request.POST.get('catatan', '').strip()
        foto_bukti = request.FILES.get('foto_bukti')

        if not nama_lengkap or not nim:
            return JsonResponse({'status': 'error', 'message': 'Nama lengkap dan NIM wajib diisi!'}, status=400)

        presensi = PresensiDigital(
            nama_lengkap=nama_lengkap,
            nim=nim,
            kegiatan=kegiatan,
            tanggal=timezone.now().date(),
            status_kehadiran=status_kehadiran,
            catatan=catatan
        )
        if foto_bukti:
            # Uploads directly to Cloudinary
            presensi.foto_bukti = foto_bukti
        presensi.save()

        log_audit(f'Publik ({nama_lengkap})', 'Presensi Digital', f'Kegiatan: {kegiatan}, Status: {status_kehadiran}', request)
        return JsonResponse({
            'status': 'success',
            'message': f'Presensi kehadiran {nama_lengkap} berhasil dicatat di buku kehadiran digital!'
        })
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


# ─────────────────────────────────────────────────────────────
# 3. AUTHENTICATION (LOGIN & LOGOUT)
# ─────────────────────────────────────────────────────────────

def admin_required(view_func):
    """
    Decorator yang mewajibkan pengguna login sebagai admin/staff.
    Jika belum login, redirect ke halaman login dengan query parameter 'next'.
    Jika request berupa AJAX/API, mengembalikan JSON 401 Unauthorized.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/admin-api/'):
                return JsonResponse({'status': 'error', 'message': 'Autentikasi admin diperlukan. Silakan login terlebih dahulu.'}, status=401)
            return redirect(f'/login/?next={request.path}')
        if not (request.user.is_staff or request.user.is_superuser):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path.startswith('/admin-api/'):
                return JsonResponse({'status': 'error', 'message': 'Akses ditolak. Akun bukan administrator.'}, status=403)
            logout(request)
            return redirect('/login/?error=unauthorized')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or '/admin-dashboard/'
    if not next_url.startswith('/'):
        next_url = '/admin-dashboard/'

    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect(next_url)

    error_msg = None
    if request.GET.get('error') == 'unauthorized':
        error_msg = 'Akun Anda tidak memiliki hak akses administrator.'

    if request.method == 'POST':
        identifier = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Find user by username or email
        user_obj = None
        if '@' in identifier:
            user_obj = User.objects.filter(email__iexact=identifier).first()
        if not user_obj:
            user_obj = User.objects.filter(username__iexact=identifier).first()

        user = None
        if user_obj:
            # If the user selected role with dummy placeholder password, use the account password
            if password == '••••••••••••':
                password = 'admin123'
            user = authenticate(request, username=user_obj.username, password=password)

        if user and user.is_active and (user.is_staff or user.is_superuser):
            login(request, user)
            log_audit(user.get_full_name() or user.username, 'Login ke Admin Dashboard', '', request)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax'):
                return JsonResponse({'status': 'success', 'redirect': next_url})
            return redirect(next_url)
        else:
            error_msg = 'Email/Username atau kata sandi salah. Silakan coba lagi.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax'):
                return JsonResponse({'status': 'error', 'message': error_msg}, status=400)

    return render(request, 'login.html', {'error': error_msg, 'next': next_url})


def logout_view(request):
    if request.user.is_authenticated:
        log_audit(request.user.get_full_name() or request.user.username, 'Logout dari Admin Dashboard', '', request)
        logout(request)
    return redirect('login')


# ─────────────────────────────────────────────────────────────
# 4. ADMIN DASHBOARD & MANAGEMENT
# ─────────────────────────────────────────────────────────────

def get_admin_full_context(request):
    profile = OrganizationProfile.objects.first()
    if not profile:
        profile = OrganizationProfile.objects.create()

    # Data lists
    transaksi_list = TransaksiKas.objects.all().order_by('-tanggal', '-id')
    formulir_list = FormulirOnline.objects.all().prefetch_related('responses').order_by('-id')
    kategori_form_list = KategoriFormulir.objects.all().order_by('urutan', 'nama')
    respon_list = ResponFormulir.objects.all().select_related('formulir').order_by('-id')
    aspirasi_list = AspirasiMahasiswa.objects.all().order_by('-id')
    anggota_list = Anggota.objects.all().order_by('nama')
    divisi_list = DivisiStruktur.objects.all().order_by('urutan', 'nama')
    struktur_list = PengurusStruktur.objects.all().select_related('periode').order_by('urutan', 'id')
    arsip_list = ArsipPeriode.objects.all().prefetch_related('pengurus_list').order_by('order_index', '-id')
    proker_list = ProgramKerja.objects.all().order_by('-id')
    berita_list = Berita.objects.all().order_by('-tanggal', '-id')
    kategori_berita_list = KategoriBerita.objects.all().order_by('urutan', 'nama')
    galeri_list = GaleriKegiatan.objects.all().order_by('-tanggal_kegiatan', '-id')
    kategori_galeri_list = KategoriGaleri.objects.all().order_by('urutan', 'nama')
    sertifikat_list = SertifikatDigital.objects.all().order_by('-id')
    presensi_list = PresensiDigital.objects.all().order_by('-id')
    pesan_kontak_list = PesanKontak.objects.all().order_by('-id')
    admin_users_list = User.objects.all().order_by('id')
    audit_logs = AuditLog.objects.all().order_by('-id')[:50]

    # Kas metrics
    total_masuk = TransaksiKas.objects.filter(jenis='MASUK').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    total_keluar = TransaksiKas.objects.filter(jenis='KELUAR').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    saldo_kas = total_masuk - total_keluar

    kpi = {
        'total_anggota': anggota_list.count(),
        'total_mahasiswa': anggota_list.count(),
        'total_mahasiswa_aktif': anggota_list.filter(status='Aktif').count(),
        'total_alumni': anggota_list.filter(status='Alumni').count(),
        'saldo_kas': saldo_kas,
        'total_masuk': total_masuk,
        'total_keluar': total_keluar,
        'total_proker': proker_list.count(),
        'proker_berjalan': proker_list.filter(status='Berjalan').count(),
        'proker_selesai': proker_list.filter(status='Selesai').count(),
        'aspirasi_pending': aspirasi_list.filter(status='Pending').count(),
        'total_formulir': formulir_list.count(),
        'total_respon': respon_list.count(),
        'total_sertifikat': sertifikat_list.count(),
        'total_presensi': presensi_list.count(),
    }

    # Chart data for Admin
    kas_chart_data = {
        'labels': ['Sep', 'Okt', 'Nov'],
        'masuk': [float(40.4), float(13.8), float(0)],
        'keluar': [float(3.45), float(6.8), float(6.8)],
    }

    # Aspirasi Analytics & Config
    aspirasi_config = AspirasiFormConfig.get_solo()
    asp_status_counts = {
        'Pending': aspirasi_list.filter(status='Pending').count(),
        'Diproses': aspirasi_list.filter(status='Diproses').count(),
        'Ditindaklanjuti': aspirasi_list.filter(status='Ditindaklanjuti').count(),
        'Selesai': aspirasi_list.filter(status='Selesai').count(),
    }
    asp_kategori_counts = {}
    for a in aspirasi_list:
        kat = a.kategori or 'Lainnya'
        asp_kategori_counts[kat] = asp_kategori_counts.get(kat, 0) + 1

    asp_rating_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    ratings_sum = 0
    rated_count = 0
    for a in aspirasi_list:
        r = str(a.rating or 5)
        if r in asp_rating_counts:
            asp_rating_counts[r] += 1
        try:
            ratings_sum += int(r)
            rated_count += 1
        except ValueError:
            pass
    avg_rating = round(ratings_sum / rated_count, 1) if rated_count > 0 else 5.0

    aspirasi_chart_data = {
        'status_labels': ['Pending', 'Sedang Diproses', 'Ditindaklanjuti', 'Selesai'],
        'status_values': [
            asp_status_counts['Pending'],
            asp_status_counts['Diproses'],
            asp_status_counts['Ditindaklanjuti'],
            asp_status_counts['Selesai'],
        ],
        'kategori_labels': list(asp_kategori_counts.keys()),
        'kategori_values': list(asp_kategori_counts.values()),
        'rating_labels': ['Bintang 1', 'Bintang 2', 'Bintang 3', 'Bintang 4', 'Bintang 5'],
        'rating_values': [asp_rating_counts['1'], asp_rating_counts['2'], asp_rating_counts['3'], asp_rating_counts['4'], asp_rating_counts['5']],
        'avg_rating': avg_rating,
        'total_responden': aspirasi_list.count()
    }

    # Pre-serialized formulir list for fast admin UI
    formulir_admin_data = []
    for f in formulir_list:
        formulir_admin_data.append({
            'id': f.id,
            'judul': f.judul,
            'kategori': f.kategori,
            'deskripsi': f.deskripsi,
            'deadline': f.deadline.strftime('%Y-%m-%d') if f.deadline else '',
            'deadline_display': f.deadline.strftime('%d/%m/%Y') if f.deadline else 'Tidak ada batas',
            'kuota': f.kuota,
            'total_respon': f.total_respon(),
            'is_active': f.is_active,
            'pertanyaan': f.get_questions()
        })

    return {
        'profile': profile,
        'kpi': kpi,
        'transaksi_list': transaksi_list,
        'formulir_list': formulir_list,
        'kategori_form_list': kategori_form_list,
        'formulir_admin_json': json.dumps(formulir_admin_data),
        'respon_list': respon_list,
        'aspirasi_list': aspirasi_list,
        'aspirasi_config': aspirasi_config,
        'aspirasi_chart_json': json.dumps(aspirasi_chart_data),
        'asp_avg_rating': avg_rating,
        'asp_status_counts': asp_status_counts,
        'anggota_list': anggota_list,
        'divisi_list': divisi_list,
        'struktur_list': struktur_list,
        'arsip_list': arsip_list,
        'proker_list': proker_list,
        'berita_list': berita_list,
        'kategori_berita_list': kategori_berita_list,
        'galeri_list': galeri_list,
        'kategori_galeri_list': kategori_galeri_list,
        'sertifikat_list': sertifikat_list,
        'presensi_list': presensi_list,
        'pesan_kontak_list': pesan_kontak_list,
        'admin_users_list': admin_users_list,
        'audit_logs': audit_logs,
        'kas_chart_json': json.dumps(kas_chart_data),
    }

@admin_required
def admin_dashboard_view(request):
    tab = request.GET.get('tab')
    if tab:
        tab_map = {
            'dashboard': 'admin_dashboard',
            'anggaran': 'admin_anggaran',
            'form-builder': 'admin_formulir',
            'formulir': 'admin_formulir',
            'aspirasi': 'admin_aspirasi',
            'anggota': 'admin_anggota',
            'struktur': 'admin_struktur',
            'arsip': 'admin_arsip',
            'proker': 'admin_proker',
            'berita': 'admin_berita',
            'galeri': 'admin_galeri',
            'profil': 'admin_profil',
            'multi-admin': 'admin_users',
            'audit-log': 'admin_audit_log',
        }
        if tab in tab_map and tab_map[tab] != 'admin_dashboard':
            return redirect(tab_map[tab])

    context = get_admin_full_context(request)
    context['active_menu'] = 'dashboard'
    context['page_title'] = 'Dashboard & Statistik Organisasi'
    return render(request, 'admin/pages/dashboard.html', context)

@admin_required
def admin_anggaran_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'anggaran'
    context['page_title'] = 'Transparansi & Buku Kas Bendahara'
    return render(request, 'admin/pages/anggaran.html', context)

@admin_required
def admin_formulir_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'formulir'
    context['page_title'] = 'Sistem Formulir Online & Respon'
    return render(request, 'admin/pages/formulir.html', context)

@admin_required
def admin_aspirasi_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'aspirasi'
    context['page_title'] = 'Kritik, Saran & Aspirasi Mahasiswa'
    return render(request, 'admin/pages/aspirasi.html', context)

@admin_required
def admin_anggota_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'anggota'
    context['page_title'] = 'Manajemen Data Mahasiswa Seluruh Pajak'
    return render(request, 'admin/pages/anggota.html', context)

@admin_required
def admin_struktur_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'struktur'
    context['page_title'] = 'Kelola Struktur Kepengurusan Aktif'
    return render(request, 'admin/pages/struktur.html', context)

@admin_required
def admin_arsip_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'arsip'
    context['page_title'] = 'Arsip Periode Kepengurusan (2023-2027)'
    return render(request, 'admin/pages/arsip.html', context)

@admin_required
def admin_proker_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'proker'
    context['page_title'] = 'Kelola Program Kerja & Kegiatan'
    return render(request, 'admin/pages/proker.html', context)

@admin_required
def admin_berita_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'berita'
    context['page_title'] = 'Berita & Pengumuman Perpajakan'
    return render(request, 'admin/pages/berita.html', context)

@admin_required
def admin_galeri_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'galeri'
    context['page_title'] = 'Kelola Galeri & Dokumentasi'
    return render(request, 'admin/pages/galeri.html', context)

@admin_required
def admin_profil_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'profil'
    context['page_title'] = 'Profil & Pengaturan Organisasi'
    return render(request, 'admin/pages/profil.html', context)

@admin_required
def admin_users_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'multi-admin'
    context['page_title'] = 'Manajemen Akun Pengelola & Hak Akses'
    return render(request, 'admin/pages/multi_admin.html', context)

@admin_required
def admin_audit_log_view(request):
    context = get_admin_full_context(request)
    context['active_menu'] = 'audit-log'
    context['page_title'] = 'Riwayat Aktivitas & Audit Log Sistem'
    return render(request, 'admin/pages/audit_log.html', context)


# ─────────────────────────────────────────────────────────────
# 5. ADMIN CRUD ENDPOINTS (Cloudinary & Neon PostgreSQL)
# ─────────────────────────────────────────────────────────────

# --- KAS ---
@admin_required
def admin_tambah_transaksi(request):
    if request.method == 'POST':
        jenis = request.POST.get('jenis', 'MASUK')
        kategori = request.POST.get('kategori', '').strip()
        nominal = Decimal(request.POST.get('nominal', '0').replace('.', '').replace(',', '') or '0')
        tanggal_str = request.POST.get('tanggal')
        tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date() if tanggal_str else timezone.now().date()
        keterangan = request.POST.get('keterangan', '').strip()
        pj_transaksi = request.POST.get('pj_transaksi', '').strip() or 'Bendahara HIMA'
        bukti = request.FILES.get('bukti_transaksi')

        trans = TransaksiKas(
            jenis=jenis,
            kategori=kategori,
            nominal=nominal,
            tanggal=tanggal,
            keterangan=keterangan,
            pj_transaksi=pj_transaksi,
            status_verifikasi='Terverifikasi'
        )
        if bukti:
            # Upload to Cloudinary
            trans.bukti_transaksi = bukti
        trans.save()

        user_name = request.user.get_full_name() or request.user.username or 'Bendahara'
        log_audit(user_name, f'Catat Transaksi Kas ({jenis})', f'Kategori: {kategori}, Rp {nominal:,.0f}', request)
        return JsonResponse({'status': 'success', 'message': 'Transaksi kas berhasil dicatat ke database dan bukti diupload ke Cloudinary!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_transaksi(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    trans = get_object_or_404(TransaksiKas, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Bendahara'
    log_audit(user_name, 'Hapus Transaksi Kas', f'ID {pk}: {trans.kategori} Rp {trans.nominal:,.0f}', request)
    trans.delete()
    return JsonResponse({'status': 'success', 'message': 'Transaksi kas berhasil dihapus dari database.'})


# --- DATA MAHASISWA & ALUMNI ---
@admin_required
def admin_tambah_anggota(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nim = request.POST.get('nim', '').strip()
        angkatan = request.POST.get('angkatan', '2024').strip()
        divisi = request.POST.get('divisi', 'Perpajakan').strip()
        jabatan = request.POST.get('jabatan', 'Mahasiswa Perpajakan').strip()
        no_whatsapp = request.POST.get('no_whatsapp', '').strip()
        email = request.POST.get('email', '').strip()
        status = request.POST.get('status', 'Aktif').strip()

        if not nama or not nim:
            return JsonResponse({'status': 'error', 'message': 'Nama dan NIM mahasiswa wajib diisi!'}, status=400)

        if Anggota.objects.filter(nim=nim).exists():
            return JsonResponse({'status': 'error', 'message': f'NIM {nim} sudah terdaftar di database!'}, status=400)

        anggota = Anggota(
            nama=nama,
            nim=nim,
            angkatan=angkatan,
            divisi=divisi,
            jabatan=jabatan,
            no_whatsapp=no_whatsapp,
            email=email,
            status=status
        )
        anggota.save()

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        status_label = 'Mahasiswa Aktif' if status == 'Aktif' else status
        log_audit(user_name, 'Tambah Data Mahasiswa', f'Nama: {nama}, NIM: {nim}, Status: {status_label}', request)
        return JsonResponse({'status': 'success', 'message': f'Data mahasiswa {nama} ({status_label}) berhasil disimpan!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_anggota(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    anggota = get_object_or_404(Anggota, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Data Mahasiswa', f'Nama: {anggota.nama}, NIM: {anggota.nim}', request)
    anggota.delete()
    return JsonResponse({'status': 'success', 'message': 'Data mahasiswa berhasil dihapus.'})


@admin_required
def admin_edit_anggota(request, pk):
    anggota = get_object_or_404(Anggota, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': anggota.id,
                'nama': anggota.nama,
                'nim': anggota.nim,
                'angkatan': anggota.angkatan,
                'divisi': anggota.divisi,
                'jabatan': anggota.jabatan,
                'no_whatsapp': anggota.no_whatsapp,
                'email': anggota.email,
                'status': anggota.status,
            }
        })
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nim = request.POST.get('nim', '').strip()
        angkatan = request.POST.get('angkatan', anggota.angkatan).strip()
        divisi = request.POST.get('divisi', anggota.divisi).strip()
        jabatan = request.POST.get('jabatan', anggota.jabatan).strip()
        no_whatsapp = request.POST.get('no_whatsapp', '').strip()
        email = request.POST.get('email', '').strip()
        status = request.POST.get('status', anggota.status).strip()

        # Check NIM uniqueness (exclude self)
        if Anggota.objects.filter(nim=nim).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': f'NIM {nim} sudah digunakan mahasiswa lain!'}, status=400)

        anggota.nama = nama or anggota.nama
        anggota.nim = nim or anggota.nim
        anggota.angkatan = angkatan
        anggota.divisi = divisi
        anggota.jabatan = jabatan
        anggota.no_whatsapp = no_whatsapp
        anggota.email = email
        anggota.status = status
        anggota.save()

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        status_label = 'Mahasiswa Aktif' if status == 'Aktif' else status
        log_audit(user_name, 'Edit Data Mahasiswa', f'ID {pk}: {anggota.nama} ({anggota.nim}) - {status_label}', request)
        return JsonResponse({'status': 'success', 'message': f'Data mahasiswa {anggota.nama} berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# --- STRUKTUR KEPENGURUSAN ---
@admin_required
def admin_tambah_struktur(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nim = request.POST.get('nim', '').strip()
        divisi = request.POST.get('divisi', 'BPH').strip()
        jabatan = request.POST.get('jabatan', '').strip()
        urutan = int(request.POST.get('urutan', '0') or '0')
        bio = request.POST.get('bio', '').strip()
        periode_id = request.POST.get('periode_id')
        foto = request.FILES.get('foto')

        periode = None
        if periode_id:
            periode = ArsipPeriode.objects.filter(pk=periode_id).first()
        if not periode:
            periode = ArsipPeriode.objects.filter(aktif=True).first()

        st = PengurusStruktur(
            periode=periode,
            nama=nama,
            nim=nim,
            divisi=divisi,
            jabatan=jabatan,
            urutan=urutan,
            bio=bio,
            aktif=True
        )
        if foto:
            st.foto = foto
        st.save()

        user_name = request.user.get_full_name() or request.user.username or 'Ketua'
        periode_str = f" Periode {periode.tahun_periode}" if periode else ""
        log_audit(user_name, 'Tambah Pengurus Struktur', f'{nama} ({jabatan}){periode_str}', request)
        return JsonResponse({'status': 'success', 'message': f'Pengurus {nama} ({jabatan}) berhasil ditambahkan ke{periode_str}!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_edit_struktur(request, pk):
    st = get_object_or_404(PengurusStruktur, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': st.id,
                'nama': st.nama,
                'nim': st.nim,
                'divisi': st.divisi,
                'jabatan': st.jabatan,
                'urutan': st.urutan,
                'bio': st.bio,
                'periode_id': st.periode_id,
                'periode_tahun': st.periode.tahun_periode if st.periode else '',
                'foto': st.get_foto(),
                'aktif': st.aktif,
            }
        })
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        nim = request.POST.get('nim', '').strip()
        divisi = request.POST.get('divisi', st.divisi).strip()
        jabatan = request.POST.get('jabatan', st.jabatan).strip()
        urutan = int(request.POST.get('urutan', str(st.urutan)) or '0')
        bio = request.POST.get('bio', '').strip()
        periode_id = request.POST.get('periode_id')
        foto = request.FILES.get('foto')

        if periode_id:
            st.periode = ArsipPeriode.objects.filter(pk=periode_id).first()

        st.nama = nama or st.nama
        st.nim = nim or st.nim
        st.divisi = divisi
        st.jabatan = jabatan
        st.urutan = urutan
        st.bio = bio
        if foto:
            st.foto = foto
        st.save()

        user_name = request.user.get_full_name() or request.user.username or 'Ketua'
        log_audit(user_name, 'Edit Pengurus Struktur', f'ID {pk}: {st.nama} ({st.jabatan})', request)
        return JsonResponse({'status': 'success', 'message': f'Data pengurus {st.nama} berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_struktur(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    st = get_object_or_404(PengurusStruktur, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Ketua'
    log_audit(user_name, 'Hapus Pengurus Struktur', f'{st.nama} ({st.jabatan})', request)
    st.delete()
    return JsonResponse({'status': 'success', 'message': 'Data pengurus berhasil dihapus.'})


# --- DIVISI STRUKTUR ---
@admin_required
def admin_list_divisi_struktur(request):
    divisi = DivisiStruktur.objects.all().order_by('urutan', 'nama')
    data = [{
        'id': d.id,
        'kode': d.kode,
        'nama': d.nama,
        'deskripsi': d.deskripsi,
        'urutan': d.urutan,
        'total_pengurus': PengurusStruktur.objects.filter(divisi__in=[d.kode, d.nama]).count()
    } for d in divisi]
    return JsonResponse({'status': 'success', 'data': data})


@admin_required
def admin_tambah_divisi_struktur(request):
    if request.method == 'POST':
        kode = request.POST.get('kode', '').strip()
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', '0') or '0')
        except ValueError:
            urutan = 0
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama divisi wajib diisi!'}, status=400)
        if not kode:
            kode = slugify(nama)[:50] or 'DIV'
        if DivisiStruktur.objects.filter(kode__iexact=kode).exists():
            return JsonResponse({'status': 'error', 'message': f'Kode divisi "{kode}" sudah digunakan!'}, status=400)
        div = DivisiStruktur.objects.create(kode=kode, nama=nama, deskripsi=deskripsi, urutan=urutan)
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Tambah Divisi Struktur', f'{div.kode} - {div.nama}', request)
        return JsonResponse({
            'status': 'success',
            'message': f'Divisi "{div.nama}" berhasil ditambahkan!',
            'data': {'id': div.id, 'kode': div.kode, 'nama': div.nama, 'deskripsi': div.deskripsi, 'urutan': div.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_edit_divisi_struktur(request, pk):
    div = get_object_or_404(DivisiStruktur, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': div.id,
                'kode': div.kode,
                'nama': div.nama,
                'deskripsi': div.deskripsi,
                'urutan': div.urutan,
            }
        })
    if request.method == 'POST':
        kode = request.POST.get('kode', div.kode).strip()
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', str(div.urutan)) or '0')
        except ValueError:
            urutan = div.urutan
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama divisi wajib diisi!'}, status=400)
        if kode and DivisiStruktur.objects.filter(kode__iexact=kode).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': f'Kode divisi "{kode}" sudah digunakan!'}, status=400)
        
        old_kode = div.kode
        old_nama = div.nama
        div.kode = kode or div.kode
        div.nama = nama
        div.deskripsi = deskripsi
        div.urutan = urutan
        div.save()

        # Update pengurus if code or name changed
        if old_kode != div.kode:
            PengurusStruktur.objects.filter(divisi=old_kode).update(divisi=div.kode)
        if old_nama != div.nama:
            PengurusStruktur.objects.filter(divisi=old_nama).update(divisi=div.nama)

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Edit Divisi Struktur', f'ID {pk}: {div.kode} - {div.nama}', request)
        return JsonResponse({
            'status': 'success',
            'message': f'Divisi "{div.nama}" berhasil diperbarui!',
            'data': {'id': div.id, 'kode': div.kode, 'nama': div.nama, 'deskripsi': div.deskripsi, 'urutan': div.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_divisi_struktur(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    div = get_object_or_404(DivisiStruktur, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Divisi Struktur', f'{div.kode} - {div.nama}', request)
    div.delete()
    return JsonResponse({'status': 'success', 'message': 'Divisi berhasil dihapus.'})


# --- ARSIP PERIODE KEPENGURUSAN ---
@admin_required
def admin_tambah_arsip(request):
    if request.method == 'POST':
        tahun_periode = request.POST.get('tahun_periode', '').strip()
        nama_kabinet = request.POST.get('nama_kabinet', '').strip()
        masa_bakti = request.POST.get('masa_bakti', '').strip()
        sk_rektor = request.POST.get('sk_rektor', '').strip()
        nama_ketua = request.POST.get('nama_ketua', '').strip()
        nim_ketua = request.POST.get('nim_ketua', '').strip()
        nama_wakil = request.POST.get('nama_wakil', '').strip()
        nim_wakil = request.POST.get('nim_wakil', '').strip()
        nama_sekretaris = request.POST.get('nama_sekretaris', '').strip()
        nama_bendahara = request.POST.get('nama_bendahara', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        aktif_val = request.POST.get('aktif', 'false').lower() in ('true', '1', 'on')
        order_index = int(request.POST.get('order_index', '0') or '0')

        if not tahun_periode or not nama_kabinet:
            return JsonResponse({'status': 'error', 'message': 'Tahun Periode dan Nama Kabinet wajib diisi!'}, status=400)

        if ArsipPeriode.objects.filter(tahun_periode=tahun_periode).exists():
            return JsonResponse({'status': 'error', 'message': f'Periode {tahun_periode} sudah ada di arsip!'}, status=400)

        if aktif_val:
            ArsipPeriode.objects.filter(aktif=True).update(aktif=False)

        arsip = ArsipPeriode.objects.create(
            tahun_periode=tahun_periode,
            nama_kabinet=nama_kabinet,
            masa_bakti=masa_bakti,
            sk_rektor=sk_rektor,
            nama_ketua=nama_ketua,
            nim_ketua=nim_ketua,
            nama_wakil=nama_wakil,
            nim_wakil=nim_wakil,
            nama_sekretaris=nama_sekretaris,
            nama_bendahara=nama_bendahara,
            deskripsi=deskripsi,
            aktif=aktif_val,
            order_index=order_index
        )
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Tambah Arsip Periode', f'{tahun_periode} - {nama_kabinet}', request)
        return JsonResponse({'status': 'success', 'message': f'Arsip Periode {tahun_periode} ({nama_kabinet}) berhasil disimpan!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_edit_arsip(request, pk):
    arsip = get_object_or_404(ArsipPeriode, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': arsip.id,
                'tahun_periode': arsip.tahun_periode,
                'nama_kabinet': arsip.nama_kabinet,
                'masa_bakti': arsip.masa_bakti,
                'sk_rektor': arsip.sk_rektor,
                'nama_ketua': arsip.nama_ketua,
                'nim_ketua': arsip.nim_ketua,
                'nama_wakil': arsip.nama_wakil,
                'nim_wakil': arsip.nim_wakil,
                'nama_sekretaris': arsip.nama_sekretaris,
                'nama_bendahara': arsip.nama_bendahara,
                'deskripsi': arsip.deskripsi,
                'aktif': arsip.aktif,
                'order_index': arsip.order_index,
            }
        })
    if request.method == 'POST':
        tahun_periode = request.POST.get('tahun_periode', '').strip()
        nama_kabinet = request.POST.get('nama_kabinet', '').strip()
        masa_bakti = request.POST.get('masa_bakti', '').strip()
        sk_rektor = request.POST.get('sk_rektor', '').strip()
        nama_ketua = request.POST.get('nama_ketua', '').strip()
        nim_ketua = request.POST.get('nim_ketua', '').strip()
        nama_wakil = request.POST.get('nama_wakil', '').strip()
        nim_wakil = request.POST.get('nim_wakil', '').strip()
        nama_sekretaris = request.POST.get('nama_sekretaris', '').strip()
        nama_bendahara = request.POST.get('nama_bendahara', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        aktif_val = request.POST.get('aktif', 'false').lower() in ('true', '1', 'on')
        order_index = int(request.POST.get('order_index', str(arsip.order_index)) or '0')

        if not tahun_periode or not nama_kabinet:
            return JsonResponse({'status': 'error', 'message': 'Tahun Periode dan Nama Kabinet wajib diisi!'}, status=400)

        if ArsipPeriode.objects.filter(tahun_periode=tahun_periode).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': f'Periode {tahun_periode} sudah digunakan arsip lain!'}, status=400)

        if aktif_val:
            ArsipPeriode.objects.exclude(pk=pk).filter(aktif=True).update(aktif=False)

        arsip.tahun_periode = tahun_periode
        arsip.nama_kabinet = nama_kabinet
        arsip.masa_bakti = masa_bakti
        arsip.sk_rektor = sk_rektor
        arsip.nama_ketua = nama_ketua
        arsip.nim_ketua = nim_ketua
        arsip.nama_wakil = nama_wakil
        arsip.nim_wakil = nim_wakil
        arsip.nama_sekretaris = nama_sekretaris
        arsip.nama_bendahara = nama_bendahara
        arsip.deskripsi = deskripsi
        arsip.aktif = aktif_val
        arsip.order_index = order_index
        arsip.save()

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Edit Arsip Periode', f'ID {pk}: {tahun_periode} - {nama_kabinet}', request)
        return JsonResponse({'status': 'success', 'message': f'Arsip Periode {tahun_periode} berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_arsip(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    arsip = get_object_or_404(ArsipPeriode, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Arsip Periode', f'{arsip.tahun_periode} - {arsip.nama_kabinet}', request)
    arsip.delete()
    return JsonResponse({'status': 'success', 'message': 'Data arsip periode kepengurusan berhasil dihapus.'})


# --- FORM BUILDER & GOOGLE FORM EDITABLE QUESTIONS ---
@admin_required
def admin_get_form_detail(request, pk):
    form_obj = get_object_or_404(FormulirOnline, pk=pk)
    analytics = form_obj.get_analytics()
    
    resp_list = []
    for r in form_obj.responses.all().order_by('-id'):
        resp_list.append({
            'id': r.id,
            'nama_lengkap': r.nama_lengkap,
            'nim': r.nim,
            'prodi_fakultas': r.prodi_fakultas,
            'no_whatsapp': r.no_whatsapp,
            'email': r.email,
            'catatan': r.catatan,
            'status': r.status,
            'created_at': r.created_at.strftime('%d/%m/%Y %H:%M'),
            'berkas_url': r.get_berkas(),
            'jawaban': r.jawaban or {}
        })

    return JsonResponse({
        'status': 'success',
        'form': {
            'id': form_obj.id,
            'judul': form_obj.judul,
            'slug': form_obj.slug,
            'deskripsi': form_obj.deskripsi,
            'kategori': form_obj.kategori,
            'deadline': form_obj.deadline.strftime('%Y-%m-%d') if form_obj.deadline else '',
            'kuota': form_obj.kuota,
            'is_active': form_obj.is_active,
            'pertanyaan': form_obj.get_questions(),
        },
        'analytics': analytics,
        'responses': resp_list
    })


@admin_required
def admin_tambah_formulir(request):
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        if not judul:
            return JsonResponse({'status': 'error', 'message': 'Judul formulir wajib diisi!'}, status=400)

        kategori = request.POST.get('kategori', 'Pelatihan Brevet').strip()
        deadline_str = request.POST.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        try:
            kuota = int(request.POST.get('kuota', '100') or '100')
        except ValueError:
            kuota = 100
        deskripsi = request.POST.get('deskripsi', '').strip()

        pertanyaan_raw = request.POST.get('pertanyaan', '[]')
        try:
            pertanyaan = json.loads(pertanyaan_raw) if isinstance(pertanyaan_raw, str) else pertanyaan_raw
            if not isinstance(pertanyaan, list):
                pertanyaan = []
        except Exception:
            pertanyaan = []

        slug = slugify(judul)
        count = FormulirOnline.objects.filter(slug__startswith=slug).count()
        if count > 0:
            slug = f"{slug}-{count + 1}"

        form_obj = FormulirOnline.objects.create(
            judul=judul,
            slug=slug,
            kategori=kategori,
            deadline=deadline,
            kuota=kuota,
            deskripsi=deskripsi,
            pertanyaan=pertanyaan if pertanyaan else FormulirOnline.default_questions(),
            is_active=True
        )
        user_name = request.user.get_full_name() or request.user.username or 'Sekretaris'
        log_audit(user_name, 'Buat Formulir Online Baru', f'Judul: {judul}, Kuota: {kuota}, Pertanyaan: {len(form_obj.pertanyaan)}', request)
        return JsonResponse({'status': 'success', 'message': f'Formulir "{judul}" berhasil dipublikasikan!', 'form_id': form_obj.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_edit_formulir(request, pk):
    form_obj = get_object_or_404(FormulirOnline, pk=pk)
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        if not judul:
            return JsonResponse({'status': 'error', 'message': 'Judul formulir wajib diisi!'}, status=400)

        kategori = request.POST.get('kategori', form_obj.kategori).strip()
        deadline_str = request.POST.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
        try:
            kuota = int(request.POST.get('kuota', str(form_obj.kuota)) or str(form_obj.kuota))
        except ValueError:
            kuota = form_obj.kuota
        deskripsi = request.POST.get('deskripsi', form_obj.deskripsi).strip()

        pertanyaan_raw = request.POST.get('pertanyaan')
        if pertanyaan_raw is not None:
            try:
                pertanyaan = json.loads(pertanyaan_raw) if isinstance(pertanyaan_raw, str) else pertanyaan_raw
                if isinstance(pertanyaan, list):
                    form_obj.pertanyaan = pertanyaan
            except Exception:
                pass

        form_obj.judul = judul
        form_obj.kategori = kategori
        form_obj.deadline = deadline
        form_obj.kuota = kuota
        form_obj.deskripsi = deskripsi
        form_obj.save()

        user_name = request.user.get_full_name() or request.user.username or 'Sekretaris'
        log_audit(user_name, 'Edit Formulir Online', f'ID {pk}: {judul}, Pertanyaan: {len(form_obj.get_questions())}', request)
        return JsonResponse({'status': 'success', 'message': f'Formulir "{judul}" dan pertanyaan berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@admin_required
def admin_toggle_formulir(request, pk):
    form_obj = get_object_or_404(FormulirOnline, pk=pk)
    form_obj.is_active = not form_obj.is_active
    form_obj.save()
    user_name = request.user.get_full_name() or request.user.username or 'Sekretaris'
    status_str = 'Diaktifkan' if form_obj.is_active else 'Ditutup'
    log_audit(user_name, f'Ubah Status Form ({status_str})', form_obj.judul, request)
    return JsonResponse({'status': 'success', 'is_active': form_obj.is_active, 'message': f'Status formulir berhasil diubah menjadi {status_str}.'})


@admin_required
def admin_hapus_formulir(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    form_obj = get_object_or_404(FormulirOnline, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Sekretaris'
    log_audit(user_name, 'Hapus Formulir Online', form_obj.judul, request)
    form_obj.delete()
    return JsonResponse({'status': 'success', 'message': 'Formulir berhasil dihapus.'})


# --- KATEGORI FORMULIR (GFORM) ---
@admin_required
def admin_list_kategori_form(request):
    kategori = KategoriFormulir.objects.all().order_by('urutan', 'nama')
    data = [{
        'id': k.id,
        'nama': k.nama,
        'deskripsi': k.deskripsi,
        'urutan': k.urutan,
        'total_formulir': FormulirOnline.objects.filter(kategori=k.nama).count()
    } for k in kategori]
    return JsonResponse({'status': 'success', 'data': data})


@admin_required
def admin_tambah_kategori_form(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', '0') or '0')
        except ValueError:
            urutan = 0
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama kategori wajib diisi!'}, status=400)
        if KategoriFormulir.objects.filter(nama__iexact=nama).exists():
            return JsonResponse({'status': 'error', 'message': f'Kategori "{nama}" sudah ada!'}, status=400)
        kat = KategoriFormulir.objects.create(nama=nama, deskripsi=deskripsi, urutan=urutan)
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Tambah Kategori Formulir', kat.nama, request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori "{kat.nama}" berhasil ditambahkan!',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_edit_kategori_form(request, pk):
    kat = get_object_or_404(KategoriFormulir, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': kat.id,
                'nama': kat.nama,
                'deskripsi': kat.deskripsi,
                'urutan': kat.urutan,
            }
        })
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', str(kat.urutan)) or '0')
        except ValueError:
            urutan = kat.urutan
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama kategori wajib diisi!'}, status=400)
        if KategoriFormulir.objects.filter(nama__iexact=nama).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': f'Kategori "{nama}" sudah ada!'}, status=400)
        
        old_nama = kat.nama
        kat.nama = nama
        kat.deskripsi = deskripsi
        kat.urutan = urutan
        kat.save()
        if old_nama != nama:
            FormulirOnline.objects.filter(kategori=old_nama).update(kategori=nama)
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Edit Kategori Formulir', f'ID {pk}: {kat.nama}', request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori "{kat.nama}" berhasil diperbarui!',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_kategori_form(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    kat = get_object_or_404(KategoriFormulir, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Kategori Formulir', kat.nama, request)
    kat.delete()
    return JsonResponse({'status': 'success', 'message': 'Kategori formulir berhasil dihapus.'})


# --- ASPIRASI MAHASISWA & EDITABLE QUESTIONS ---
@admin_required
def admin_get_aspirasi_config(request):
    config = AspirasiFormConfig.get_solo()
    return JsonResponse({
        'status': 'success',
        'config': {
            'id': config.id,
            'judul': config.judul,
            'deskripsi': config.deskripsi,
            'pertanyaan': config.get_questions(),
            'is_active': config.is_active
        }
    })


@admin_required
def admin_simpan_aspirasi_config(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    config = AspirasiFormConfig.get_solo()
    judul = request.POST.get('judul', '').strip() or config.judul
    deskripsi = request.POST.get('deskripsi', '').strip() or config.deskripsi
    pertanyaan_raw = request.POST.get('pertanyaan', '[]')
    try:
        pertanyaan = json.loads(pertanyaan_raw) if isinstance(pertanyaan_raw, str) else pertanyaan_raw
        if not isinstance(pertanyaan, list):
            pertanyaan = []
    except Exception:
        pertanyaan = []

    config.judul = judul
    config.deskripsi = deskripsi
    if pertanyaan:
        config.pertanyaan = pertanyaan
    config.save()

    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Update Konfigurasi & Pertanyaan Aspirasi', f'Jumlah Pertanyaan: {len(config.get_questions())}', request)
    return JsonResponse({
        'status': 'success',
        'message': 'Konfigurasi pertanyaan formulir aspirasi berhasil disimpan!'
    })


@admin_required
def admin_get_aspirasi_analytics(request):
    total_aspirasi = AspirasiMahasiswa.objects.count()
    config = AspirasiFormConfig.get_solo()
    all_asp = list(AspirasiMahasiswa.objects.all().order_by('-id'))

    status_counts = {'Pending': 0, 'Diproses': 0, 'Ditindaklanjuti': 0, 'Selesai': 0}
    for a in all_asp:
        if a.status in status_counts:
            status_counts[a.status] += 1
        else:
            status_counts[a.status] = 1

    kategori_counts = {}
    for a in all_asp:
        kat = a.kategori or 'Lainnya'
        kategori_counts[kat] = kategori_counts.get(kat, 0) + 1

    rating_counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    ratings_sum = 0
    rated_count = 0
    for a in all_asp:
        r = str(a.rating or 5)
        if r in rating_counts:
            rating_counts[r] += 1
        try:
            ratings_sum += int(r)
            rated_count += 1
        except ValueError:
            pass
    avg_rating = round(ratings_sum / rated_count, 1) if rated_count > 0 else 5.0

    questions = config.get_questions()
    q_analytics = []
    for q in questions:
        q_id = q.get('id', '')
        q_label = q.get('label', '')
        q_tipe = q.get('tipe', 'text')
        q_options = q.get('options', [])

        stat = {
            'id': q_id,
            'label': q_label,
            'tipe': q_tipe,
            'options': q_options,
            'counts': {},
            'text_answers': []
        }

        if q_tipe in ('radio', 'select', 'checkbox', 'rating'):
            for opt in q_options:
                stat['counts'][str(opt)] = 0

            for a in all_asp:
                val = None
                if q_id == 'q_kategori':
                    val = a.kategori
                elif q_id == 'q_rating':
                    val = str(a.rating or 5)
                elif a.jawaban_tambahan and q_id in a.jawaban_tambahan:
                    val = a.jawaban_tambahan[q_id]

                if val:
                    if isinstance(val, list):
                        for item in val:
                            item_str = str(item)
                            stat['counts'][item_str] = stat['counts'].get(item_str, 0) + 1
                    else:
                        val_str = str(val)
                        stat['counts'][val_str] = stat['counts'].get(val_str, 0) + 1
        else:
            for a in all_asp:
                val = ''
                if q_id == 'q_isi':
                    val = a.isi_aspirasi
                elif a.jawaban_tambahan and q_id in a.jawaban_tambahan:
                    val = a.jawaban_tambahan[q_id]
                if val:
                    stat['text_answers'].append({
                        'pengirim': a.pengirim,
                        'jawaban': str(val)
                    })
        q_analytics.append(stat)

    return JsonResponse({
        'status': 'success',
        'total_aspirasi': total_aspirasi,
        'avg_rating': avg_rating,
        'status_counts': status_counts,
        'kategori_counts': kategori_counts,
        'rating_counts': rating_counts,
        'questions_analytics': q_analytics
    })


@admin_required
def admin_update_aspirasi(request, pk):
    asp = get_object_or_404(AspirasiMahasiswa, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status', asp.status)
        tanggapan = request.POST.get('tanggapan', asp.tanggapan_admin)
        is_public = request.POST.get('is_public') == 'true' or request.POST.get('is_public') == '1'

        asp.status = new_status
        asp.tanggapan_admin = tanggapan
        asp.is_public = is_public
        asp.save()

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Update Status Aspirasi', f'ID {pk}: {new_status}', request)
        return JsonResponse({'status': 'success', 'message': 'Aspirasi berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_aspirasi(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    asp = get_object_or_404(AspirasiMahasiswa, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Aspirasi Mahasiswa', f'ID {pk}', request)
    asp.delete()
    return JsonResponse({'status': 'success', 'message': 'Aspirasi berhasil dihapus.'})


# --- PROGRAM KERJA ---
@admin_required
def admin_tambah_proker(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        divisi = request.POST.get('divisi', 'Diklat & Brevet').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        target_peserta = request.POST.get('target_peserta', '').strip()
        waktu_info = request.POST.get('waktu_info', '').strip()
        lokasi = request.POST.get('lokasi', '').strip()
        anggaran = Decimal(request.POST.get('anggaran_biaya', '0').replace('.', '').replace(',', '') or '0')
        realisasi = Decimal(request.POST.get('realisasi_biaya', '0').replace('.', '').replace(',', '') or '0')
        status = request.POST.get('status', 'Terjadwal')
        progress = int(request.POST.get('progress_persen', '0') or '0')
        pendaftaran_buka = request.POST.get('pendaftaran_buka') in ('true', '1', 'on')
        banner = request.FILES.get('banner')

        proker = ProgramKerja(
            nama=nama,
            divisi=divisi,
            deskripsi=deskripsi,
            target_peserta=target_peserta,
            waktu_info=waktu_info,
            lokasi=lokasi,
            anggaran_biaya=anggaran,
            realisasi_biaya=realisasi,
            status=status,
            progress_persen=progress,
            pendaftaran_buka=pendaftaran_buka
        )
        if banner:
            # Upload to Cloudinary
            proker.banner = banner
        proker.save()

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Tambah Program Kerja Baru', f'{nama} ({divisi})', request)
        return JsonResponse({'status': 'success', 'message': f'Program kerja "{nama}" berhasil disimpan ke database!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_proker(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    proker = get_object_or_404(ProgramKerja, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Program Kerja', proker.nama, request)
    proker.delete()
    return JsonResponse({'status': 'success', 'message': 'Program kerja berhasil dihapus.'})


@admin_required
def admin_edit_proker(request, pk):
    proker = get_object_or_404(ProgramKerja, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': proker.id,
                'nama': proker.nama,
                'divisi': proker.divisi,
                'deskripsi': proker.deskripsi,
                'target_peserta': proker.target_peserta,
                'waktu_info': proker.waktu_info,
                'lokasi': proker.lokasi,
                'anggaran_biaya': float(proker.anggaran_biaya),
                'realisasi_biaya': float(proker.realisasi_biaya),
                'status': proker.status,
                'progress_persen': proker.progress_persen,
                'pendaftaran_buka': proker.pendaftaran_buka,
                'link_pendaftaran': proker.link_pendaftaran,
                'banner': proker.get_banner(),
            }
        })
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        divisi = request.POST.get('divisi', proker.divisi).strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        target_peserta = request.POST.get('target_peserta', proker.target_peserta).strip()
        waktu_info = request.POST.get('waktu_info', proker.waktu_info).strip()
        lokasi = request.POST.get('lokasi', proker.lokasi).strip()
        anggaran_str = request.POST.get('anggaran_biaya', str(proker.anggaran_biaya)).replace('.', '').replace(',', '')
        realisasi_str = request.POST.get('realisasi_biaya', str(proker.realisasi_biaya)).replace('.', '').replace(',', '')
        anggaran = Decimal(anggaran_str or '0')
        realisasi = Decimal(realisasi_str or '0')
        status = request.POST.get('status', proker.status).strip()
        progress = int(request.POST.get('progress_persen', str(proker.progress_persen)) or '0')
        pendaftaran_buka = request.POST.get('pendaftaran_buka') in ('true', '1', 'on')
        link_pendaftaran = request.POST.get('link_pendaftaran', proker.link_pendaftaran).strip()
        banner = request.FILES.get('banner')

        proker.nama = nama or proker.nama
        proker.divisi = divisi
        proker.deskripsi = deskripsi
        proker.target_peserta = target_peserta
        proker.waktu_info = waktu_info
        proker.lokasi = lokasi
        proker.anggaran_biaya = anggaran
        proker.realisasi_biaya = realisasi
        proker.status = status
        proker.progress_persen = progress
        proker.pendaftaran_buka = pendaftaran_buka
        proker.link_pendaftaran = link_pendaftaran
        if banner:
            proker.banner = banner
        proker.save()

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Edit Program Kerja', f'ID {pk}: {proker.nama}', request)
        return JsonResponse({'status': 'success', 'message': f'Program kerja "{proker.nama}" berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# ==================== KATEGORI BERITA CRUD ====================
@admin_required
def admin_list_kategori_berita(request):
    kategori = KategoriBerita.objects.all().order_by('urutan', 'nama')
    data = [{
        'id': k.id,
        'nama': k.nama,
        'deskripsi': k.deskripsi,
        'urutan': k.urutan,
        'total_berita': Berita.objects.filter(kategori=k.nama).count()
    } for k in kategori]
    return JsonResponse({'status': 'success', 'data': data})


@admin_required
def admin_tambah_kategori_berita(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', '0') or '0')
        except ValueError:
            urutan = 0
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama kategori berita wajib diisi!'}, status=400)
        if KategoriBerita.objects.filter(nama__iexact=nama).exists():
            return JsonResponse({'status': 'error', 'message': f'Kategori berita "{nama}" sudah ada!'}, status=400)
        kat = KategoriBerita.objects.create(nama=nama, deskripsi=deskripsi, urutan=urutan)
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Tambah Kategori Berita', kat.nama, request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori berita "{kat.nama}" berhasil ditambahkan!',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_edit_kategori_berita(request, pk):
    kat = get_object_or_404(KategoriBerita, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    elif request.method == 'POST':
        old_nama = kat.nama
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', str(kat.urutan)) or '0')
        except ValueError:
            urutan = kat.urutan
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama kategori berita wajib diisi!'}, status=400)
        if KategoriBerita.objects.filter(nama__iexact=nama).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': f'Kategori berita "{nama}" sudah ada!'}, status=400)
        
        kat.nama = nama
        kat.deskripsi = deskripsi
        kat.urutan = urutan
        kat.save()

        # Update matching berita
        if old_nama != nama:
            Berita.objects.filter(kategori=old_nama).update(kategori=nama)

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Edit Kategori Berita', f'{old_nama} -> {kat.nama}', request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori berita "{kat.nama}" berhasil diperbarui!',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_kategori_berita(request, pk):
    if request.method == 'POST':
        kat = get_object_or_404(KategoriBerita, pk=pk)
        nama = kat.nama
        kat.delete()
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Hapus Kategori Berita', nama, request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori berita "{nama}" berhasil dihapus!'
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# --- BERITA ---
@admin_required
def admin_tambah_berita(request):
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        kategori = request.POST.get('kategori', 'Perpajakan').strip()
        tanggal_str = request.POST.get('tanggal')
        tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date() if tanggal_str else timezone.now().date()
        penulis = request.POST.get('penulis', '').strip() or 'Humas HIMA'
        ringkasan = request.POST.get('ringkasan', '').strip()
        isi = request.POST.get('isi', '').strip()
        gambar = request.FILES.get('gambar')

        slug = slugify(judul)
        count = Berita.objects.filter(slug__startswith=slug).count()
        if count > 0:
            slug = f"{slug}-{count + 1}"

        berita = Berita(
            judul=judul,
            slug=slug,
            kategori=kategori,
            tanggal=tanggal,
            penulis=penulis,
            ringkasan=ringkasan,
            isi=isi,
            is_published=True
        )
        if gambar:
            # Upload to Cloudinary
            berita.gambar_sampul = gambar
        berita.save()

        user_name = request.user.get_full_name() or request.user.username or 'Media'
        log_audit(user_name, 'Publikasi Berita Baru', judul, request)
        return JsonResponse({'status': 'success', 'message': f'Berita "{judul}" berhasil dipublikasikan dan gambar tersimpan di Cloudinary!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_berita(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    berita = get_object_or_404(Berita, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Media'
    log_audit(user_name, 'Hapus Berita', berita.judul, request)
    berita.delete()
    return JsonResponse({'status': 'success', 'message': 'Berita berhasil dihapus.'})


@admin_required
def admin_edit_berita(request, pk):
    berita = get_object_or_404(Berita, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': berita.id,
                'judul': berita.judul,
                'kategori': berita.kategori,
                'tanggal': berita.tanggal.strftime('%Y-%m-%d') if berita.tanggal else '',
                'penulis': berita.penulis,
                'ringkasan': berita.ringkasan,
                'isi': berita.isi,
                'is_published': berita.is_published,
                'gambar': berita.get_gambar(),
            }
        })
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        kategori = request.POST.get('kategori', berita.kategori).strip()
        tanggal_str = request.POST.get('tanggal')
        penulis = request.POST.get('penulis', berita.penulis).strip()
        ringkasan = request.POST.get('ringkasan', '').strip()
        isi = request.POST.get('isi', '').strip()
        gambar = request.FILES.get('gambar')

        if not judul:
            return JsonResponse({'status': 'error', 'message': 'Judul berita tidak boleh kosong!'}, status=400)

        berita.judul = judul
        berita.slug = slugify(judul)
        berita.kategori = kategori
        if tanggal_str:
            try:
                berita.tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        berita.penulis = penulis or berita.penulis
        berita.ringkasan = ringkasan or berita.ringkasan
        berita.isi = isi or berita.isi
        if gambar:
            berita.gambar_sampul = gambar
        berita.save()

        user_name = request.user.get_full_name() or request.user.username or 'Media'
        log_audit(user_name, 'Edit Berita', berita.judul, request)
        return JsonResponse({'status': 'success', 'message': f'Berita "{berita.judul}" berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# ==================== KATEGORI GALERI CRUD ====================
@admin_required
def admin_list_kategori_galeri(request):
    kategori = KategoriGaleri.objects.all().order_by('urutan', 'nama')
    data = [{
        'id': k.id,
        'nama': k.nama,
        'deskripsi': k.deskripsi,
        'urutan': k.urutan,
        'total_galeri': GaleriKegiatan.objects.filter(kategori=k.nama).count()
    } for k in kategori]
    return JsonResponse({'status': 'success', 'data': data})


@admin_required
def admin_tambah_kategori_galeri(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', '0') or '0')
        except ValueError:
            urutan = 0
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama kategori galeri wajib diisi!'}, status=400)
        if KategoriGaleri.objects.filter(nama__iexact=nama).exists():
            return JsonResponse({'status': 'error', 'message': f'Kategori galeri "{nama}" sudah ada!'}, status=400)
        kat = KategoriGaleri.objects.create(nama=nama, deskripsi=deskripsi, urutan=urutan)
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Tambah Kategori Galeri', kat.nama, request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori galeri "{kat.nama}" berhasil ditambahkan!',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_edit_kategori_galeri(request, pk):
    kat = get_object_or_404(KategoriGaleri, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    elif request.method == 'POST':
        old_nama = kat.nama
        nama = request.POST.get('nama', '').strip()
        deskripsi = request.POST.get('deskripsi', '').strip()
        try:
            urutan = int(request.POST.get('urutan', str(kat.urutan)) or '0')
        except ValueError:
            urutan = kat.urutan
        if not nama:
            return JsonResponse({'status': 'error', 'message': 'Nama kategori galeri wajib diisi!'}, status=400)
        if KategoriGaleri.objects.filter(nama__iexact=nama).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': f'Kategori galeri "{nama}" sudah ada!'}, status=400)
        
        kat.nama = nama
        kat.deskripsi = deskripsi
        kat.urutan = urutan
        kat.save()

        # Update matching galeri photos
        if old_nama != nama:
            GaleriKegiatan.objects.filter(kategori=old_nama).update(kategori=nama)

        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Edit Kategori Galeri', f'{old_nama} -> {kat.nama}', request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori galeri "{kat.nama}" berhasil diperbarui!',
            'data': {'id': kat.id, 'nama': kat.nama, 'deskripsi': kat.deskripsi, 'urutan': kat.urutan}
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_kategori_galeri(request, pk):
    if request.method == 'POST':
        kat = get_object_or_404(KategoriGaleri, pk=pk)
        nama = kat.nama
        kat.delete()
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Hapus Kategori Galeri', nama, request)
        return JsonResponse({
            'status': 'success',
            'message': f'Kategori galeri "{nama}" berhasil dihapus!'
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# --- GALERI ---
@admin_required
def admin_tambah_galeri(request):
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        kategori = request.POST.get('kategori', 'Kegiatan').strip()
        tanggal_str = request.POST.get('tanggal_kegiatan')
        tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date() if tanggal_str else timezone.now().date()
        keterangan = request.POST.get('keterangan', '').strip()
        gambar = request.FILES.get('gambar')

        galeri = GaleriKegiatan(
            judul=judul,
            kategori=kategori,
            tanggal_kegiatan=tanggal,
            keterangan=keterangan
        )
        if gambar:
            # Upload to Cloudinary
            galeri.gambar = gambar
        else:
            return JsonResponse({'status': 'error', 'message': 'File gambar wajib diunggah!'}, status=400)
        galeri.save()

        user_name = request.user.get_full_name() or request.user.username or 'Media'
        log_audit(user_name, 'Upload Dokumentasi Galeri', judul, request)
        return JsonResponse({'status': 'success', 'message': f'Dokumentasi "{judul}" berhasil diupload ke Cloudinary dan database!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_galeri(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    galeri = get_object_or_404(GaleriKegiatan, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Media'
    log_audit(user_name, 'Hapus Foto Galeri', galeri.judul, request)
    galeri.delete()
    return JsonResponse({'status': 'success', 'message': 'Foto galeri berhasil dihapus.'})


@admin_required
def admin_edit_galeri(request, pk):
    galeri = get_object_or_404(GaleriKegiatan, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': galeri.id,
                'judul': galeri.judul,
                'kategori': galeri.kategori,
                'tanggal_kegiatan': galeri.tanggal_kegiatan.strftime('%Y-%m-%d') if galeri.tanggal_kegiatan else '',
                'keterangan': galeri.keterangan,
                'gambar': galeri.get_gambar(),
            }
        })
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        kategori = request.POST.get('kategori', galeri.kategori).strip()
        tanggal_str = request.POST.get('tanggal_kegiatan')
        keterangan = request.POST.get('keterangan', '').strip()
        gambar = request.FILES.get('gambar')

        if not judul:
            return JsonResponse({'status': 'error', 'message': 'Judul foto galeri tidak boleh kosong!'}, status=400)

        galeri.judul = judul
        galeri.kategori = kategori
        if tanggal_str:
            try:
                galeri.tanggal_kegiatan = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        galeri.keterangan = keterangan
        if gambar:
            galeri.gambar = gambar
        galeri.save()

        user_name = request.user.get_full_name() or request.user.username or 'Media'
        log_audit(user_name, 'Edit Foto Galeri', galeri.judul, request)
        return JsonResponse({'status': 'success', 'message': f'Dokumentasi "{galeri.judul}" berhasil diperbarui!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# --- PROFIL ORGANISASI ---
@admin_required
def admin_update_profil(request):
    if request.method == 'POST':
        profile = OrganizationProfile.objects.first()
        if not profile:
            profile = OrganizationProfile.objects.create()

        profile.nama_organisasi = request.POST.get('nama_organisasi', profile.nama_organisasi).strip()
        profile.tagline = request.POST.get('tagline', profile.tagline).strip()
        profile.deskripsi = request.POST.get('deskripsi', profile.deskripsi).strip()
        profile.visi = request.POST.get('visi', profile.visi).strip()
        profile.misi = request.POST.get('misi', profile.misi).strip()
        profile.sejarah = request.POST.get('sejarah', profile.sejarah).strip()
        profile.makna_lambang = request.POST.get('makna_lambang', profile.makna_lambang).strip()
        profile.nama_ketua = request.POST.get('nama_ketua', profile.nama_ketua).strip()
        profile.periode_aktif = request.POST.get('periode_aktif', profile.periode_aktif).strip()
        profile.sambutan_ketua = request.POST.get('sambutan_ketua', profile.sambutan_ketua).strip()
        profile.email = request.POST.get('email', profile.email).strip()
        profile.no_whatsapp = request.POST.get('no_whatsapp', profile.no_whatsapp).strip()
        profile.instagram = request.POST.get('instagram', profile.instagram).strip()
        profile.linkedin = request.POST.get('linkedin', profile.linkedin).strip()
        profile.alamat = request.POST.get('alamat', profile.alamat).strip()

        foto_ketua = request.FILES.get('foto_ketua')
        if foto_ketua:
            profile.foto_ketua = foto_ketua

        profile.save()

        user_name = request.user.get_full_name() or request.user.username or 'Ketua'
        log_audit(user_name, 'Update Profil Organisasi', profile.nama_organisasi, request)
        return JsonResponse({'status': 'success', 'message': 'Profil organisasi berhasil diperbarui di database Neon PostgreSQL!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# --- MULTI ADMIN ---
@admin_required
def admin_tambah_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        nama = request.POST.get('nama', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', 'Super Admin')

        if not username or not password:
            return JsonResponse({'status': 'error', 'message': 'Username dan password wajib diisi!'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username sudah digunakan!'}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nama,
            is_staff=True,
            is_superuser=(role == 'Super Admin')
        )
        user_name = request.user.get_full_name() or request.user.username or 'Admin'
        log_audit(user_name, 'Tambah Akun Pengelola Baru', f'{username} ({role})', request)
        return JsonResponse({'status': 'success', 'message': f'Akun admin "{username}" berhasil dibuat!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_user(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    user = get_object_or_404(User, pk=pk)
    if user.id == request.user.id:
        return JsonResponse({'status': 'error', 'message': 'Tidak dapat menghapus akun Anda sendiri yang sedang aktif!'}, status=400)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Akun Pengelola', user.username, request)
    user.delete()
    return JsonResponse({'status': 'success', 'message': 'Akun admin berhasil dihapus.'})


# --- SERTIFIKAT & PRESENSI ---
@admin_required
def admin_tambah_sertifikat(request):
    if request.method == 'POST':
        nomor = request.POST.get('nomor_sertifikat', '').strip()
        nama = request.POST.get('nama_penerima', '').strip()
        nim = request.POST.get('nim', '').strip()
        kegiatan = request.POST.get('kegiatan', '').strip()
        tanggal_str = request.POST.get('tanggal_terbit')
        tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date() if tanggal_str else timezone.now().date()
        predikat = request.POST.get('predikat', 'Peserta Lulus').strip()
        file_cert = request.FILES.get('file_sertifikat')

        if not nomor or not nama:
            return JsonResponse({'status': 'error', 'message': 'Nomor sertifikat dan nama penerima wajib diisi!'}, status=400)

        cert = SertifikatDigital(
            nomor_sertifikat=nomor,
            nama_penerima=nama,
            nim=nim,
            kegiatan=kegiatan,
            tanggal_terbit=tanggal,
            predikat=predikat,
            is_valid=True
        )
        if file_cert:
            # Upload to Cloudinary
            cert.file_sertifikat = file_cert
        cert.save()

        user_name = request.user.get_full_name() or request.user.username or 'Diklat'
        log_audit(user_name, 'Penerbitan E-Sertifikat', f'{nomor} - {nama}', request)
        return JsonResponse({'status': 'success', 'message': f'Sertifikat {nomor} untuk {nama} berhasil diterbitkan!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@admin_required
def admin_hapus_sertifikat(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    cert = get_object_or_404(SertifikatDigital, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus E-Sertifikat', cert.nomor_sertifikat, request)
    cert.delete()
    return JsonResponse({'status': 'success', 'message': 'Sertifikat berhasil dihapus.'})


@admin_required
def admin_hapus_presensi(request, pk):
    if request.method not in ('POST', 'DELETE', 'GET'):
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    pr = get_object_or_404(PresensiDigital, pk=pk)
    user_name = request.user.get_full_name() or request.user.username or 'Admin'
    log_audit(user_name, 'Hapus Catatan Presensi', f'{pr.nama_lengkap} ({pr.kegiatan})', request)
    pr.delete()
    return JsonResponse({'status': 'success', 'message': 'Catatan presensi berhasil dihapus.'})


# --- DOWNLOAD / PRINT LPJ LAPORAN KEUANGAN ---
def download_lpj_view(request):
    profile = OrganizationProfile.objects.first()
    transaksi = TransaksiKas.objects.all().order_by('tanggal')
    total_masuk = TransaksiKas.objects.filter(jenis='MASUK').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    total_keluar = TransaksiKas.objects.filter(jenis='KELUAR').aggregate(total=Sum('nominal'))['total'] or Decimal(0)
    saldo_kas = total_masuk - total_keluar

    html = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Laporan Pertanggungjawaban Keuangan - {profile.nama_organisasi}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; color: #1e293b; }}
            .header {{ text-align: center; border-bottom: 3px double #002B5C; padding-bottom: 15px; margin-bottom: 25px; }}
            .header h1 {{ margin: 0; color: #002B5C; font-size: 22px; text-transform: uppercase; }}
            .header p {{ margin: 5px 0 0; font-size: 13px; color: #64748b; }}
            .summary-box {{ display: flex; gap: 20px; margin-bottom: 25px; }}
            .card {{ flex: 1; padding: 15px; border-radius: 8px; border: 1px solid #cbd5e1; background: #f8fafc; }}
            .card h3 {{ margin: 0 0 5px; font-size: 11px; text-transform: uppercase; color: #64748b; }}
            .card p {{ margin: 0; font-size: 18px; font-weight: bold; color: #002B5C; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 15px; }}
            th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
            th {{ background-color: #002B5C; color: white; text-transform: uppercase; font-size: 11px; }}
            tr:nth-child(even) {{ background-color: #f8fafc; }}
            .text-right {{ text-align: right; }}
            .masuk {{ color: #059669; font-weight: bold; }}
            .keluar {{ color: #dc2626; font-weight: bold; }}
            .footer {{ margin-top: 40px; display: flex; justify-content: space-between; font-size: 12px; }}
            .sign-box {{ text-align: center; width: 220px; }}
            .sign-space {{ height: 60px; }}
            @media print {{
                body {{ padding: 10px; }}
                button {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div style="text-align: right; margin-bottom: 10px;">
            <button onclick="window.print()" style="padding: 8px 16px; background: #002B5C; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">Cetak / Simpan PDF</button>
        </div>
        <div class="header">
            <h1>{profile.nama_organisasi}</h1>
            <p>LAPORAN PERTANGGUNGJAWABAN ARUS KAS ORGANISASI PERIODE {profile.periode_aktif}</p>
            <p>{profile.alamat} • Email: {profile.email}</p>
        </div>

        <div class="summary-box">
            <div class="card">
                <h3>Total Penerimaan Kas</h3>
                <p class="masuk">Rp {total_masuk:,.0f}</p>
            </div>
            <div class="card">
                <h3>Total Pengeluaran Kas</h3>
                <p class="keluar">Rp {total_keluar:,.0f}</p>
            </div>
            <div class="card">
                <h3>Sisa Saldo Kas Bersih</h3>
                <p>Rp {saldo_kas:,.0f}</p>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width: 35px;">No</th>
                    <th style="width: 85px;">Tanggal</th>
                    <th style="width: 80px;">Jenis</th>
                    <th>Kategori & Keterangan Transaksi</th>
                    <th style="width: 140px;">Penanggung Jawab</th>
                    <th class="text-right" style="width: 130px;">Nominal (Rp)</th>
                </tr>
            </thead>
            <tbody>
    """
    for idx, t in enumerate(transaksi, 1):
        color_class = "masuk" if t.jenis == "MASUK" else "keluar"
        nominal_str = f"+ Rp {t.nominal:,.0f}" if t.jenis == "MASUK" else f"- Rp {t.nominal:,.0f}"
        html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{t.tanggal.strftime('%d/%m/%Y')}</td>
                    <td class="{color_class}">{t.jenis}</td>
                    <td><strong>{t.kategori}</strong><br><span style="color:#64748b; font-size:11px;">{t.keterangan}</span></td>
                    <td>{t.pj_transaksi}</td>
                    <td class="text-right {color_class}">{nominal_str}</td>
                </tr>
        """

    html += f"""
            </tbody>
            <tfoot>
                <tr style="background: #f1f5f9; font-weight: bold;">
                    <td colspan="5" style="text-align: right;">SISA SALDO KAS TERAKHIR:</td>
                    <td class="text-right" style="color: #002B5C; font-size: 14px;">Rp {saldo_kas:,.0f}</td>
                </tr>
            </tfoot>
        </table>

        <div class="footer">
            <div class="sign-box">
                <p>Mengetahui,<br><strong>Ketua Umum HIMA</strong></p>
                <div class="sign-space"></div>
                <p><u>{profile.nama_ketua}</u><br>NIM. 23141010028</p>
            </div>
            <div class="sign-box">
                <p>Jakarta, {timezone.now().strftime('%d %B %Y')}<br><strong>Bendahara Umum HIMA</strong></p>
                <div class="sign-space"></div>
                <p><u>Nadia Rahmawati</u><br>NIM. 24141010032</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

from django.contrib import admin
from .models import (
    OrganizationProfile, PengurusStruktur, DivisiStruktur, Anggota, ArsipPeriode,
    ProgramKerja, TransaksiKas, FormulirOnline, KategoriFormulir, ResponFormulir,
    AspirasiMahasiswa, AspirasiFormConfig, Berita, GaleriKegiatan, PesanKontak,
    SertifikatDigital, PresensiDigital, AuditLog
)

@admin.register(DivisiStruktur)
class DivisiStrukturAdmin(admin.ModelAdmin):
    list_display = ('kode', 'nama', 'urutan')
    search_fields = ('kode', 'nama')

@admin.register(KategoriFormulir)
class KategoriFormulirAdmin(admin.ModelAdmin):
    list_display = ('nama', 'urutan')
    search_fields = ('nama',)

@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    list_display = ('nama_organisasi', 'nama_ketua', 'periode_aktif', 'email', 'no_whatsapp')

@admin.register(PengurusStruktur)
class PengurusStrukturAdmin(admin.ModelAdmin):
    list_display = ('nama', 'nim', 'jabatan', 'divisi', 'periode', 'urutan', 'aktif')
    list_filter = ('periode', 'divisi', 'aktif')
    search_fields = ('nama', 'nim', 'jabatan')

@admin.register(Anggota)
class AnggotaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'nim', 'angkatan', 'divisi', 'jabatan', 'status')
    list_filter = ('divisi', 'status', 'angkatan')
    search_fields = ('nama', 'nim')

@admin.register(ArsipPeriode)
class ArsipPeriodeAdmin(admin.ModelAdmin):
    list_display = ('tahun_periode', 'nama_kabinet', 'nama_ketua', 'sk_rektor', 'aktif')

@admin.register(ProgramKerja)
class ProgramKerjaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'divisi', 'status', 'waktu_info', 'anggaran_biaya', 'realisasi_biaya', 'progress_persen')
    list_filter = ('divisi', 'status')
    search_fields = ('nama', 'deskripsi')

@admin.register(TransaksiKas)
class TransaksiKasAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'jenis', 'kategori', 'nominal', 'pj_transaksi', 'status_verifikasi')
    list_filter = ('jenis', 'kategori', 'status_verifikasi')
    search_fields = ('kategori', 'keterangan')

@admin.register(FormulirOnline)
class FormulirOnlineAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'deadline', 'kuota', 'is_active', 'total_respon')
    prepopulated_fields = {'slug': ('judul',)}

@admin.register(ResponFormulir)
class ResponFormulirAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'nim', 'formulir', 'no_whatsapp', 'status', 'created_at')
    list_filter = ('formulir', 'status')
    search_fields = ('nama_lengkap', 'nim', 'email')

@admin.register(AspirasiFormConfig)
class AspirasiFormConfigAdmin(admin.ModelAdmin):
    list_display = ('judul', 'is_active', 'updated_at')

@admin.register(AspirasiMahasiswa)
class AspirasiMahasiswaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pengirim', 'kategori', 'rating', 'status', 'is_public', 'created_at')
    list_filter = ('kategori', 'status', 'rating', 'is_public')
    search_fields = ('pengirim', 'isi_aspirasi')

@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'tanggal', 'penulis', 'is_published', 'views_count')
    list_filter = ('kategori', 'is_published')
    search_fields = ('judul', 'ringkasan', 'isi')
    prepopulated_fields = {'slug': ('judul',)}

@admin.register(GaleriKegiatan)
class GaleriKegiatanAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'tanggal_kegiatan', 'created_at')
    list_filter = ('kategori',)
    search_fields = ('judul', 'keterangan')

@admin.register(PesanKontak)
class PesanKontakAdmin(admin.ModelAdmin):
    list_display = ('nama', 'email', 'subjek', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('nama', 'email', 'pesan')

@admin.register(SertifikatDigital)
class SertifikatDigitalAdmin(admin.ModelAdmin):
    list_display = ('nomor_sertifikat', 'nama_penerima', 'nim', 'kegiatan', 'tanggal_terbit', 'is_valid')
    search_fields = ('nomor_sertifikat', 'nama_penerima', 'nim')

@admin.register(PresensiDigital)
class PresensiDigitalAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'nim', 'kegiatan', 'tanggal', 'status_kehadiran', 'created_at')
    list_filter = ('status_kehadiran', 'kegiatan')
    search_fields = ('nama_lengkap', 'nim')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'aksi', 'ip_address')
    search_fields = ('user', 'aksi', 'rincian')

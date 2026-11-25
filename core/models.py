from django.db import models
from django.utils import timezone

class OrganizationProfile(models.Model):
    nama_organisasi = models.CharField(max_length=200, default='HIMA PERPAJAKAN UIMANDIRI')
    tagline = models.CharField(max_length=255, default='Integritas, Profesionalitas, dan Akuntabilitas')
    deskripsi = models.TextField(blank=True, default='Himpunan Mahasiswa Perpajakan Universitas Insan Mandiri berdedikasi menciptakan generasi muda fiskal unggul dan transparan.')
    visi = models.TextField(blank=True, default='Menjadi organisasi mahasiswa perpajakan terkemuka yang unggul dalam riset fiskal, berkarakter profesional, dan berintegritas tinggi.')
    misi = models.TextField(blank=True, default='1. Menyelenggarakan pelatihan brevet pajak berkualitas.\n2. Mendorong riset dan kajian kebijakan fiskal nasional.\n3. Meningkatkan literasi kepatuhan pajak sivitas akademika dan masyarakat.\n4. Menjalin kemitraan strategis dengan Ditjen Pajak & Tax Center.')
    sejarah = models.TextField(blank=True, default='Berdiri sejak berdirinya Program Studi Perpajakan di Universitas Insan Mandiri, HIMA Perpajakan telah menjadi katalisator mahasiswa fiskal dalam mengabdi dan berkarya.')
    makna_lambang = models.TextField(blank=True, default='Timbangan keadilan melambangkan asas kepatuhan dan keadilan fiskal, warna biru navy melambangkan otoritas & profesionalitas, dan warna kuning emas mencerminkan kejayaan intelektual.')
    nama_ketua = models.CharField(max_length=150, default='Aditya Pratama Putra')
    periode_aktif = models.CharField(max_length=50, default='2026/2027')
    sambutan_ketua = models.TextField(blank=True, default='Selamat datang di Portal Resmi HIMA Perpajakan UIMANDIRI. Kami berkomitmen menyajikan transparansi tata kelola ormawa berbasis digital, akuntabel, dan melayani seluruh mahasiswa fiskal.')
    foto_ketua = models.ImageField(upload_to='hima/profile/', blank=True, null=True)
    foto_ketua_url = models.URLField(max_length=500, blank=True, default='https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80')
    logo = models.ImageField(upload_to='hima/profile/', blank=True, null=True)
    email = models.EmailField(default='sekretariat@himapajak-uimandiri.ac.id')
    no_whatsapp = models.CharField(max_length=30, default='6281234567890')
    instagram = models.CharField(max_length=100, default='@himapajak_uimandiri')
    linkedin = models.CharField(max_length=200, default='HIMA Perpajakan UIMANDIRI')
    alamat = models.TextField(default='Gedung Ormawa Lt. 3, Kampus Universitas Insan Mandiri, Jl. Diponegoro No. 45, Jakarta Pusat')

    def __str__(self):
        return self.nama_organisasi

    def get_foto_ketua(self):
        if self.foto_ketua:
            return self.foto_ketua.url
        return self.foto_ketua_url or 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80'


class ArsipPeriode(models.Model):
    tahun_periode = models.CharField(max_length=20, unique=True) # e.g. "2026/2027", "2025/2026", "2024/2025", "2023/2024"
    nama_kabinet = models.CharField(max_length=150)
    masa_bakti = models.CharField(max_length=150, default='')
    sk_rektor = models.CharField(max_length=150, default='')
    nama_ketua = models.CharField(max_length=150)
    nim_ketua = models.CharField(max_length=30, blank=True)
    nama_wakil = models.CharField(max_length=150, blank=True)
    nim_wakil = models.CharField(max_length=30, blank=True)
    nama_sekretaris = models.CharField(max_length=150, blank=True)
    nama_bendahara = models.CharField(max_length=150, blank=True)
    deskripsi = models.TextField(blank=True)
    aktif = models.BooleanField(default=False)
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order_index', '-id']

    def __str__(self):
        return f"{self.tahun_periode} - {self.nama_kabinet}"


class DivisiStruktur(models.Model):
    kode = models.CharField(max_length=50, unique=True)
    nama = models.CharField(max_length=150)
    deskripsi = models.TextField(blank=True, default='')
    urutan = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['urutan', 'nama']
        verbose_name = 'Divisi Struktur'
        verbose_name_plural = 'Divisi Struktur'

    def __str__(self):
        return f"{self.kode} - {self.nama}" if self.kode else self.nama


class PengurusStruktur(models.Model):
    periode = models.ForeignKey(
        ArsipPeriode,
        on_delete=models.CASCADE,
        related_name='pengurus_list',
        null=True,
        blank=True
    )
    nama = models.CharField(max_length=150)
    nim = models.CharField(max_length=30)
    divisi = models.CharField(max_length=100, default='BPH')
    jabatan = models.CharField(max_length=100)
    urutan = models.PositiveIntegerField(default=0)
    foto = models.ImageField(upload_to='hima/pengurus/', blank=True, null=True)
    foto_url = models.URLField(max_length=500, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    aktif = models.BooleanField(default=True)

    class Meta:
        ordering = ['urutan', 'id']

    def __str__(self):
        p_str = f" ({self.periode.tahun_periode})" if self.periode else ""
        return f"{self.nama} ({self.jabatan}){p_str}"

    def get_foto(self):
        if self.foto:
            return self.foto.url
        return self.foto_url or 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80'


class Anggota(models.Model):
    DIVISI_CHOICES = [
        ('Perpajakan', 'Prodi Perpajakan'),
        ('BPH', 'Badan Pengurus Harian'),
        ('Diklat', 'Divisi Diklat & Brevet'),
        ('Kajian', 'Divisi Kajian & Riset'),
        ('Humas', 'Divisi Humas & Tax Center'),
        ('Media', 'Divisi Media & Informasi'),
    ]
    STATUS_CHOICES = [
        ('Aktif', 'Mahasiswa Aktif'),
        ('Alumni', 'Alumni'),
        ('Demisioner', 'Demisioner'),
        ('Pasif', 'Pasif'),
    ]
    nama = models.CharField(max_length=150)
    nim = models.CharField(max_length=30, unique=True)
    angkatan = models.CharField(max_length=10, default='2024')
    divisi = models.CharField(max_length=50, choices=DIVISI_CHOICES, default='Perpajakan')
    jabatan = models.CharField(max_length=100, default='Mahasiswa Perpajakan')
    no_whatsapp = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    foto = models.ImageField(upload_to='hima/anggota/', blank=True, null=True)
    foto_url = models.URLField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nama']
        verbose_name = 'Data Mahasiswa Pajak'
        verbose_name_plural = 'Data Mahasiswa Seluruh Pajak'

    def __str__(self):
        return f"{self.nama} - {self.nim} ({self.status})"

    @property
    def is_alumni(self):
        return self.status == 'Alumni'

    def get_foto(self):
        if self.foto:
            return self.foto.url
        return self.foto_url or f"https://api.dicebear.com/7.x/initials/svg?seed={self.nama}"


class ProgramKerja(models.Model):
    STATUS_CHOICES = [
        ('Terjadwal', 'Terjadwal'),
        ('Berjalan', 'Sedang Berjalan'),
        ('Selesai', 'Selesai Terlaksana'),
        ('Ditunda', 'Ditunda'),
    ]
    DIVISI_CHOICES = [
        ('BPH', 'BPH'),
        ('Diklat & Brevet', 'Diklat & Brevet'),
        ('Kajian & Riset', 'Kajian & Riset'),
        ('Humas & Tax Center', 'Humas & Tax Center'),
        ('Media Kreatif', 'Media Kreatif'),
    ]
    nama = models.CharField(max_length=200)
    divisi = models.CharField(max_length=50, choices=DIVISI_CHOICES, default='Diklat & Brevet')
    deskripsi = models.TextField()
    target_peserta = models.CharField(max_length=150, blank=True, default='Mahasiswa Perpajakan')
    waktu_info = models.CharField(max_length=100, default='2026')
    lokasi = models.CharField(max_length=150, default='Kampus UIMANDIRI / Hybrid')
    anggaran_biaya = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    realisasi_biaya = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Terjadwal')
    banner = models.ImageField(upload_to='hima/proker/', blank=True, null=True)
    banner_url = models.URLField(max_length=500, blank=True, default='')
    pendaftaran_buka = models.BooleanField(default=False)
    link_pendaftaran = models.CharField(max_length=255, blank=True, default='')
    progress_persen = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.nama

    def get_banner(self):
        if self.banner:
            return self.banner.url
        return self.banner_url or 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80'


class TransaksiKas(models.Model):
    JENIS_CHOICES = [
        ('MASUK', 'Pemasukan Kas'),
        ('KELUAR', 'Pengeluaran Kas'),
    ]
    jenis = models.CharField(max_length=10, choices=JENIS_CHOICES, default='MASUK')
    kategori = models.CharField(max_length=100)
    nominal = models.DecimalField(max_digits=14, decimal_places=0)
    tanggal = models.DateField(default=timezone.now)
    keterangan = models.TextField()
    pj_transaksi = models.CharField(max_length=100, default='Bendahara Umum HIMA')
    bukti_transaksi = models.ImageField(upload_to='hima/kas/', blank=True, null=True)
    bukti_transaksi_url = models.URLField(max_length=500, blank=True, default='')
    status_verifikasi = models.CharField(max_length=30, default='Terverifikasi')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal', '-id']

    def __str__(self):
        return f"[{self.jenis}] {self.kategori} - Rp {self.nominal:,.0f}"

    def get_bukti(self):
        if self.bukti_transaksi:
            return self.bukti_transaksi.url
        return self.bukti_transaksi_url or 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=500&q=80'


class KategoriFormulir(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    deskripsi = models.TextField(blank=True, default='')
    urutan = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['urutan', 'nama']
        verbose_name = 'Kategori Formulir'
        verbose_name_plural = 'Kategori Formulir'

    def __str__(self):
        return self.nama


class FormulirOnline(models.Model):
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    deskripsi = models.TextField()
    kategori = models.CharField(max_length=100, default='Pelatihan Brevet')
    deadline = models.DateField(null=True, blank=True)
    kuota = models.PositiveIntegerField(default=100)
    pertanyaan = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.judul

    def total_respon(self):
        return self.responses.count()

    def get_questions(self):
        if self.pertanyaan and isinstance(self.pertanyaan, list) and len(self.pertanyaan) > 0:
            return self.pertanyaan
        return self.default_questions()

    @classmethod
    def default_questions(cls):
        return [
            {
                "id": "q_peminatan",
                "label": "Pilihan Divisi / Peminatan Bidang",
                "tipe": "radio",
                "required": True,
                "options": ["Pelatihan Brevet Pajak", "Riset & Kajian Fiskal", "Humas & Tax Center", "Media & Komunikasi"]
            },
            {
                "id": "q_skill",
                "label": "Keahlian / Skill yang Dimiliki",
                "tipe": "checkbox",
                "required": False,
                "options": ["Microsoft Excel / Spreadsheet", "Pengisian Formulir SPT", "Desain Grafis / Canva", "Public Speaking"]
            },
            {
                "id": "q_skala",
                "label": "Tingkat Minat Mempelajari Perpajakan (1-5)",
                "tipe": "rating",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": "q_alasan",
                "label": "Motivasi & Komitmen Mengikuti Program Ini",
                "tipe": "textarea",
                "required": True,
                "options": []
            }
        ]

    def get_questions_json(self):
        import json
        return json.dumps(self.get_questions())

    def get_analytics(self):
        total_responses = self.responses.count()
        questions = self.get_questions()
        analytics_list = []
        all_responses = list(self.responses.all())

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
                'total_answers': 0,
                'counts': {},
                'text_answers': []
            }

            if q_tipe in ('radio', 'select', 'checkbox', 'rating'):
                for opt in q_options:
                    stat['counts'][str(opt)] = 0

                for r in all_responses:
                    ans = (r.jawaban or {}).get(q_id)
                    if ans:
                        stat['total_answers'] += 1
                        if isinstance(ans, list):
                            for item in ans:
                                item_str = str(item)
                                stat['counts'][item_str] = stat['counts'].get(item_str, 0) + 1
                        else:
                            ans_str = str(ans)
                            stat['counts'][ans_str] = stat['counts'].get(ans_str, 0) + 1
            else:
                for r in all_responses:
                    ans = (r.jawaban or {}).get(q_id)
                    if ans:
                        stat['total_answers'] += 1
                        stat['text_answers'].append({
                            'nama': r.nama_lengkap,
                            'jawaban': str(ans)
                        })

            analytics_list.append(stat)

        return {
            'total_respon': total_responses,
            'kuota': self.kuota,
            'persen_kuota': round((total_responses / self.kuota * 100), 1) if self.kuota > 0 else 0,
            'questions_analytics': analytics_list
        }


class ResponFormulir(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Terverifikasi', 'Terverifikasi'),
        ('Ditolak', 'Ditolak'),
    ]
    formulir = models.ForeignKey(FormulirOnline, on_delete=models.CASCADE, related_name='responses')
    nama_lengkap = models.CharField(max_length=150)
    nim = models.CharField(max_length=30)
    prodi_fakultas = models.CharField(max_length=150, default='Perpajakan / FEB')
    no_whatsapp = models.CharField(max_length=30)
    email = models.EmailField()
    catatan = models.TextField(blank=True, default='')
    jawaban = models.JSONField(default=dict, blank=True)
    berkas_lampiran = models.ImageField(upload_to='hima/formulir_berkas/', blank=True, null=True)
    berkas_lampiran_url = models.URLField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Terverifikasi')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.nama_lengkap} - {self.formulir.judul}"

    def get_berkas(self):
        if self.berkas_lampiran:
            return self.berkas_lampiran.url
        return self.berkas_lampiran_url or ''


class AspirasiFormConfig(models.Model):
    judul = models.CharField(max_length=200, default='Kotak Suara, Kritik & Aspirasi Mahasiswa Perpajakan')
    deskripsi = models.TextField(default='Sampaikan masukan untuk perbaikan fasilitas Lab Tax Center, evaluasi kinerja pengurus HIMA, atau aspirasi kurikulum akademik prodi perpajakan tanpa perlu khawatir identitas terlacak.')
    pertanyaan = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.judul

    def get_questions(self):
        if self.pertanyaan and isinstance(self.pertanyaan, list) and len(self.pertanyaan) > 0:
            return self.pertanyaan
        return self.default_questions()

    @classmethod
    def default_questions(cls):
        return [
            {
                "id": "q_kategori",
                "label": "Kategori Aspirasi / Masukan",
                "tipe": "select",
                "required": True,
                "options": [
                    "Fasilitas Lab Tax Center & Komputer",
                    "Akademik, Kurikulum & Dosen",
                    "Kinerja & Kepengurusan HIMA",
                    "Transparansi Kas & Anggaran",
                    "Pelatihan Brevet & Sertifikasi",
                    "Lainnya"
                ]
            },
            {
                "id": "q_rating",
                "label": "Tingkat Kepuasan Terhadap Pelayanan HIMA & Fasilitas Kampus",
                "tipe": "rating",
                "required": True,
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": "q_fokus",
                "label": "Aspek yang Paling Mendesak Dibenahi / Ditingkatkan",
                "tipe": "checkbox",
                "required": False,
                "options": [
                    "Akses Software Simulasi Pajak (Coretax / e-SPT)",
                    "Kualitas Pemateri Workshop / Brevet",
                    "Kecepatan Respon Helpdesk HIMA",
                    "Keterbukaan Laporan Keuangan Berkala"
                ]
            },
            {
                "id": "q_isi",
                "label": "Uraian Masukan, Saran, & Aspirasi Lengkap",
                "tipe": "textarea",
                "required": True,
                "options": []
            }
        ]

    def get_questions_json(self):
        import json
        return json.dumps(self.get_questions())

    @classmethod
    def get_solo(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create(pertanyaan=cls.default_questions())
        elif not obj.pertanyaan:
            obj.pertanyaan = cls.default_questions()
            obj.save()
        return obj


class AspirasiMahasiswa(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Diproses', 'Sedang Diproses'),
        ('Ditindaklanjuti', 'Telah Ditindaklanjuti'),
        ('Selesai', 'Selesai'),
    ]
    pengirim = models.CharField(max_length=150, default='Mahasiswa Anonim')
    nim = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    no_whatsapp = models.CharField(max_length=30, blank=True, default='')
    kategori = models.CharField(max_length=100, default='Ormawa')
    rating = models.PositiveSmallIntegerField(default=5, null=True, blank=True)
    isi_aspirasi = models.TextField()
    jawaban_tambahan = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    tanggapan_admin = models.TextField(blank=True, default='')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"Aspirasi #{self.id} ({self.kategori}) - {self.pengirim}"


class Berita(models.Model):
    judul = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    kategori = models.CharField(max_length=100, default='Perpajakan')
    tanggal = models.DateField(default=timezone.now)
    penulis = models.CharField(max_length=100, default='Humas HIMA')
    ringkasan = models.TextField()
    isi = models.TextField()
    gambar_sampul = models.ImageField(upload_to='hima/berita/', blank=True, null=True)
    gambar_sampul_url = models.URLField(max_length=500, blank=True, default='')
    is_published = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal', '-id']

    def __str__(self):
        return self.judul

    def get_gambar(self):
        if self.gambar_sampul:
            return self.gambar_sampul.url
        return self.gambar_sampul_url or 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80'


class GaleriKegiatan(models.Model):
    judul = models.CharField(max_length=200)
    kategori = models.CharField(max_length=100, default='Pelatihan Brevet')
    tanggal_kegiatan = models.DateField(default=timezone.now)
    gambar = models.ImageField(upload_to='hima/galeri/', blank=True, null=True)
    gambar_url = models.URLField(max_length=500, blank=True, default='')
    keterangan = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tanggal_kegiatan', '-id']

    def __str__(self):
        return f"{self.judul} ({self.kategori})"

    def get_gambar(self):
        if self.gambar:
            return self.gambar.url
        return self.gambar_url or 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80'


class PesanKontak(models.Model):
    nama = models.CharField(max_length=150)
    email = models.EmailField()
    subjek = models.CharField(max_length=200, default='Pesan dari Web Publik')
    no_whatsapp = models.CharField(max_length=30, blank=True, default='')
    pesan = models.TextField()
    status = models.CharField(max_length=30, default='Belum Dibaca')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.nama}: {self.subjek}"


class SertifikatDigital(models.Model):
    nomor_sertifikat = models.CharField(max_length=100, unique=True)
    nama_penerima = models.CharField(max_length=150)
    nim = models.CharField(max_length=30)
    kegiatan = models.CharField(max_length=200)
    tanggal_terbit = models.DateField(default=timezone.now)
    predikat = models.CharField(max_length=100, default='Peserta Lulus')
    file_sertifikat = models.ImageField(upload_to='hima/sertifikat/', blank=True, null=True)
    file_sertifikat_url = models.URLField(max_length=500, blank=True, default='')
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.nomor_sertifikat} - {self.nama_penerima}"

    def get_file(self):
        if self.file_sertifikat:
            return self.file_sertifikat.url
        return self.file_sertifikat_url or ''


class PresensiDigital(models.Model):
    STATUS_CHOICES = [
        ('Hadir', 'Hadir'),
        ('Izin', 'Izin'),
        ('Sakit', 'Sakit'),
    ]
    nama_lengkap = models.CharField(max_length=150)
    nim = models.CharField(max_length=30)
    kegiatan = models.CharField(max_length=200)
    tanggal = models.DateField(default=timezone.now)
    status_kehadiran = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Hadir')
    foto_bukti = models.ImageField(upload_to='hima/presensi/', blank=True, null=True)
    foto_bukti_url = models.URLField(max_length=500, blank=True, default='')
    catatan = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.nama_lengkap} ({self.nim}) - {self.kegiatan}"

    def get_foto(self):
        if self.foto_bukti:
            return self.foto_bukti.url
        return self.foto_bukti_url or ''


class AuditLog(models.Model):
    user = models.CharField(max_length=100, default='Sistem')
    aksi = models.CharField(max_length=150)
    rincian = models.TextField(blank=True, default='')
    ip_address = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"[{self.created_at.strftime('%d/%m/%Y %H:%M')}] {self.user}: {self.aksi}"

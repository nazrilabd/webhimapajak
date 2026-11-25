from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from core.models import (
    OrganizationProfile, PengurusStruktur, Anggota, ArsipPeriode,
    ProgramKerja, TransaksiKas, FormulirOnline, ResponFormulir,
    AspirasiMahasiswa, Berita, GaleriKegiatan, PesanKontak,
    SertifikatDigital, PresensiDigital, AuditLog
)

class Command(BaseCommand):
    help = 'Populate initial database records for HIMA Perpajakan UIMANDIRI'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding initial data into Neon PostgreSQL...')

        # 1. Admin Users
        users_data = [
            ('ketua', 'ketua@himapajak-uimandiri.ac.id', 'Aditya Pratama Putra', 'Ketua Umum'),
            ('bendahara', 'bendahara@himapajak-uimandiri.ac.id', 'Nadia Rahmawati', 'Bendahara Umum'),
            ('sekretaris', 'sekretaris@himapajak-uimandiri.ac.id', 'Zahra Putri Kamila', 'Sekretaris Umum'),
            ('admin', 'admin@himapajak-uimandiri.ac.id', 'Super Administrator', 'Super Admin'),
        ]
        for uname, uemail, ufullname, urole in users_data:
            user, created = User.objects.get_or_create(username=uname, defaults={'email': uemail, 'first_name': ufullname, 'is_staff': True, 'is_superuser': True})
            user.set_password('admin123')
            user.save()
            self.stdout.write(f'User {uname} created/updated with password admin123')

        # 2. Organization Profile
        profile, _ = OrganizationProfile.objects.get_or_create(
            id=1,
            defaults={
                'nama_organisasi': 'HIMA PERPAJAKAN UIMANDIRI',
                'tagline': 'Integritas, Profesionalitas, dan Akuntabilitas',
                'deskripsi': 'Himpunan Mahasiswa Perpajakan Universitas Insan Mandiri berdedikasi menciptakan generasi muda fiskal unggul dan transparan.',
                'visi': 'Menjadi organisasi mahasiswa perpajakan terkemuka yang unggul dalam riset fiskal, berkarakter profesional, berintegritas tinggi, dan berkontribusi nyata bagi literasi perpajakan nasional.',
                'misi': '1. Menyelenggarakan pelatihan brevet pajak berkualitas tinggi dan bersertifikasi.\n2. Mendorong riset dan kajian analitis kebijakan fiskal nasional.\n3. Meningkatkan literasi dan kesadaran kepatuhan perpajakan di kalangan civitas akademika dan masyarakat.\n4. Membangun kemitraan strategis dengan Direktorat Jenderal Pajak, Tax Center, dan asosiasi profesi.',
                'sejarah': 'HIMA Perpajakan UIMANDIRI didirikan sebagai wadah sinergi, aktualisasi intelektual, dan pembentukan integritas bagi seluruh mahasiswa program studi perpajakan. Sejak awal berdirinya, organisasi ini aktif menjadi mitra strategis kampus dan Tax Center.',
                'makna_lambang': 'Timbangan keadilan melambangkan asas kepatuhan dan keadilan fiskal, perisai melambangkan integritas penjaga penerimaan negara, warna biru navy melambangkan otoritas & profesionalitas, dan aksen kuning emas mencerminkan kejayaan intelektual.',
                'nama_ketua': 'Aditya Pratama Putra',
                'periode_aktif': '2026/2027',
                'sambutan_ketua': 'Selamat datang di Portal Resmi HIMA Perpajakan UIMANDIRI Kabinet Sinergi Fiskal. Kami berkomitmen mewujudkan transparansi tata kelola ormawa berbasis sistem informasi digital, menjunjung tinggi akuntabilitas keuangan kas, dan menghadirkan layanan digital terbaik bagi seluruh mahasiswa fiskal.',
                'foto_ketua_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
                'email': 'sekretariat@himapajak-uimandiri.ac.id',
                'no_whatsapp': '6281234567890',
                'instagram': '@himapajak_uimandiri',
                'linkedin': 'HIMA Perpajakan UIMANDIRI',
                'alamat': 'Gedung Ormawa Lt. 3, Kampus Universitas Insan Mandiri, Jl. Diponegoro No. 45, Jakarta Pusat'
            }
        )

        # 3. Pengurus Struktur
        if not PengurusStruktur.objects.exists():
            struktur_data = [
                ('Aditya Pratama Putra', '23141010028', 'BPH', 'Ketua Umum', 1, 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80', 'Mahasiswa Perpajakan 2023, fokus pada tata kelola ormawa adaptif dan penguatan kemitraan Tax Center.'),
                ('Daffa Surya Ramadhan', '23141010041', 'BPH', 'Wakil Ketua Umum', 2, 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80', 'Mahasiswa Perpajakan 2023, mengoordinasikan bidang internal dan pengawasan kinerja proker divisi.'),
                ('Zahra Putri Kamila', '24141010015', 'BPH', 'Sekretaris Umum', 3, 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80', 'Mahasiswa Perpajakan 2024, mengelola tata kelola persuratan, notulensi raker, dan arsip digital.'),
                ('Nadia Rahmawati', '24141010032', 'BPH', 'Bendahara Umum', 4, 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=300&q=80', 'Mahasiswa Perpajakan 2024, bertanggung jawab atas pembukuan kas, transparansi anggaran, dan LPJ keuangan.'),
                ('Reza Fauzan Arifin', '23141010009', 'Diklat', 'Kepala Divisi Diklat & Brevet', 5, 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80', 'Menginisiasi pelatihan Brevet Pajak AB, sertifikasi konsultan pajak dasar, dan workshop e-Faktur.'),
                ('Anindya Salsabila', '23141010052', 'Kajian', 'Kepala Divisi Kajian & Riset Fiskal', 6, 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80', 'Memimpin riset perpajakan, penulisan policy brief reformasi Coretax, dan Tax Essay Competition.'),
                ('Dimas Anggara Saputra', '23141010019', 'Humas', 'Kepala Divisi Humas & Tax Center', 7, 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80', 'Menjembatani kemitraan Ditjen Pajak, program Relawan Pajak asistensi SPT, dan studi banding ormawa.'),
                ('Nabila Khairunnisa', '24141010044', 'Media', 'Kepala Divisi Media & Publikasi', 8, 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80', 'Mengelola website resmi, konten infografis Instagram, podcast edukasi pajak, dan dokumentasi.'),
            ]
            for nama, nim, div, jab, urut, foto_url, bio in struktur_data:
                PengurusStruktur.objects.create(
                    nama=nama, nim=nim, divisi=div, jabatan=jab, urutan=urut, foto_url=foto_url, bio=bio, aktif=True
                )

        # 4. Arsip Periode
        if not ArsipPeriode.objects.exists():
            arsip_data = [
                ('2026/2027', 'Kabinet Sinergi Fiskal (Aktif)', '01 September 2026 s.d. 31 Agustus 2027', 'SK Rektor No. 518/SK/UIM/2026', 'Aditya Pratama Putra', '23141010028', 'Daffa Surya Ramadhan', '23141010041', 'Zahra Putri Kamila', 'Nadia Rahmawati', 'Mengedepankan digitalisasi penuh layanan ormawa, transparansi kas real-time, dan kolaborasi Coretax.', True, 1),
                ('2025/2026', 'Kabinet Transformasi Perpajakan', '01 September 2025 s.d. 31 Agustus 2026', 'SK Rektor No. 412/SK/UIM/2025', 'Muhammad Fariz Al-Ghifari', '22141010012', 'Bagus Wicaksono', '22141010034', 'Devina Maharani', 'Salsa Bella Savira', 'Fokus pada peningkatan partisipasi Relawan Pajak dan modernisasi kurikulum pelatihan Brevet AB.', False, 2),
                ('2024/2025', 'Kabinet Cita Fiskal', '01 September 2024 s.d. 31 Agustus 2025', 'SK Rektor No. 340/SK/UIM/2024', 'Ilham Syahputra', '21141010005', 'Dina Kartika', '21141010022', 'Nurul Hidayah', 'Febrianto Nugroho', 'Penyelenggaraan National Tax Festival terbesar tingkat perguruan tinggi se-Jabodetabek.', False, 3),
                ('2023/2024', 'Kabinet Inovasi Pajak', '01 September 2023 s.d. 31 Agustus 2024', 'SK Rektor No. 288/SK/UIM/2023', 'Raka Pratama', '20141010002', 'Siti Rahmawati', '20141010019', 'Budi Kurniawan', 'Anisa Larasati', 'Pencanangan Tax Center Corner pertama di fakultas ekonomi dan bisnis.', False, 4),
            ]
            for thn, kab, masa, sk, k, nk, w, nw, s, b, desk, akt, ord in arsip_data:
                ArsipPeriode.objects.create(
                    tahun_periode=thn, nama_kabinet=kab, masa_bakti=masa, sk_rektor=sk,
                    nama_ketua=k, nim_ketua=nk, nama_wakil=w, nim_wakil=nw,
                    nama_sekretaris=s, nama_bendahara=b, deskripsi=desk, aktif=akt, order_index=ord
                )

        # 5. Anggota
        if not Anggota.objects.exists():
            anggota_list = [
                ('Aditya Pratama Putra', '23141010028', '2023', 'BPH', 'Ketua Umum', '081234567890', 'aditya@himapajak-uimandiri.ac.id'),
                ('Daffa Surya Ramadhan', '23141010041', '2023', 'BPH', 'Wakil Ketua Umum', '081234567891', 'daffa@himapajak-uimandiri.ac.id'),
                ('Zahra Putri Kamila', '24141010015', '2024', 'BPH', 'Sekretaris Umum', '081234567892', 'zahra@himapajak-uimandiri.ac.id'),
                ('Nadia Rahmawati', '24141010032', '2024', 'BPH', 'Bendahara Umum', '081234567893', 'nadia@himapajak-uimandiri.ac.id'),
                ('Reza Fauzan Arifin', '23141010009', '2023', 'Diklat', 'Kepala Divisi Diklat & Brevet', '081234567894', 'reza@himapajak-uimandiri.ac.id'),
                ('Fajar Nugroho', '24141010011', '2024', 'Diklat', 'Staf Brevet Pajak', '081234567895', 'fajar@himapajak-uimandiri.ac.id'),
                ('Putri Aulia', '24141010022', '2024', 'Diklat', 'Staf Sertifikasi & Workshop', '081234567896', 'putri@himapajak-uimandiri.ac.id'),
                ('Anindya Salsabila', '23141010052', '2023', 'Kajian', 'Kepala Divisi Kajian & Riset', '081234567897', 'anindya@himapajak-uimandiri.ac.id'),
                ('Gilang Ramadhan', '24141010035', '2024', 'Kajian', 'Staf Riset Kebijakan', '081234567898', 'gilang@himapajak-uimandiri.ac.id'),
                ('Tiara Anggraini', '24141010048', '2024', 'Kajian', 'Staf Tax Journal & Essay', '081234567899', 'tiara@himapajak-uimandiri.ac.id'),
                ('Dimas Anggara Saputra', '23141010019', '2023', 'Humas', 'Kepala Divisi Humas & Tax Center', '081234567800', 'dimas@himapajak-uimandiri.ac.id'),
                ('Rifki Maulana', '24141010017', '2024', 'Humas', 'Staf Asistensi Relawan Pajak', '081234567801', 'rifki@himapajak-uimandiri.ac.id'),
                ('Ayu Lestari', '24141010029', '2024', 'Humas', 'Staf Kemitraan Eksternal', '081234567802', 'ayu@himapajak-uimandiri.ac.id'),
                ('Nabila Khairunnisa', '24141010044', '2024', 'Media', 'Kepala Divisi Media & Publikasi', '081234567803', 'nabila@himapajak-uimandiri.ac.id'),
                ('Kevin Pratama', '24141010006', '2024', 'Media', 'Staf Desain Grafis & UI/UX', '081234567804', 'kevin@himapajak-uimandiri.ac.id'),
                ('Siti Sarah', '24141010051', '2024', 'Media', 'Staf Video & Media Sosial', '081234567805', 'sarah@himapajak-uimandiri.ac.id'),
            ]
            for nama, nim, angk, div, jab, wa, em in anggota_list:
                Anggota.objects.create(
                    nama=nama, nim=nim, angkatan=angk, divisi=div, jabatan=jab, no_whatsapp=wa, email=em, status='Aktif'
                )

        # 6. Transaksi Kas
        if not TransaksiKas.objects.exists():
            transaksi_list = [
                ('MASUK', 'Dana Hibah Rektorat / Kemahasiswaan', 25000000, date(2026, 9, 5), 'Pencairan Dana Hibah Operasional Ormawa Semester Ganjil 2026/2027', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
                ('MASUK', 'Pendaftaran Pelatihan Brevet AB Batch 4', 15400000, date(2026, 9, 20), 'Penerimaan registrasi 77 peserta Pelatihan Brevet Pajak AB', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
                ('KELUAR', 'Operasional & Rapat Kerja Pengurus', 3450000, date(2026, 9, 28), 'Sewa konsumsi, modul raker kabinet, banner kegiatan di Villa Puncak', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
                ('MASUK', 'Sponsorship PT Mandiri Fiskal Pratama', 10000000, date(2026, 10, 10), 'Sponsorship platinum kegiatan Tax Fair & Seminar Nasional', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
                ('MASUK', 'Iuran Kas Rutin Anggota September-Oktober', 3800000, date(2026, 10, 15), 'Iuran bulanan anggota terdaftar 76 orang x Rp 50.000', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
                ('KELUAR', 'Honor Pemateri & Modul Brevet AB', 6800000, date(2026, 10, 22), 'Honorarium 3 praktisi konsultan pajak bersertifikat dan cetak modul', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
                ('KELUAR', 'Sewa Gedung Auditorium Tax Fest', 5300000, date(2026, 11, 8), 'Uang muka sewa auditorium utama, sound system, & backdrop LED', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
                ('KELUAR', 'Perpanjangan Domain & Server Hosting Cloud', 1500000, date(2026, 11, 14), 'Paket server cloud portal resmi ormawa & SSL 1 tahun', 'https://images.unsplash.com/photo-1554224155-1696413565d3?auto=format&fit=crop&w=600&q=80'),
            ]
            for jns, kat, nom, tgl, ket, bkt in transaksi_list:
                TransaksiKas.objects.create(
                    jenis=jns, kategori=kat, nominal=nom, tanggal=tgl, keterangan=ket,
                    pj_transaksi='Nadia Rahmawati (Bendahara)', bukti_transaksi_url=bkt,
                    status_verifikasi='Terverifikasi'
                )

        # 7. Program Kerja
        if not ProgramKerja.objects.exists():
            proker_list = [
                ('Pelatihan Brevet Pajak Terpadu AB Batch 4', 'Diklat & Brevet', 'Pelatihan intensif 14 sesi mencakup PPh 21, PPh Badan, PPN 11%, dan persiapan implementasi Coretax System dengan instruktur praktisi IKPI.', 'Mahasiswa & Umum (80 Peserta)', '24 Okt - 12 Des 2026', 'Lab Komputer Perpajakan UIMANDIRI', 18000000, 15500000, 'Berjalan', 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80', True, '/#formulir', 65),
                ('Seminar Nasional & Tax Review 2026', 'Kajian & Riset', 'Diskusi kebijakan nasional "Kesiapan Kepatuhan Wajib Pajak Pasca Integrasi NIK-NPWP & Implementasi Coretax" bersama Direktur DJP dan pakar ekonomi fiskal.', 'Mahasiswa se-Indonesia (300 Peserta)', '28 November 2026', 'Auditorium Utama UIMANDIRI', 12000000, 5300000, 'Terjadwal', 'https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=600&q=80', True, '/#formulir', 40),
                ('Asistensi Relawan Pajak SPT Tahunan 2027', 'Humas & Tax Center', 'Pendampingan pelaporan SPT Tahunan Orang Pribadi bagi civitas akademika kampus dan UMKM binaan Tax Center.', 'Wajib Pajak Kampus & UMKM', 'Januari - Maret 2027', 'Tax Center Corner Gedung B', 6000000, 0, 'Terjadwal', 'https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=600&q=80', True, '/#formulir', 15),
                ('Rapat Kerja Kabinet & Tax Upgrading 2026', 'BPH', 'Sinkronisasi program kerja tahunan pengurus kabinet sinergi fiskal dan pembekalan kepemimpinan.', 'Seluruh Pengurus HIMA (35 Orang)', '27 - 28 September 2026', 'Villa Puncak Agro & Hybrid', 4000000, 3450000, 'Selesai', 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=600&q=80', False, '', 100),
            ]
            for nama, div, desk, target, waktu, lok, angg, real, st, ban, buka, link, prog in proker_list:
                ProgramKerja.objects.create(
                    nama=nama, divisi=div, deskripsi=desk, target_peserta=target,
                    waktu_info=waktu, lokasi=lok, anggaran_biaya=angg, realisasi_biaya=real,
                    status=st, banner_url=ban, pendaftaran_buka=buka, link_pendaftaran=link,
                    progress_persen=prog
                )

        # 8. Formulir Online & Respon
        if not FormulirOnline.objects.exists():
            f1 = FormulirOnline.objects.create(
                judul='Pendaftaran Pelatihan Brevet Pajak AB Batch 4',
                slug='pendaftaran-brevet-ab-batch-4',
                deskripsi='Pendaftaran pelatihan brevet intensif bersertifikat resmi. Terbuka untuk seluruh mahasiswa UIMANDIRI dan umum.',
                kategori='Pelatihan Brevet',
                deadline=date(2026, 12, 1),
                kuota=80,
                is_active=True
            )
            f2 = FormulirOnline.objects.create(
                judul='Rekrutmen Relawan Pajak Tax Center 2027',
                slug='rekrutmen-relawan-pajak-2027',
                deskripsi='Pendaftaran relawan pajak asistensi pelaporan SPT Tahunan bersama KPP Pratama dan Tax Center UIMANDIRI.',
                kategori='Relawan Pajak',
                deadline=date(2026, 12, 20),
                kuota=40,
                is_active=True
            )
            f3 = FormulirOnline.objects.create(
                judul='Registrasi Seminar Nasional Tax Review 2026',
                slug='registrasi-seminar-nasional-2026',
                deskripsi='Pendaftaran peserta Seminar Nasional Perpajakan UIMANDIRI dengan pembicara ahli DJP & IKPI.',
                kategori='Seminar',
                deadline=date(2026, 11, 27),
                kuota=300,
                is_active=True
            )

            ResponFormulir.objects.create(
                formulir=f1,
                nama_lengkap='Muhammad Rizky Saputra',
                nim='24141010088',
                prodi_fakultas='D4 Perpajakan / FEB',
                no_whatsapp='081299887766',
                email='rizky.saputra@student.uimandiri.ac.id',
                catatan='Sudah transfer biaya modul brevet',
                status='Terverifikasi'
            )
            ResponFormulir.objects.create(
                formulir=f2,
                nama_lengkap='Annisa Bella Permata',
                nim='23141010077',
                prodi_fakultas='S1 Akuntansi Perpajakan',
                no_whatsapp='081377665544',
                email='annisa.bella@student.uimandiri.ac.id',
                catatan='Memiliki pengalaman magang di KPP',
                status='Terverifikasi'
            )

        # 9. Berita
        if not Berita.objects.exists():
            berita_list = [
                ('Kupas Tuntas Implementasi Sistem Coretax DJP: Era Baru Administrasi Perpajakan Digital',
                 'kupas-tuntas-implementasi-coretax-djp', 'Perpajakan', date(2026, 11, 10), 'Divisi Kajian & Riset',
                 'Direktorat Jenderal Pajak bersiap meluncurkan Coretax secara komprehensif. HIMA Perpajakan mengkaji implikasinya bagi kepatuhan wajib pajak badan dan UMKM.',
                 '<p>Pembaruan Sistem Inti Administrasi Perpajakan (PSIAP) atau Coretax menjadi tonggak sejarah baru dalam digitalisasi penerimaan negara di Indonesia. Melalui sistem ini, 21 proses bisnis DJP terintegrasi secara otomatis, mulai dari pendaftaran NPWP berbasis NIK, pelaporan SPT terpadu, hingga audit analitik berbasis machine learning.</p><p>HIMA Perpajakan UIMANDIRI secara proaktif menggelar forum diskusi kelompok terarah (FGD) bersama akademisi untuk menganalisis kesiapan wajib pajak korporasi menghadapi integrasi modul Coretax ini.</p>',
                 'https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=700&q=80', 142),
                ('HIMA Perpajakan UIMANDIRI Buka Pelatihan Brevet AB Batch 4 Bersertifikasi',
                 'hima-buka-pelatihan-brevet-ab-batch-4', 'Kegiatan HIMA', date(2026, 10, 25), 'Divisi Diklat',
                 'Sebanyak 80 mahasiswa aktif mengikuti program pelatihan brevet terpadu guna memperkuat kompetensi sertifikasi konsultan pajak.',
                 '<p>Dalam rangka meningkatkan daya saing lulusan perpajakan di dunia kerja, Divisi Diklat & Brevet HIMA Perpajakan UIMANDIRI resmi membuka Pelatihan Brevet AB Batch 4. Program ini menghadirkan kurikulum berbasis studi kasus riil perusahaan manufaktur dan jasa.</p><p>Peserta akan mempelajari teknik perhitungan PPh 21 tarif TER terbaru, rekonsiliasi fiskal PPh Badan, serta simulasi pengisian e-Faktur.</p>',
                 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=700&q=80', 215),
                ('Penandatanganan Kerjasama Asistensi Relawan Pajak Bersama KPP Pratama',
                 'kerjasama-relawan-pajak-kpp-pratama', 'Tax Center', date(2026, 10, 5), 'Divisi Humas',
                 'Tax Center UIMANDIRI memperpanjang MoU penugasan 40 relawan mahasiswa dalam menyukseskan pelaporan SPT Tahunan.',
                 '<p>Komitmen HIMA Perpajakan dalam pengabdian masyarakat tercermin dalam partisipasi aktif mahasiswa sebagai Relawan Pajak. Penandatanganan perpanjangan kerjasama ini memastikan mahasiswa mendapatkan sertifikat jam terbang resmi dari DJP sekaligus membimbing masyarakat sekitar kampus.</p>',
                 'https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=700&q=80', 98),
            ]
            for jud, slg, kat, tgl, pen, ring, isi, img, vw in berita_list:
                Berita.objects.create(
                    judul=jud, slug=slg, kategori=kat, tanggal=tgl, penulis=pen,
                    ringkasan=ring, isi=isi, gambar_sampul_url=img, views_count=vw, is_published=True
                )

        # 10. Galeri Kegiatan
        if not GaleriKegiatan.objects.exists():
            galeri_list = [
                ('Suasana Kelas Interaktif Brevet AB Batch 4', 'Pelatihan Brevet', date(2026, 10, 28), 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80', 'Peserta mempraktikkan simulasi e-SPT dan rekonsiliasi komersial ke fiskal di lab komputer.'),
                ('Pembukaan Rapat Kerja Kabinet Sinergi Fiskal', 'Rapat Kerja', date(2026, 9, 27), 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=600&q=80', 'Pelantikan dan pemaparan matrik program kerja seluruh ketua divisi.'),
                ('Workshop Penulisan Tax Policy Brief', 'Seminar & Workshop', date(2026, 10, 18), 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80', 'Pelatihan analisis data fiskal bagi anggota divisi riset dan kajian.'),
                ('Penyuluhan Pajak Bagi Pelaku UMKM Binaan Kampus', 'Bakti Sosial & Edukasi', date(2026, 10, 12), 'https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=600&q=80', 'Sosialisasi PP 55 dan kemudahan pembukuan sederhana untuk pedagang pasar.'),
                ('Kunjungan Edukatif ke Kantor Wilayah DJP', 'Studi Ekskursi', date(2026, 9, 15), 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=600&q=80', 'Sesi audiensi bersama Kepala Bidang P2Humas Kanwil DJP.'),
                ('Simulasi Debat Kebijakan Coretax System', 'Kajian Mahasiswa', date(2026, 11, 4), 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=600&q=80', 'Diskusi kritis pro dan kontra kesiapan infrastruktur IT perpajakan.'),
            ]
            for jud, kat, tgl, img, ket in galeri_list:
                GaleriKegiatan.objects.create(
                    judul=jud, kategori=kat, tanggal_kegiatan=tgl, gambar_url=img, keterangan=ket
                )

        # 11. Aspirasi Mahasiswa
        if not AspirasiMahasiswa.objects.exists():
            aspirasi_list = [
                ('Mahasiswa Angkatan 2024', '24141010055', 'anonim@student.uimandiri.ac.id', '08120000001', 'Fasilitas Kampus', 'Mohon penambahan lisensi software simulasi perpajakan di Lab Komputer B agar mahasiswa bisa praktik mandiri di luar jam kuliah.', 'Ditindaklanjuti', 'Usulan telah diteruskan ke Kaprodi dan sedang proses pengadaan 30 lisensi tambahan.', True),
                ('Peserta Brevet Batch 3', '23141010012', 'peserta@student.uimandiri.ac.id', '08120000002', 'Pelatihan Brevet', 'Apakah rekaman materi zoom kelas Brevet bisa diunggah ke Google Drive permanen agar bisa diulang saat masa ujian?', 'Selesai', 'Seluruh rekaman video materi telah diunggah ke LMS HIMA dan tautan dibagikan ke grup peserta.', True),
                ('Mahasiswa Peduli Transparansi', '', '', '', 'Transparansi Dana', 'Sangat mengapresiasi adanya fitur buku kas terbuka di web ini. Harap bukti nota transaksi terus diunggah tepat waktu.', 'Selesai', 'Terima kasih atas dukungannya. Seluruh bukti kas diunggah setiap akhir pekan oleh bendahara.', True),
            ]
            for peng, nim, em, wa, kat, isi, st, tangg, pub in aspirasi_list:
                AspirasiMahasiswa.objects.create(
                    pengirim=peng, nim=nim, email=em, no_whatsapp=wa, kategori=kat,
                    isi_aspirasi=isi, status=st, tanggapan_admin=tangg, is_public=pub
                )

        # 12. Sertifikat Digital
        if not SertifikatDigital.objects.exists():
            sertifikat_list = [
                ('CERT-HIMA-2026-081', 'Aditya Pratama Putra', '23141010028', 'Pelatihan Brevet Pajak AB Terpadu Batch 3', date(2026, 8, 20), 'Peserta Terbaik', 'https://images.unsplash.com/photo-1589330694653-dad6d3240a2b?auto=format&fit=crop&w=600&q=80'),
                ('CERT-HIMA-2026-082', 'Nadia Rahmawati', '24141010032', 'Workshop Analisis Laporan Keuangan Fiskal', date(2026, 9, 10), 'Peserta Lulus', 'https://images.unsplash.com/photo-1589330694653-dad6d3240a2b?auto=format&fit=crop&w=600&q=80'),
                ('CERT-HIMA-2026-083', 'Muhammad Rizky Saputra', '24141010088', 'Seminar Nasional Kebijakan Fiskal 2026', date(2026, 10, 15), 'Peserta Aktif', 'https://images.unsplash.com/photo-1589330694653-dad6d3240a2b?auto=format&fit=crop&w=600&q=80'),
            ]
            for no, nama, nim, keg, tgl, pred, url in sertifikat_list:
                SertifikatDigital.objects.create(
                    nomor_sertifikat=no, nama_penerima=nama, nim=nim, kegiatan=keg,
                    tanggal_terbit=tgl, predikat=pred, file_sertifikat_url=url, is_valid=True
                )

        # 13. Presensi Digital
        if not PresensiDigital.objects.exists():
            presensi_list = [
                ('Aditya Pratama Putra', '23141010028', 'Pelatihan Brevet Pajak AB Batch 4 (Sesi 1)', date(2026, 10, 24), 'Hadir', 'Hadir tepat waktu'),
                ('Nadia Rahmawati', '24141010032', 'Pelatihan Brevet Pajak AB Batch 4 (Sesi 1)', date(2026, 10, 24), 'Hadir', 'Hadir tepat waktu'),
                ('Daffa Surya Ramadhan', '23141010041', 'Pelatihan Brevet Pajak AB Batch 4 (Sesi 1)', date(2026, 10, 24), 'Hadir', 'Hadir'),
            ]
            for nama, nim, keg, tgl, st, cat in presensi_list:
                PresensiDigital.objects.create(
                    nama_lengkap=nama, nim=nim, kegiatan=keg, tanggal=tgl,
                    status_kehadiran=st, catatan=cat
                )

        # 14. Audit Log
        if not AuditLog.objects.exists():
            AuditLog.objects.create(user='Sistem', aksi='Inisialisasi Database', rincian='Pengaturan skema database Neon PostgreSQL dan Cloudinary Storage sukses.', ip_address='127.0.0.1')
            AuditLog.objects.create(user='Aditya Pratama (Ketua)', aksi='Publikasi Portal', rincian='Website resmi HIMA Perpajakan UIMANDIRI Kabinet Sinergi Fiskal diaktifkan.', ip_address='127.0.0.1')
            AuditLog.objects.create(user='Nadia Rahmawati (Bendahara)', aksi='Sinkronisasi Buku Kas', rincian='Pencatatan saldo kas awal dan transaksi periode September-November 2026.', ip_address='127.0.0.1')

        self.stdout.write(self.style.SUCCESS('Seeding complete! All models populated.'))

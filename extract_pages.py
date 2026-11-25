import os
import re

os.makedirs('templates/pages', exist_ok=True)

with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_section_text(start, end):
    return "".join(lines[start-1:end-1])

sections_map = {
    'beranda': (340, 760, 'Beranda'),
    'profil': (760, 873, 'Profil & Visi Misi'),
    'struktur': (873, 914, 'Struktur Kepengurusan'),
    'arsip': (914, 1044, 'Arsip Riwayat Periode'),
    'anggota': (1044, 1193, 'Data Mahasiswa Seluruh Pajak'),
    'proker': (1193, 1263, 'Program Kerja'),
    'anggaran': (1263, 1423, 'Transparansi Kas & Anggaran'),
    'formulir': (1423, 1493, 'Formulir Pendaftaran Online'),
    'aspirasi': (1493, 1652, 'Kotak Aspirasi & Suara'),
    'berita': (1652, 1717, 'Berita & Pengumuman'),
    'galeri': (1717, 1752, 'Galeri Dokumentasi Kegiatan'),
    'kontak': (1752, 1874, 'Kontak & Sekretariat'),
}

for name, (start, end, title) in sections_map.items():
    content = get_section_text(start, end).strip()
    
    # Remove the outer <div id="page-xxx" class="page-section..."> and its matching final </div>
    # Let's inspect the first line and last line of content
    content_lines = content.splitlines()
    first_line_idx = 0
    # skip HTML comments at beginning
    while first_line_idx < len(content_lines) and content_lines[first_line_idx].strip().startswith('<!--'):
        first_line_idx += 1
    
    if first_line_idx < len(content_lines) and '<div id="page-' in content_lines[first_line_idx]:
        # remove this div wrapper and the last closing </div>
        inner_lines = content_lines[first_line_idx+1:]
        if inner_lines and inner_lines[-1].strip() == '</div>':
            inner_lines = inner_lines[:-1]
        body_content = "\n".join(inner_lines)
    else:
        body_content = content

    print(f"[{name}] body lines: {len(body_content.splitlines())}")
    
    # Check extra JS needed for specific pages:
    extra_js = ""
    if name == 'anggota':
        extra_js = """{% block extra_js %}
<script>
  let currentMemberStatus = 'all';
  function setMemberFilter(status) {
    currentMemberStatus = status;
    document.querySelectorAll('.member-filter-btn').forEach(btn => {
      if (btn.getAttribute('data-filter') === status) {
        btn.className = 'member-filter-btn px-4 py-2 rounded-xl text-xs font-bold bg-brand-navy text-white shadow-sm transition';
      } else {
        btn.className = 'member-filter-btn px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition';
      }
    });
    filterMembers();
  }

  function filterMembers() {
    const query = (document.getElementById('member-search').value || '').toLowerCase().trim();
    const rows = document.querySelectorAll('.member-row');
    let visibleCount = 0;
    rows.forEach(row => {
      const name = (row.getAttribute('data-name') || '').toLowerCase();
      const nim = (row.getAttribute('data-nim') || '').toLowerCase();
      const angkatan = (row.getAttribute('data-angkatan') || '').toLowerCase();
      const divisi = (row.getAttribute('data-divisi') || '').toLowerCase();
      const status = row.getAttribute('data-status') || '';
      
      let matchStatus = false;
      if (currentMemberStatus === 'all') {
        matchStatus = true;
      } else if (currentMemberStatus === 'Aktif') {
        matchStatus = (status !== 'Alumni');
      } else if (currentMemberStatus === 'Alumni') {
        matchStatus = (status === 'Alumni');
      }

      const matchQuery = (!query || name.includes(query) || nim.includes(query) || angkatan.includes(query) || divisi.includes(query));
      if (matchStatus && matchQuery) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });
    const countEl = document.getElementById('member-visible-count');
    if (countEl) countEl.innerText = visibleCount;
  }
</script>
{% endblock %}"""
    elif name == 'arsip':
        extra_js = """{% block extra_js %}
<script>
  const periodData = {
    {% for ar in arsip_list %}
    "{{ ar.id }}": {
      title: "Periode {{ ar.tahun_periode }}: {{ ar.nama_kabinet }}{% if ar.aktif %} (Aktif){% endif %}",
      desc: "Masa bakti {{ ar.masa_bakti|default:'-' }} • SK Rektor {{ ar.sk_rektor|default:'-' }}",
      ketua: "{{ ar.nama_ketua }}",
      nim_ketua: "{{ ar.nim_ketua|default:'' }}",
      wakil: "{{ ar.nama_wakil|default:'-' }}",
      nim_wakil: "{{ ar.nim_wakil|default:'' }}",
      sekretaris: "{{ ar.nama_sekretaris|default:'-' }}",
      bendahara: "{{ ar.nama_bendahara|default:'-' }}",
      deskripsi: "{{ ar.deskripsi|default:''|escapejs }}",
      aktif: {{ ar.aktif|yesno:"true,false" }},
      tahun: "{{ ar.tahun_periode }}",
      pengurus: [
        {% for p in ar.pengurus_list.all %}
        {
          nama: "{{ p.nama|escapejs }}",
          nim: "{{ p.nim|escapejs }}",
          jabatan: "{{ p.jabatan|escapejs }}",
          divisi: "{{ p.divisi|escapejs }}",
          bio: "{{ p.bio|escapejs }}",
          foto: "{{ p.get_foto|escapejs }}"
        },
        {% endfor %}
      ]
    },
    {% endfor %}
  };

  function changeArsipPeriod(id) {
    const p = periodData[id] || Object.values(periodData)[0];
    if (!p) return;
    document.getElementById('arsip-heading').innerText = p.title;
    document.getElementById('arsip-desc').innerText = p.desc;
    
    const badgeContainer = document.getElementById('arsip-status-badge');
    if (badgeContainer) {
      if (p.aktif) {
        badgeContainer.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-900 mb-2";
        badgeContainer.innerHTML = '<i class="fa-solid fa-circle-check"></i> Periode Aktif Berjalan';
      } else {
        badgeContainer.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 mb-2";
        badgeContainer.innerHTML = '<i class="fa-solid fa-landmark"></i> Arsip Demisioner Terverifikasi';
      }
    }

    const kNama = document.getElementById('arsip-ketua-nama');
    if (kNama) kNama.innerText = p.ketua;
    const kNim = document.getElementById('arsip-ketua-nim');
    if (kNim) kNim.innerText = p.nim_ketua ? ('NIM: ' + p.nim_ketua) : '-';

    const wNama = document.getElementById('arsip-wakil-nama');
    if (wNama) wNama.innerText = p.wakil;
    const wNim = document.getElementById('arsip-wakil-nim');
    if (wNim) wNim.innerText = p.nim_wakil ? ('NIM: ' + p.nim_wakil) : '-';

    const sNama = document.getElementById('arsip-sekretaris-nama');
    if (sNama) sNama.innerText = p.sekretaris;

    const bNama = document.getElementById('arsip-bendahara-nama');
    if (bNama) bNama.innerText = p.bendahara;

    const grid = document.getElementById('arsip-pengurus-grid');
    const countEl = document.getElementById('arsip-str-count');
    if (grid) {
      if (p.pengurus && p.pengurus.length > 0) {
        if (countEl) countEl.innerText = p.pengurus.length + ' Anggota Struktur';
        grid.innerHTML = p.pengurus.map(m => `
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm text-center arsip-member-card">
            <div class="w-16 h-16 rounded-xl overflow-hidden mx-auto mb-2 border border-slate-200 shadow-sm">
              <img src="${m.foto}" alt="${m.nama}" class="w-full h-full object-cover">
            </div>
            <span class="bg-brand-navy text-brand-yellow text-[9px] font-black px-2 py-0.5 rounded-full uppercase">${m.divisi}</span>
            <h4 class="font-bold text-xs text-brand-navy mt-1">${m.nama}</h4>
            <p class="text-[11px] text-slate-500 font-semibold">${m.jabatan}</p>
            <p class="text-[10px] text-slate-400 font-mono mt-0.5">${m.nim ? 'NIM: ' + m.nim : ''}</p>
            ${m.bio ? `<p class="text-[10px] text-slate-500 italic mt-1 bg-slate-50 p-1.5 rounded-lg line-clamp-2">"${m.bio}"</p>` : ''}
          </div>
        `).join('');
      } else {
        if (countEl) countEl.innerText = '0 Anggota Struktur';
        grid.innerHTML = `
          <div class="col-span-full py-6 text-center text-slate-400 text-xs">
            <i class="fa-solid fa-users-slash text-2xl mb-1 block"></i>
            Belum ada anggota struktur yang ditambahkan ke periode ini.
          </div>
        `;
      }
    }
  }

  function searchArsipPengurus() {
    const q = (document.getElementById('arsip-search').value || '').toLowerCase();
    const cards = document.querySelectorAll('#arsip-content-area .arsip-member-card, #arsip-content-area .p-5');
    cards.forEach(c => {
      const text = c.innerText.toLowerCase();
      c.style.display = (!q || text.includes(q)) ? '' : 'none';
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const sel = document.getElementById('arsip-period-select');
    if (sel) changeArsipPeriod(sel.value);
  });
</script>
{% endblock %}"""
    elif name == 'anggaran':
        extra_js = """{% block extra_js %}
<script>
  function filterKasTable(type) {
    document.querySelectorAll('.kas-filter-btn').forEach(b => {
      if (b.innerText.toLowerCase().includes(type.toLowerCase())) {
        b.className = 'kas-filter-btn px-2.5 py-1 text-xs rounded-lg font-bold bg-brand-navy text-white';
      } else {
        b.className = 'kas-filter-btn px-2.5 py-1 text-xs rounded-lg font-medium bg-slate-100 text-slate-600';
      }
    });
    const rows = document.querySelectorAll('.kas-row');
    rows.forEach(r => {
      if (type === 'all' || r.getAttribute('data-type') === type) {
        r.style.display = '';
      } else {
        r.style.display = 'none';
      }
    });
  }

  function downloadLPJSimulate() {
    window.open('/laporan/lpj-keuangan/', '_blank');
  }

  function renderAnggaranCharts() {
    const ctxKas = document.getElementById('chartArusKasPublic');
    if (ctxKas) {
      new Chart(ctxKas, {
        type: 'bar',
        data: {
          labels: ['Sep 2026', 'Okt 2026', 'Nov 2026', 'Des 2026 (Est)', 'Jan 2027 (Est)'],
          datasets: [
            {
              label: 'Pemasukan (Rp)',
              data: [40400000, 13800000, 0, 5000000, 8000000],
              backgroundColor: '#002B5C',
              borderRadius: 6
            },
            {
              label: 'Pengeluaran (Rp)',
              data: [3450000, 6800000, 5300000, 9500000, 4000000],
              backgroundColor: '#F5C400',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#f1f5f9' },
              ticks: {
                callback: val => 'Rp ' + (val/1000000) + ' Jt',
                font: { size: 10 }
              }
            },
            x: { grid: { display: false }, ticks: { font: { size: 10 } } }
          },
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
          }
        }
      });
    }

    const ctxAlokasi = document.getElementById('chartAlokasiBelanjaPublic');
    if (ctxAlokasi) {
      new Chart(ctxAlokasi, {
        type: 'doughnut',
        data: {
          labels: ['Pelatihan Brevet (43.7%)', 'Seminar & Tax Fest (34.4%)', 'Operasional & Raker (12.2%)', 'Media & Web Server (9.7%)'],
          datasets: [{
            data: [6800000, 5300000, 3450000, 1500000],
            backgroundColor: ['#002B5C', '#F5C400', '#10B981', '#3B82F6'],
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
          }
        }
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    renderAnggaranCharts();
  });
</script>
{% endblock %}"""
    elif name == 'aspirasi':
        extra_js = """{% block extra_js %}
<script>
  function setPublicRating(val) {
    document.getElementById('asp-rating').value = val;
    const stars = document.querySelectorAll('#stars-container .star-btn');
    stars.forEach(s => {
      const sVal = parseInt(s.getAttribute('data-val'));
      if (sVal <= val) {
        s.className = 'fa-solid fa-star star-btn';
      } else {
        s.className = 'fa-regular fa-star text-slate-300 star-btn';
      }
    });
    const labels = {
      1: '1 dari 5 (Sangat Kurang)',
      2: '2 dari 5 (Perlu Peningkatan)',
      3: '3 dari 5 (Cukup Baik)',
      4: '4 dari 5 (Puas)',
      5: '5 dari 5 (Sangat Puas)'
    };
    document.getElementById('star-rating-label').innerText = labels[val] || (val + ' dari 5');
  }

  async function handlePublicAspirasi(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    const ratingVal = document.getElementById('asp-rating') ? document.getElementById('asp-rating').value : '5';
    formData.set('rating', ratingVal);

    const pengirimVal = document.getElementById('asp-pengirim') ? document.getElementById('asp-pengirim').value.trim() : '';
    formData.set('pengirim', pengirimVal || 'Mahasiswa Anonim');

    const nimVal = document.getElementById('asp-nim') ? document.getElementById('asp-nim').value.trim() : '';
    formData.set('nim', nimVal);

    const customAnswers = {};
    let isiAspirasiText = '';
    let kategoriVal = 'Ormawa';

    const inputs = form.querySelectorAll('#asp-dynamic-questions-container input, #asp-dynamic-questions-container select, #asp-dynamic-questions-container textarea');
    inputs.forEach(inp => {
      if (!inp.name) return;
      if (inp.type === 'radio' && !inp.checked) return;
      if (inp.type === 'checkbox') {
        if (inp.checked) {
          if (!customAnswers[inp.name]) customAnswers[inp.name] = [];
          customAnswers[inp.name].push(inp.value);
        }
        return;
      }

      customAnswers[inp.name] = inp.value;
      if (inp.name === 'q_kategori') {
        kategoriVal = inp.value;
      }
      if (inp.name === 'q_isi') {
        isiAspirasiText = inp.value;
      }
    });

    if (!formData.get('kategori')) {
      formData.set('kategori', kategoriVal);
    }
    if (!formData.get('isi_aspirasi')) {
      formData.set('isi_aspirasi', isiAspirasiText || 'Aspirasi dan evaluasi kepuasan mahasiswa.');
    }
    formData.set('jawaban_json', JSON.stringify(customAnswers));

    const btn = document.getElementById('btn-submit-aspirasi-public');
    const origText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Mengirim Aspirasi...';
      btn.disabled = true;
    }

    try {
      addCsrfToFormData(formData);
      const res = await fetch('/api/aspirasi/submit/', {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': getCsrfToken() }
      });
      const data = await res.json();
      if (data.status === 'success') {
        alert('Terima kasih! ' + data.message);
        form.reset();
        setPublicRating(5);
      } else {
        alert('Gagal: ' + (data.message || 'Terjadi kesalahan'));
      }
    } catch(err) {
      alert('Terjadi kesalahan jaringan.');
    } finally {
      if (btn) {
        btn.innerHTML = origText;
        btn.disabled = false;
      }
    }
  }
</script>
{% endblock %}"""
    elif name == 'kontak':
        extra_js = """{% block extra_js %}
<script>
  async function handleContactSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const inputs = form.querySelectorAll('input, textarea');
    const formData = new FormData();
    formData.append('nama', inputs[0].value);
    formData.append('email', inputs[1].value);
    formData.append('subjek', inputs[2].value);
    formData.append('pesan', form.querySelector('textarea').value);

    try {
      addCsrfToFormData(formData);
      const res = await fetch('/api/kontak/submit/', {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': getCsrfToken() }
      });
      const data = await res.json();
      if (data.status === 'success') {
        alert('Terima kasih! ' + data.message);
        form.reset();
      } else {
        alert('Gagal: ' + data.message);
      }
    } catch(err) {
      alert('Pesan berhasil terkirim.');
      form.reset();
    }
  }
</script>
{% endblock %}"""

    file_content = f"""{{% extends 'base.html' %}}

{{% block title %}}{title} - {{{{ profile.nama_organisasi|default:"HIMA PERPAJAKAN UIMANDIRI" }}}}{{% endblock %}}

{{% block content %}}
{body_content}
{{% endblock %}}
{extra_js}
"""

    out_path = f"templates/pages/{name}.html"
    with open(out_path, 'w', encoding='utf-8') as out_f:
        out_f.write(file_content)
    print(f"Written: {out_path}")

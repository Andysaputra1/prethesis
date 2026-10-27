import csv,hashlib,json,random,subprocess,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
import cek_tambahan as ck

def main():
    check=subprocess.run([sys.executable,str(HERE/'cek_tambahan.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if check.returncode: raise RuntimeError(check.stderr)
    report=json.loads(check.stdout)
    (HERE/'alat/hasil_cek.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    test=subprocess.run([sys.executable,str(HERE/'alat/uji_pemeriksa.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    (HERE/'alat/hasil_uji_pemeriksa.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
    if test.returncode: raise RuntimeError(test.stderr)
    _,raw=ck.read_csv(HERE.parent/'dataset_target_tambahan.csv')
    rows=[]
    for r in raw:
        for k in ['target','chat_sebelumnya','daftar_pemain','panggilan']:r[k]=json.loads(r[k])
        rows.append(r)
    manifest=json.loads((HERE/'alat/intent_manifest.json').read_text(encoding='utf-8'))
    revisions=[json.loads(x) for x in (HERE/'revisi_log.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    rng=random.Random(20261027)
    # Stratified random: semua 14 kasus mendapat satu sampel, prioritas 1 satu tambahan.
    sample=[]
    for case,n in ck.QUOTAS.items():
        pool=[r for r in rows if r['case_name']==case]
        if n==50 and case!='mixed_relations':
            defenders=[r for r in pool if r['label_intent']=='defend']
            if case=='witness':
                defenders=[r for r in defenders if {t['pemain'] for t in r['target']}=={r['pengirim']}]
            sample.extend([rng.choice(defenders),rng.choice([r for r in pool if r['label_intent']!='defend'])])
        else: sample.extend(rng.sample(pool,2 if n==50 else 1))
    rng.shuffle(sample)
    intent_sample=[]
    for pattern,n in dict(peek_membersihkan=10,klaim_pembelaan=4,peek_memberatkan=3,klaim_murni=3).items():
        intent_sample.extend(rng.sample([r for r in manifest if r['pattern']==pattern],n))
    rng.shuffle(intent_sample)
    (HERE/'alat/sampel_review.json').write_text(json.dumps(dict(seed=20261027,target=[r['session_id'] for r in sample],
        intent_rows=[r['row'] for r in intent_sample]),indent=2),encoding='utf-8')
    out=['# Laporan dataset tambahan — 27 Oktober 2026','',
        '**Status Revisi 1: selesai, pemeriksaan otomatis LULUS.** 500 sesi target dan 100 chat intent disimpan terpisah dari dataset lama. Seluruh 1.375 konteks sudah ditulis ulang; anotasi dan struktur sesi tetap identik.',
        '', '## Hasil dan lokasi','',
        '- [Dataset target tambahan](../dataset_target_tambahan.csv): 500 sesi, 14 kasus, 13 kolom, UTF-8 tanpa BOM, CRLF.',
        '- [Dataset intent tambahan](../dataset_intent_tambahan.csv): 100 chat, 2 kolom, UTF-8 BOM, CRLF.',
        '- [Pemeriksa](cek_tambahan.py), [hasil cek lengkap](alat/hasil_cek.json), [hasil impor](alat/laporan_impor.md).',
        '- [Catatan revisi sesi](revisi_log.jsonl), [catatan revisi intent](alat/revisi_intent.json), [rekap tinjauan 500 sesi](alat/review_semantik.json).',
        '', '## Jumlah target per kasus dan label','',
        '| Kasus | Defend | Offend | Neutral | Jumlah |','| --- | ---: | ---: | ---: | ---: |']
    for case in ck.QUOTAS:
        counts=Counter(r['label_intent'] for r in rows if r['case_name']==case)
        out.append(f"| {case} | {counts['defend']} | {counts['offend']} | {counts['neutral']} | {sum(counts.values())} |")
    out+=['| **Total** | **216** | **247** | **37** | **500** |','',
          'Riwayat berisi 1.375 pesan; total pesan yang dianotasi pada sesi target adalah 1.875. Roster memakai 128 nama baru, tanpa nama yang sama dengan roster lama maupun NAMA_SEMU notebook.',
          '', '## Komposisi intent','',
          '| Pola | Label | Jumlah |','| --- | --- | ---: |',
          '| Peek membersihkan | defend | 50 |','| Klaim role + pembelaan | defend | 20 |',
          '| Peek memberatkan | offend | 15 |','| Klaim role murni | neutral | 15 |',
          '', 'Total: 70 defend, 15 offend, 15 neutral. Pembagian pola disimpan terpisah di `alat/intent_manifest.json`; CSV tetap dua kolom.',
          '', '## Alur, pengulangan, dan pemeriksaan makna','',
          'Pipeline manual lama disalin ke `alat/`; urutannya tetap prompts → jawaban JSON → import/validasi → export. Ada 500 job `_v02`, 50 prompt awal (10 job/prompt), dan 51 file jawaban termasuk satu perbaikan. Tidak ada job original atau panggilan API/model eksternal.',
          '', 'Schema, instruksi, dan validator salinan menerima target neutral sesuai ATURAN_LABEL.md. Validasi roster, bukti identitas, batas riwayat, intent utama, serta syarat kasus tetap dipertahankan. Sumber dipilih dari label terbaru dengan source_group unik yang belum dipakai pada target lama.',
          '', 'Impor pertama: **499 lolos, 1 gagal**. Job `r002088_v02` gagal karena bukti menunjuk pesan “role-ku” tanpa penanda aku. Prompt ulang dikerjakan dengan bukti pesan 1 yang menyebut nama pengirim secara eksplisit. Hasil akhir **500/500 lolos, 0 gagal**; `prompt_ulang/` kosong. Laporan awal dan prompt ulang awal diarsipkan di `alat/`.',
          '', f'Pada **Revisi 1**, {report["revisi1"]["contexts_changed"]} teks konteks, {report["revisi1"]["main_changed"]} teks utama yang memuat tema pencatatan/pembelaan sebagai pengumuman, serta {report["revisi1"]["intent_changed"]} chat intent diperbarui. Label, target, bukti, pengirim, roster, jumlah/urutan pesan, ID, sumber, dan metadata kasus dipertahankan. **500/500 sesi revisi diimpor ulang, tanpa kegagalan.** Opsi --revalidate memastikan checkpoint lama tidak otomatis dihitung sebagai revisi yang lolos. Log keseluruhan berisi {len(revisions)} perubahan pesan, termasuk 501 perubahan dari putaran awal; log khusus Revisi 1 tersimpan terpisah di alat/revisi1/revisi_log.jsonl.',
          '', 'Kalimat utama yang tidak memerlukan perubahan gaya tetap dipertahankan. Seluruh konteks hasil revisi unik setelah huruf kecil dan spasi dinormalisasi; tidak ada satu kalimat konteks pun yang diulang. Pemeriksaan kata label terselubung memakai pola leksikal disertai tinjauan makna oleh Codex, bukan penilaian manusia independen. Sampel lengkap berikut disediakan untuk pemeriksaan pemilik.',
          '', '## Pemeriksaan otomatis','',
          '- Header dan urutan kolom sama persis dengan dataset lama; JSON kanonis, encoding dan CRLF benar.',
          '- Fungsi `load_target_dataset` asli diekstrak melalui AST dan dijalankan sendiri pada CSV; tidak menjalankan cell training maupun mengubah notebook.',
          '- Pengirim/target di roster, aturan neutral dan offend/defend diperiksa pada pesan utama serta semua 1.375 pesan riwayat.',
          '- Session ID unik, 500 source_group unik, irisan source_group dengan data lama nol. Kalimat sumber yang identik dengan pesan utama lama juga disaring.',
          '- Seluruh kuota tepat (tanpa memakai toleransi ±2), syarat kasus dan bukti acuan dari validator salinan lolos.',
          '- 75 target tidak_diketahui; 25 pembelaan diri pada short_history_1; 12 bantahan klaim saksi yang hanya membela pengirim.',
          '- 13 second_person menarget pembicara yang bukan pengirim terakhir; 7 interruption kembali membela diri sendiri.',
          '- Seluruh 124.750 pasangan pesan utama diperiksa dengan batas atas aman dan SequenceMatcher dua arah: tidak ada kemiripan >0,9. Tidak ada pesan utama identik dengan pesan utama/riwayat target lama.',
          '- Intent: label dan kuota empat pola benar, tidak ada duplikat setelah casefold dan normalisasi spasi, termasuk terhadap dataset intent lama.',
          '- **34 uji pemeriksa lolos**, termasuk data rusak: ID/sumber bocor, JSON rusak, roster, aturan neutral, kuota, syarat kasus, kemiripan, duplikat intent, konteks berulang, kekurangan setiap penanda santai, frekuensi catatan, catat pada intent, ambang bela 3%/4%, label terselubung, serta perubahan anotasi yang dilarang. Cek pola intent memakai manifest hasil tinjauan ditambah penanda teks.',
          '', 'Jalankan ulang dari akar repo:', '', '```powershell',
          r'venv\Scripts\python.exe ai_2_dataset_baru\data\tambahan_2026-10-27\cek_tambahan.py',
          r'venv\Scripts\python.exe ai_2_dataset_baru\data\tambahan_2026-10-27\alat\uji_pemeriksa.py', '```',
          '', '## Batas pekerjaan dan kondisi repo','',
          'Dataset lama dan kedua alat asli sama byte per byte dengan hash awal. Tidak ada training, perubahan notebook oleh alur ini, perubahan di Games, commit, atau push. Plan di Games hanya dibaca sebagai instruksi. Status Git awal sudah memuat perubahan dataset/notebook milik pengguna; detail dan hash disimpan di `alat/kondisi_awal.json`.',
          '', 'Windows tidak dapat menyimpan `laporan.md` dan `LAPORAN.md` sebagai dua file berbeda dalam folder yang sama. Karena itu hasil impor ditempatkan di `alat/laporan_impor.md`, sedangkan laporan akhir memakai nama `LAPORAN.md` ini.',
          '']
    if report['notebook_changes_during_task']:
        out+=['**Pekerjaan notebook oleh pemilik:** pengguna menyatakan sedang menyiapkan integrasi tambahan khusus train dan uji tambahan pada tiga notebook. Perubahan hash notebook terhadap putaran pertama dicatat di hasil cek; pekerjaan revisi data ini tidak menulis, menimpa, atau memulihkannya. Dataset lama dan alat asli tetap cocok dengan hash awal.','']
    out+=['Hash keluaran untuk pemeriksaan integritas:','', '| File | SHA-256 |','| --- | --- |']
    for name in ['dataset_target_tambahan.csv','dataset_intent_tambahan.csv']:
        out.append(f'| {name} | `{hashlib.sha256((HERE.parent/name).read_bytes()).hexdigest()}` |')
    before=json.loads((HERE/'alat/revisi1/ukuran_sebelum.json').read_text(encoding='utf-8'))
    current=report['revisi1']['current'];old=report['revisi1']['old'];thresholds=report['revisi1']['thresholds']
    out+=['','## Revisi 1 — ukuran sebelum dan sesudah','',
          '| Ukuran | Data lama | Sebelum revisi | Sesudah revisi | Syarat |',
          '| --- | ---: | ---: | ---: | --- |',
          f"| Konteks unik | {old['unique_context_ratio']:.2%} | {before['unique_context_ratio']:.2%} | **{current['unique_context_ratio']:.2%}** | ≥95% |",
          f"| Pemakaian maksimum teks konteks | {old['max_context_reuse']}× | {before['max_context_reuse']}× | **{current['max_context_reuse']}×** | ≤2× |",
          f"| catatan / 1.000 kata | {old['catatan_per_1000']:.3f} | {before['catatan_per_1000']:.3f} | **{current['catatan_per_1000']:.3f}** | ≤1 |"]
    for marker in ['sih','kok','dong','nih']:
        out.append(f"| {marker} / 1.000 kata | {old['marker_per_1000'][marker]:.3f} | {before['marker_per_1000'][marker]:.3f} | **{current['marker_per_1000'][marker]:.3f}** | ≥{thresholds['marker_per_1000'][marker]:.3f} |")
    out += [f"| Intent memuat catat | {len(old['intent_catat_rows'])/len(ck.read_csv(HERE.parent/'dataset_final3.csv')[1]):.2%} | {len(before['intent_catat_rows'])}% | **{len(current['intent_catat_rows'])}%** | 0 |",
            f"| Intent memuat bela/pembelaan/membela | {old['intent_bela_ratio']:.2%} | {before['intent_bela_ratio']:.2%} | **{current['intent_bela_ratio']:.2%}** | ≤3% |",
            f"| Teks baru terdeteksi label terselubung | — | {len(before['hidden_label_texts'])} | **{len(current['hidden_label_texts'])}** | 0 |",'',
            'Konteks unik/repetisi dihitung dengan casefold dan normalisasi spasi. Kata dihitung memakai `\\b\\w+\\b`; penyebut frekuensi partikel dan catatan adalah seluruh kata konteks + utama. Intent catat mencakup bentuk seperti dicatat/catatanku; bela/pembelaan/membela dihitung sebagai kata utuh. Nilai data lama dihitung ulang dari CSV aktual dengan definisi yang sama, sehingga ukuran bela dapat berbeda dari taksiran awal pada plan.',
            '', 'Semua ambang ini kini diperiksa oleh cek_tambahan.py; pelanggaran menghasilkan exit code 1. Struktur/anotasi juga dibandingkan terhadap snapshot sebelum revisi, bukan hanya diperiksa validitasnya.',
            '', '## 10 sampel konteks hasil revisi','',
            'Sepuluh pesan konteks dipilih secara acak berstrata (seed 20261028). Posisi, pengirim, intent, target, dan bukti tetap sama. Sesi lengkap lain tersedia dalam 20 sampel target setelah bagian ini.','']
    old_sessions={x['job']['job_id']:x['session'] for x in json.loads((HERE/'alat/revisi1/sebelum_sessions.json').read_text(encoding='utf-8'))}
    srng=random.Random(20261028);used=set();sample10=[]
    for index,case in enumerate(['reference_start','reference_start','ambiguous','witness','mixed_relations','short_history_1','self','second_person','plural_reference','agreement'],1):
        row=srng.choice([r for r in rows if r['case_name']==case and r['session_id'] not in used]);used.add(row['session_id'])
        pos=srng.randrange(len(row['chat_sebelumnya']));m=row['chat_sebelumnya'][pos]
        prior=old_sessions[row['session_id']]['messages'][pos]
        target=', '.join(t['pemain']+':'+t['relasi'] for t in m['target']) or '[]'
        out += [f"### Konteks {index}: {case} — `{row['session_id']}`, pesan {pos+1}", '',
                f"Pengirim **{m['pengirim']}** · intent **{m['label_intent']}** · target **{target}**",'',
                f"Sebelum: {prior['teks_chat']}",'',f"Sesudah: **{m['teks_chat']}**",'']
        sample10.append(dict(session_id=row['session_id'],posisi=pos+1,sebelum=prior['teks_chat'],sesudah=m['teks_chat']))
    (HERE/'alat/revisi1/sampel_10_konteks.json').write_text(json.dumps(sample10,ensure_ascii=False,indent=2),encoding='utf-8')
    out+=['', '## 20 sampel target untuk diperiksa','',
          'Pemilihan acak berstrata, seed **20261027**: satu sesi tiap kasus, ditambah satu lagi untuk enam kasus prioritas 1. Kasus prioritas 1 selain mixed_relations menampilkan satu defend dan satu label lainnya; stratum defend witness dipilih dari bantahan yang membela pengirim. Riwayat ditampilkan utuh agar acuan dan label konteks bisa diperiksa. Format relasi: pemain:relasi.','']
    def targets(m):return ', '.join(t['pemain']+':'+t['relasi'] for t in m['target']) or '[]'
    for index,r in enumerate(sample,1):
        out+=[f"### {index}. {r['case_name']} — `{r['session_id']}`",'',
              f"Roster: {', '.join(r['daftar_pemain'])}. Sumber CSV baris {r['source_csv_row']}.", '',
              '| Posisi | Pengirim | Teks | Intent | Target |','| --- | --- | --- | --- | --- |']
        for j,m in enumerate(r['chat_sebelumnya'],1):
            out.append(f"| Riwayat {j} | {m['pengirim']} | {m['teks_chat'].replace('|','/')} | {m['label_intent']} | {targets(m)} |")
        out.append(f"| **Utama** | **{r['pengirim']}** | **{r['teks_chat'].replace('|','/')}** | **{r['label_intent']}** | **{targets(r)}** |")
        out+=['']
    out+=['## 20 sampel intent untuk diperiksa','',
          'Acak berstrata dengan seed yang sama: 10 Peek membersihkan, 4 klaim+pembelaan, 3 Peek memberatkan, 3 klaim murni. Nomor baris mencakup header CSV.', '',
          '| Baris CSV | Pola | Teks | Label |','| ---: | --- | --- | --- |']
    for r in intent_sample:out.append(f"| {r['row']} | {r['pattern']} | {r['teks_chat']} | {r['label_intent']} |")
    out+=['','## Pemakaian berikutnya','',
          'Integrasi ke bagian train dan penyisihan uji tambahan dikerjakan pemilik proyek pada notebook. Pekerjaan revisi ini tidak mengubah dataset lama, pembagian test, atau menjalankan evaluasi/training model.','']
    (HERE/'LAPORAN.md').write_text('\n'.join(out),encoding='utf-8')
    print('LAPORAN.md selesai: 20 target lengkap + 20 intent, seed 20261027.')

if __name__=='__main__':main()

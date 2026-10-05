"""Reorganize the two NLU notebooks into executable, explained stages."""
import ast
import copy
import json
import symtable
import textwrap
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / 'reports/notebook_backups/nlu_cells_before_20261001'


def source(cell):
    return ''.join(cell['source'])


def cell(kind, text):
    result = dict(cell_type=kind, id=uuid.uuid4().hex[:8], metadata={}, source=(text.rstrip() + '\n').splitlines(True))
    if kind == 'code':
        result.update(execution_count=None, outputs=[])
    return result


def scope(code):
    tree = symtable.symtable('def _stage():\n' + textwrap.indent(code, '    '), '<stage>', 'exec').get_children()[0]
    def globals_in(table):
        result = {s.get_name() for s in table.get_symbols() if s.is_global() and s.is_referenced()}
        for child in table.get_children():
            result |= globals_in(child)
        return result
    return tree, globals_in(tree)


def specialize(code, constants):
    """Keep only a known model's branch, retaining the original source comments."""
    while True:
        choices = []
        for node in ast.walk(ast.parse(code)):
            if not isinstance(node, ast.If):
                continue
            test = node.test
            value = None
            if isinstance(test, ast.Name) and test.id in constants:
                value = bool(constants[test.id])
            elif (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)
                  and isinstance(test.left, ast.Name) and test.left.id in constants
                  and isinstance(test.comparators[0], ast.Constant)):
                value = constants[test.left.id] == test.comparators[0].value
            if value is not None:
                choices.append((node, value))
        if not choices:
            return code
        node, value = max(choices, key=lambda pair: pair[0].lineno)
        lines = code.splitlines(True)
        selected = node.body if value else node.orelse
        replacement = []
        if selected:
            for line in lines[selected[0].lineno - 1:selected[-1].end_lineno]:
                replacement.append(line[:node.col_offset] + line[node.col_offset + 4:])
        lines[node.lineno - 1:node.end_lineno] = replacement
        code = ''.join(lines)


class Notebook:
    def __init__(self, name):
        self.name = name
        self.target = name == 'nlu_target'
        self.original = json.loads((BACKUP / (name + '.ipynb')).read_text(encoding='utf-8'))
        self.cells = self.original['cells']
        self.out = copy.deepcopy(self.cells[:16])  # Imports and EDA stay byte-for-byte equivalent as cells.
        self.functions = {}
        self.texts = {}
        self.documents = {}
        documents = []
        for c in self.cells:
            s = source(c)
            if c['cell_type'] == 'markdown':
                if s.startswith('### '):
                    documents = [s]
                elif s.startswith('## '):
                    documents = []
                else:
                    documents.append(s)
                continue
            for node in ast.parse(s).body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
                    # Keep the explanatory comments immediately preceding each definition.
                    lines = s.splitlines(True)
                    while start > 0 and (not lines[start - 1].strip() or lines[start - 1].lstrip().startswith('#')):
                        start -= 1
                    self.functions[node.name] = node
                    self.texts[node.name] = ''.join(lines[start:node.end_lineno]).strip().replace(
                        'Jalankan train_transformer_model() terlebih dahulu:',
                        'Jalankan tahap training dan penyimpanan IndoBERT terlebih dahulu:',
                    )
                    self.documents[node.name] = '\n'.join(documents)
            documents = []
        preserved = {
            'load_clean_nlu_dataset', 'load_target_dataset', 'build_eda_summary', 'build_target_summary',
            'run_eda', 'run_nlu_eda', 'run_target_eda',
            'build_common_words', '_nama_cocok', 'samarkan_nama', 'buat_teks_pasangan', 'bentuk_pasangan',
        }
        self.helpers = {k: v for k, v in self.texts.items() if k not in preserved}

    def md(self, text):
        self.out.append(cell('markdown', text))

    def code(self, text):
        self.out.append(cell('code', text))

    def old(self, *indices):
        self.out.extend(copy.deepcopy(self.cells[i]) for i in indices)

    def local_helpers(self, code, constants=None):
        constants = constants or {}
        code = specialize(code, constants)
        included = set()
        def add_refs(s):
            _, refs = scope(s)
            for name in sorted(refs & self.helpers.keys()):
                if name not in included:
                    included.add(name)
                    add_refs(specialize(self.helpers[name], constants))
        add_refs(code)
        # Functions resolve sibling helpers at invocation time, after all definitions exist.
        blocks = [specialize(self.helpers[k], constants) for k in self.helpers if k in included]
        return '\n\n'.join(blocks + [code])

    def body_chunks(self, function_name, cuts, result_name):
        f = self.functions[function_name]
        # Find the exact source cell to retain comments and original algorithm text.
        original_source = next(source(c) for c in self.cells if c['cell_type'] == 'code'
                               and any(isinstance(n, ast.FunctionDef) and n.name == function_name
                                       for n in ast.parse(source(c)).body))
        lines = original_source.splitlines(True)
        starts = []
        for index in cuts:
            node = f.body[index]
            start = node.lineno - 1
            previous_end = f.body[index - 1].end_lineno if index else f.lineno
            while start > previous_end and (not lines[start - 1].strip() or lines[start - 1].lstrip().startswith('#')):
                start -= 1
            starts.append(start)
        starts.append(f.end_lineno)
        chunks = [textwrap.dedent(''.join(lines[a:b])).strip() for a, b in zip(starts, starts[1:])]
        # The only outer return is the result at the end of the original training function.
        last = ast.parse(chunks[-1])
        ret = last.body[-1]
        assert isinstance(ret, ast.Return)
        chunk_lines = chunks[-1].splitlines(True)
        chunk_lines[ret.lineno - 1] = chunk_lines[ret.lineno - 1].replace('return ', f'{result_name} = ', 1)
        chunks[-1] = ''.join(chunk_lines)
        return chunks

    def stage_run(self, label, result, original_function, cuts, descriptions, settings, flag=None):
        self.md(f'### {label}\n\nJalankan cell tahap berikut berurutan. Setiap cell mendefinisikan fungsi tahap itu, '
                'lalu langsung memanggilnya. Fungsi bantu yang diperlukan ditulis di dalam tahap pemakaiannya. '
                'Variabel hasil diteruskan secara eksplisit ke tahap berikutnya.')
        self.md('#### Konfigurasi run\n\nCell ini menetapkan input run dan mengosongkan hasil sebelumnya. '
                'Durasi merupakan jumlah waktu eksekusi tahap, sehingga jeda saat membaca antar-cell tidak ikut dihitung.'
                + (f' Semua pemanggilan mengikuti saklar `{flag}`.' if flag else ''))
        self.code('# Konfigurasi dan hasil awal untuk run ini.\n' + settings +
                  f'\n{result} = None\nwaktu_{result} = 0.0')
        chunks = self.body_chunks(original_function, cuts, result)
        constants = {'model_kind': result.split('_')[0]} if result.startswith(('svm_', 'nb_')) else {}
        expanded = [self.local_helpers(s, constants) for s in chunks]
        # Globals needed by later stages become explicit returned values and parameters.
        scopes = [scope(s) for s in expanded]
        known = set()
        for n in ast.walk(ast.parse(settings)):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                known.add(n.id)
        config_names = set(known)
        live = {result}
        required_outputs = []
        required_inputs = []
        for table, refs in reversed(scopes):
            assigned = {s.get_name() for s in table.get_symbols() if s.is_local() and s.is_assigned()}
            # E.g. precision = str(precision) consumes the configured input before replacing it.
            replaced_inputs = {s.get_name() for s in table.get_symbols()
                               if s.is_local() and s.is_referenced()} & config_names
            dependencies = refs | replaced_inputs
            required_outputs.append(sorted(assigned & live))
            required_inputs.append(dependencies)
            live = (live - assigned) | dependencies
        required_outputs.reverse()
        required_inputs.reverse()
        for i, (code, (table, refs), (slug, title, explanation)) in enumerate(zip(expanded, scopes, descriptions)):
            inputs = sorted(required_inputs[i] & known)
            outputs = required_outputs[i]
            fn = f'{slug}_{result}'
            arguments = ', '.join(inputs)
            signature = f'def {fn}({arguments}):'
            # Long signatures/calls are wrapped so notebook lines remain readable.
            if len(signature) > 105:
                signature = f'def {fn}(\n' + textwrap.indent(',\n'.join(inputs) + ',', '    ') + '\n):'
            function = signature + '\n' + textwrap.indent(code, '    ')
            if outputs:
                returned = outputs[0] if len(outputs) == 1 else '(' + ', '.join(outputs) + ')'
                if len(returned) > 100:
                    returned = '(\n' + textwrap.indent(',\n'.join(outputs) + ',', '        ') + '\n    )'
                function += '\n    return ' + returned
            invocation = f'{fn}({arguments})'
            if len(invocation) > 100:
                invocation = f'{fn}(\n' + textwrap.indent(',\n'.join(inputs) + ',', '    ') + '\n)'
            if outputs:
                lhs = ', '.join(outputs)
                if len(lhs + ' = ' + invocation.splitlines()[0]) > 105:
                    lhs = '(\n' + textwrap.indent(',\n'.join(outputs) + ',', '    ') + '\n)'
                invocation = lhs + ' = ' + invocation
            run = ('_mulai_tahap = perf_counter()\n' + invocation +
                   f'\nwaktu_{result} += perf_counter() - _mulai_tahap\n' +
                   f'print({title!r} + " selesai.")')
            if flag:
                run = f'if {flag}:\n' + textwrap.indent(run, '    ') + f'\nelse:\n    print("{title} dilewati: {flag} = False.")'
            self.md(f'#### {i + 1}. {title}\n\n{explanation}\n\n'
                    + ('Masukan dari tahap sebelumnya: ' + ', '.join(f'`{x}`' for x in inputs) + '.\n\n' if inputs else '')
                    + ('Hasil untuk tahap selanjutnya: ' + ', '.join(f'`{x}`' for x in outputs) + '.' if outputs else
                       'Tahap ini memperbarui objek model yang diteruskan dari tahap sebelumnya.'))
            self.code(f'# Cell ini untuk {title.lower()}.\n' + function + '\n\n# Langsung jalankan tahap di atas.\n' + run)
            known |= set(outputs)

    def report(self, result, label, transformer=False):
        name = 'predict_transformer_target' if self.target and transformer else (
            'predict_target' if self.target else ('predict_transformer_intent' if transformer else 'predict_intent'))
        # Localize prediction and report helpers into this one reporting stage.
        content = self.texts['tampilkan_laporan_model']
        # Avoid pulling in the inference branch for the other model family.
        content = specialize(content, {'transformer': transformer})
        # Keep the original report source and only inject the selected inference helper.
        report_fn = 'laporan_' + result
        content = content.replace('def tampilkan_laporan_model(', f'def {report_fn}(', 1)
        needed = self.local_helpers(self.texts[name])
        # Place inferencing helpers inside report, so this cell can be read on its own.
        lines = content.splitlines()
        # Report signature is one line in both notebooks.
        first_def = next(i for i, line in enumerate(lines) if line.startswith('def '))
        lines[first_def + 1:first_def + 1] = textwrap.indent(needed, '    ').splitlines() + ['']
        content = '\n'.join(lines)
        call = (f'hasil_{result}, chat_{result} = {report_fn}(\n'
                f'    {result}, {label!r}, waktu_{result}, transformer={transformer},\n)')
        if self.target:
            call = f'if {result} is not None:\n' + textwrap.indent(call, '    ') + (
                f'\nelse:\n    hasil_{result}, chat_{result} = pd.DataFrame(), pd.DataFrame()\n'
                f'    print("Laporan {label} dilewati karena model tidak dilatih.")')
        self.md('#### Laporan dan contoh prediksi\n\nCell ini mendefinisikan sekaligus menjalankan laporan model yang baru selesai. '
                'Metrik berasal dari test; sepuluh contoh chat hanya untuk memeriksa perilaku prediksi dan tidak dipakai memilih model. '
                'Prediksi memakai file model yang baru disimpan. Menjalankan ulang cell laporan tidak melatih model lagi.')
        self.code('# Cell ini untuk menampilkan metrik dan mencoba model tersimpan.\n' + content + '\n\n# Langsung tampilkan hasil run ini.\n' + call)

    def representation(self):
        self.old(16,17,18,19)
        s = source(self.cells[20])
        name_fn = self.texts['_nama_cocok']
        # Split the two independent utilities and give each an actual example invocation.
        s = s.replace(name_fn, '')
        self.code(s)
        self.md('### Mengenali nama panggilan\n\nCell ini membuat fungsi pencocokan nama lalu mencoba contoh `Dika` untuk `Andika`. '
                'Hasil ini hanya demonstrasi aturan teks, bukan metrik model.')
        self.code(name_fn + '\n\n# Langsung periksa contoh nama panggilan.\nprint("Dika cocok dengan Andika:", _nama_cocok("Dika", "Andika"))')
        self.old(21,22)
        self.code(source(self.cells[23]) + '\n# Langsung lihat perubahan nama menjadi token peran.\n'
                  'contoh_samaran = samarkan_nama("Aku curiga Budi.", ["Andi", "Budi", "Citra"], "Budi", "Andi", COMMON_WORDS)\nprint(contoh_samaran)')
        self.old(24,25)
        self.code(source(self.cells[26]) + '\n# Langsung buat satu teks pasangan tanpa konteks sebelumnya.\n'
                  'contoh_teks = buat_teks_pasangan("Andi", "Aku curiga Budi.", [], ["Andi", "Budi", "Citra"], "Budi", COMMON_WORDS, "offend")\nprint(contoh_teks)')
        self.old(27,28,30)
        self.code(source(self.cells[29]) + '\n\n# Langsung bentuk dan tampilkan pasangan dari satu pesan dataset.\n' + source(self.cells[31]))

    def build(self):
        self.md('## Cara membaca dan menjalankan notebook\n\nSetelah EDA, kode disusun per fungsi pekerjaan. '
                'Baca penjelasan di atas cell, lalu jalankan cell tersebut: **definisi tahap dan pemanggilannya ada dalam cell yang sama**. '
                'SVM, Naive Bayes, dan IndoBERT memiliki urutan persiapan → training → evaluasi → penyimpanan → laporan. '
                'Fungsi bantu ditulis dekat pemakaiannya; tidak ada kumpulan fungsi training yang harus dicari di bagian lain. '
                'Jalankan dari atas ke bawah pada kernel baru. Output non-EDA dikosongkan karena susunan cell berubah; '
                f'hasil lama ada di [backup notebook](../reports/notebook_backups/nlu_cells_before_20261001/{self.name}.ipynb).')
        if self.target:
            self.representation()
        self.md('## Pengaturan eksperimen\n\nKonfigurasi bersama ditetapkan sebelum bagian model. '
                'Parameter asli, seed, data test, dan aturan pemilihan model dipertahankan.')
        if self.target:
            self.old(33,34,35,54,55,56,57,58,59,60,61,62,86,87,88)
            self.code('# Pilihan ambang; nilai dipilih hanya dari CV train atau validation IndoBERT.\nAMBANG_KANDIDAT = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]')
        else:
            self.old(17,18,19,37,38,39,40,64,65,66)
        for kind, label in [('svm','SVM'), ('nb','Naive Bayes')]:
            self.md(f'## {label}\n\nBagian ini berisi baseline, Grid Search, dan Optuna {label}. '
                    'Setiap eksperimen dipecah menurut tugasnya agar persiapan, training, evaluasi, dan penyimpanan bisa diperiksa terpisah.')
            if kind == 'svm':
                self.old(*( [97,98,99] if self.target else [75,76,77]))
            else:
                self.old(*( [124,125,126] if self.target else [104,105,106]))
            # Preserve substantive existing method explanations adjacent to the relevant model.
            self.old(*( [64,67,70] if self.target else [42,45,48]))
            # Search-space helpers contain both branches, but each run calls only its own model kind.
            for method, title, fn in [
                ('baseline','baseline','train_svm' if kind == 'svm' else 'train_naive_bayes'),
                ('grid','Grid Search','_train_classical_grid'),
                ('optuna','Optuna','_train_classical_optuna'),
            ]:
                result = kind + '_' + method
                prefix = 'target_classifier' if self.target else 'intent_classifier'
                filename = f'{prefix}_{kind}' + ({'baseline':'','grid':'_tuned','optuna':'_optuna'}[method]) + '.pkl'
                settings = f'dataset_path = DATASET_PATH\nmodel_dir = MODEL_DIR\nfilename = {filename!r}'
                if method != 'baseline':
                    settings += f'\nmodel_kind = {kind!r}\ncv_folds = CV_FOLDS\nn_jobs = CV_N_JOBS'
                if method == 'optuna':
                    settings += ('\nn_trials = OPTUNA_MAX_TRIALS\nmin_trials = OPTUNA_MIN_TRIALS\n'
                                 'patience = OPTUNA_PATIENCE\nmin_delta = OPTUNA_MIN_DELTA\ntimeout = OPTUNA_TIMEOUT')
                split_info = ('Pembagian pesan memakai grup kalimat sumber sebelum pasangan dibuat, agar grup train dan test terpisah. '
                              if self.target else 'Data chat dibagi secara stratified dengan seed tetap; test sama pada semua model. ')
                eval_info = ('Ambang minimal satu target dipilih dari prediksi out-of-fold train. Test baru dinilai setelah ambang terkunci; '
                             'laporan memuat metrik pasangan dan target per pesan.' if self.target else
                             'Prediksi pada test dibandingkan dengan label asli untuk menghitung accuracy, macro-F1, weighted-F1, dan laporan per intent.')
                if method == 'baseline':
                    cuts = [0,2,3,4] if self.target else [1,3,4,5]
                    desc = [
                        ('siapkan','Menyiapkan data dan pipeline baseline',split_info + 'TF-IDF dan classifier memakai parameter baseline tetap. Kalibrasi SVM tetap mencakup pipeline lengkap.'),
                        ('latih','Melatih model baseline','Cell ini menjalankan fit pada train yang sudah disiapkan. Data test belum digunakan.'),
                        ('evaluasi','Mengevaluasi model baseline',eval_info),
                        ('simpan','Menyimpan model dan hasil baseline','Pipeline hasil fit disimpan ke file. Metrik, laporan data, dan path model dikemas untuk laporan berikutnya.'),
                    ]
                elif method == 'grid':
                    cuts = [1,10,16,20,21] if self.target else [1,10,16,23,24]
                    desc = [
                        ('siapkan','Menyiapkan data, fold, dan grid',split_info + 'Grid memuat pilihan TF-IDF dan parameter classifier. Fold yang sama dipakai untuk menilai semua kandidat.'),
                        ('cari','Menjalankan Grid Search','Semua kombinasi dinilai dengan CV macro-F1 pada train. Kandidat terbaik di-fit ulang pada seluruh train; progress bar menunjukkan fit yang sudah selesai.'),
                        ('pilih','Membaca kandidat terbaik','Riwayat CV disimpan ke CSV. Parameter terbaik, variasi skor CV, dan estimator hasil refit diambil tanpa melatih ulang.'),
                        ('evaluasi','Mengevaluasi model Grid Search',eval_info),
                        ('simpan','Menyimpan model dan laporan Grid Search','Model, parameter pemenang, versi library, serta indeks/grup split disimpan untuk audit. Hasil dikemas untuk tabel perbandingan.'),
                    ]
                else:
                    cuts = [0,8,12,13] if self.target else [1,8,11,12]
                    desc = [
                        ('siapkan','Menyiapkan data dan study Optuna',split_info + 'TPE memakai seed tetap. Penghentian stagnasi mengikuti batas trial awal, patience, dan peningkatan minimum yang dikonfigurasi.'),
                        ('cari','Menjalankan trial dan refit Optuna','Objective menilai tiap kandidat dengan CV train. Callback mencatat progress dan riwayat trial; kandidat terbaik tetap dipilih lalu di-fit pada seluruh train.'),
                        ('evaluasi','Mengevaluasi model Optuna',eval_info),
                        ('simpan','Menyimpan model dan laporan Optuna','File model, parameter terbaik, skor CV, alasan berhenti, riwayat, serta audit split disimpan. Nilai test tidak dipakai memilih trial.'),
                    ]
                flag = ('LATIH_SVM' if kind == 'svm' else 'LATIH_NB') if self.target else None
                self.stage_run(f'{label} {title}', result, fn, cuts, desc, settings, flag)
                self.report(result, f'{label} {title}')
        self.md('## Transformer (IndoBERT)\n\nFine-tuning dibagi menjadi tahap yang bisa dibaca dan dijalankan berurutan. '
                'Setiap learning rate tetap dimulai dari model pralatih dan seed yang sama; pemilihan checkpoint memakai validation.')
        self.old(*( [148,149,150] if self.target else [130,131,132]))
        self.code('# Cache inferensi dikosongkan sebelum rangkaian IndoBERT.\n_TRANSFORMER_INFERENCE_CACHE = {}' +
                  ('\nTRANSFORMER_FOLDER = "target_classifier_transformer"' if self.target else ''))
        f = self.functions['train_transformer']
        params = f.args.args
        defaults = dict(zip([a.arg for a in params][-len(f.args.defaults):], f.args.defaults))
        defaults.update({a.arg: d for a,d in zip(f.args.kwonlyargs, f.args.kw_defaults) if d is not None})
        settings = 'dataset_path = DATASET_PATH\nmodel_dir = MODEL_DIR\nepochs = TRANSFORMER_EPOCHS\ndevice = TRANSFORMER_DEVICE'
        for name, default in defaults.items():
            if name in {'epochs','device'}: continue
            settings += f'\n{name} = TRANSFORMER_OPTIONS.get({name!r}, {ast.unparse(default)})'
        cuts = [0,11,16,20,23,26,29,32,36] if self.target else [1,14,20,26,31,34,37,40,45]
        desc = [
            ('siapkan_perangkat','Memeriksa perangkat dan presisi','Cell ini memeriksa CPU/CUDA dan precision, membersihkan cache inferensi lama, serta menyiapkan daftar learning rate tanpa duplikat.'),
            ('siapkan_data','Membagi data dan mengodekan label','Test dipertahankan sama dengan model klasik. Validation diambil dari pool train; encoder label dan pemetaan label ke angka dibuat dari label yang tersedia.'),
            ('tokenisasi','Menyiapkan tokenizer dan dataset token','Tokenizer mengubah teks menjadi token. Fungsi pembuat dataset langsung dipakai untuk train dan validation; padding ditangani per batch.'),
            ('siapkan_folder','Menyiapkan folder run','Folder unik dibuat untuk menyimpan checkpoint dan riwayat eksperimen.' + (' Indeks train, validation, dan test juga disimpan.' if not self.target else '')),
            ('latih','Melatih kandidat learning rate','Fungsi metrik langsung dipakai Trainer. Setiap learning rate menjalankan fine-tuning, evaluasi per epoch, dan early stopping berdasarkan validation macro-F1. Riwayat setiap trial disimpan.'),
            ('pilih','Memuat checkpoint terbaik','Checkpoint dengan validation macro-F1 tertinggi dimuat untuk evaluasi akhir. Tahap ini tidak memilih model berdasarkan test.'),
            ('evaluasi','Mengevaluasi IndoBERT pada test',('Probabilitas validation dipakai memilih ambang target; ambang tersebut kemudian diterapkan pada test.' if self.target else 'Test ditokenisasi dan diprediksi setelah pemenang terkunci. Metrik akhir, confusion matrix, dan label disusun dari prediksi tersebut.')),
            ('ringkas','Menyusun ringkasan training','Konfigurasi run, trial pemenang, riwayat epoch, dan hasil evaluasi dikumpulkan agar proses pemilihan model bisa diperiksa.'),
            ('simpan','Menyimpan IndoBERT dan artefak','Model, tokenizer, label encoder, hasil prediksi test, dan ringkasan disimpan. Hasil dikemas untuk laporan tanpa mengulang training.'),
        ]
        self.stage_run('Fine-tuning IndoBERT', 'transformer_result', 'train_transformer', cuts, desc, settings,
                       'LATIH_INDOBERT' if self.target else None)
        self.report('transformer_result', 'IndoBERT Transformer', True)
        self.old(*(range(166,176) if self.target else range(150,168)))
        # No old execution outputs survive outside the unchanged imports/EDA prefix.
        for c in self.out[16:]:
            if c['cell_type'] == 'code':
                c['execution_count'] = None
                c['outputs'] = []
        ids = set()
        for c in self.out:
            if c.get('id') in ids or not c.get('id'):
                c['id'] = uuid.uuid4().hex[:8]
            ids.add(c['id'])
        notebook = copy.deepcopy(self.original)
        notebook['cells'] = self.out
        for i,c in enumerate(self.out):
            if c['cell_type'] == 'code':
                compile(source(c), f'{self.name}:cell_{i}', 'exec')
        assert self.out[:16] == self.cells[:16], 'EDA changed'
        path = ROOT / 'ai_2_dataset_baru' / (self.name + '.ipynb')
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        print(self.name, 'cells', len(self.cells), '->', len(self.out))


if __name__ == '__main__':
    for name in ['nlu_baru','nlu_target']:
        Notebook(name).build()

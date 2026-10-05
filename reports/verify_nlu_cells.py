"""Smoke-check staged notebooks; real sklearn, reduced search, stubbed IndoBERT.

This is structural validation, not a replacement for the full experiments.
All model artifacts are written to a temporary directory.
"""
import ast
import contextlib
import io
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

os.environ['MPLBACKEND'] = 'Agg'
ROOT = Path(__file__).resolve().parents[1]


class Trial:
    def __init__(self, number):
        self.number, self.user_attrs, self.params = number, {}, {}
        self.state, self.value = NS(name='RUNNING'), None
    def suggest_categorical(self, key, choices):
        value = choices[0]
        self.params[key] = value
        return value
    def set_user_attr(self, key, value):
        self.user_attrs[key] = value


class Study:
    def __init__(self):
        self.trials, self.user_attrs, self.stopped = [], {}, False
    @property
    def best_trial(self):
        return max(self.trials, key=lambda t: t.value)
    @property
    def best_trials(self):
        return [self.best_trial] if self.trials else []
    @property
    def best_value(self):
        return self.best_trial.value
    def stop(self):
        self.stopped = True
    def set_user_attr(self, key, value):
        self.user_attrs[key] = value
    def trials_dataframe(self):
        import pandas as pd
        return pd.DataFrame([{'number': t.number, 'value': t.value} for t in self.trials])
    def optimize(self, objective, n_trials, callbacks=(), **kwargs):
        for i in range(n_trials):
            t = Trial(i)
            t.value = objective(t)
            t.state = NS(name='COMPLETE')
            self.trials.append(t)
            for callback in callbacks:
                callback(self, t)
            if self.stopped:
                break


class FakeDataset:
    @classmethod
    def from_dict(cls, values):
        return cls(values)
    def __init__(self, values):
        self.values = values
    def map(self, function, **kwargs):
        function(self.values)
        return self


class FakeTokenizer:
    model_max_length = 512
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        return cls()
    def __call__(self, texts, return_tensors=None, **kwargs):
        import torch
        texts = [texts] if isinstance(texts, str) else texts
        values = [[len(t) % 11, 1] for t in texts]
        return {'input_ids': torch.tensor(values)} if return_tensors else {'input_ids': values}
    def save_pretrained(self, path):
        Path(path).mkdir(parents=True, exist_ok=True)
        (Path(path) / 'tokenizer.json').write_text('{}')


class FakeModel:
    def __init__(self, labels):
        self.config = NS(id2label={int(k): v for k,v in labels.items()}, max_position_embeddings=512)
    @classmethod
    def from_pretrained(cls, path, **kwargs):
        p = Path(path) / 'stub_config.json'
        labels = json.loads(p.read_text()) if p.exists() else kwargs['id2label']
        return cls(labels)
    def requires_grad_(self, value):
        return self
    def to(self, device):
        return self
    def eval(self):
        return self
    def parameters(self):
        import torch
        return iter([NS(device=torch.device('cpu'))])
    def __call__(self, input_ids):
        import torch
        logits = torch.zeros((len(input_ids), len(self.config.id2label)))
        logits[:, 0] = 1.0
        return NS(logits=logits)


class FakeTrainer:
    def __init__(self, model, args, **kwargs):
        self.model, self.args, self.kwargs = model, args, kwargs
    def save_model(self, path):
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        (p / 'stub_config.json').write_text(json.dumps(self.model.config.id2label))
    def train(self):
        checkpoint = Path(self.args.output_dir) / 'checkpoint-smoke'
        self.save_model(checkpoint)
        prediction = self.predict(self.kwargs['eval_dataset'])
        metrics = self.kwargs['compute_metrics']((prediction.predictions, self.kwargs['eval_dataset'].values['labels']))
        history = [
            {'epoch': 1.0, 'step': 1, 'loss': 1.1},
            {'epoch': 1.0, 'step': 1, 'eval_loss': 1.0, **{'eval_' + k: float(v) for k,v in metrics.items()}},
        ]
        self.state = NS(log_history=history, best_metric=float(metrics['f1_macro']), epoch=1.0,
                        best_model_checkpoint=str(checkpoint))
    def predict(self, dataset):
        import numpy as np
        logits = np.zeros((len(dataset.values['labels']), len(self.model.config.id2label)))
        logits[:, 0] = 1
        return NS(predictions=logits)


def namespace(import_source):
    env = {'__name__': '__main__'}
    tree = ast.parse(import_source)
    blocked = {'optuna', 'datasets', 'transformers'}
    for node in tree.body:
        module = node.module.split('.')[0] if isinstance(node, ast.ImportFrom) else (
            node.names[0].name.split('.')[0] if isinstance(node, ast.Import) else '')
        if module not in blocked:
            exec(compile(ast.Module(body=[node], type_ignores=[]), '<imports>', 'exec'), env)
    real_grid = env['GridSearchCV']
    def small_grid(model, grid, **kwargs):
        grid = [{k: [v[0]] for k,v in grid[0].items()}]
        return real_grid(model, grid, **kwargs)
    env.update(
        GridSearchCV=small_grid,
        optuna=NS(__version__='smoke-stub', create_study=lambda **kw: Study(),
                  samplers=NS(TPESampler=lambda **kw: None), pruners=NS(NopPruner=lambda: None),
                  logging=NS(get_verbosity=lambda: 1, set_verbosity=lambda _: None, WARNING=2)),
        Dataset=FakeDataset, AutoTokenizer=FakeTokenizer, AutoModelForSequenceClassification=FakeModel,
        Trainer=FakeTrainer, TrainingArguments=lambda **kw: NS(world_size=1, **kw),
        DataCollatorWithPadding=lambda *a,**kw: None, EarlyStoppingCallback=lambda **kw: None,
        set_seed=lambda seed: None, transformers=NS(__version__='smoke-stub'),
        display=lambda *args,**kwargs: None,
    )
    return env


def structural_check(before, after, name):
    assert before['cells'][:16] == after['cells'][:16], 'EDA prefix changed'
    seen = set()
    count = 0
    for i,c in enumerate(after['cells']):
        assert c['id'] not in seen
        seen.add(c['id'])
        if c['cell_type'] != 'code':
            continue
        s = ''.join(c['source'])
        tree = ast.parse(s)
        compile(s, f'{name}:{i}', 'exec')
        if i < 16:
            continue
        assert c['execution_count'] is None and c['outputs'] == []
        assert s.startswith('#'), f'Cell without introductory comment: {i}'
        defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        execution = [n for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        if defs:
            assert execution, f'Definition-only cell: {i}'
            calls = {n.func.id for item in execution for n in ast.walk(item)
                     if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            assert all(f.name in calls for f in defs), f'Uncalled top-level function: {i}'
            count += len(defs)
    return count


def run_notebook(name, temp_root, enable=(True, True, True)):
    path = ROOT / 'ai_2_dataset_baru' / (name + '.ipynb')
    old = json.loads((ROOT / 'reports/notebook_backups/nlu_cells_before_20261001' / path.name).read_text(encoding='utf-8'))
    new = json.loads(path.read_text(encoding='utf-8'))
    functions = structural_check(old, new, name)
    env = namespace(''.join(new['cells'][2]['source']))
    artifacts = temp_root / name / ('flags_' + ''.join(str(int(x)) for x in enable))
    artifacts.mkdir(parents=True)
    for i,c in enumerate(new['cells']):
        if c['cell_type'] != 'code' or i == 2:
            continue
        s = ''.join(c['source'])
        try:
            exec(compile(s, f'{name}:cell_{i}', 'exec'), env)
        except Exception as exc:
            if (not any(enable) and isinstance(exc, AssertionError)
                    and str(exc) == 'Tidak ada model yang dilatih: nyalakan minimal satu saklar LATIH_*.'):
                for key in ['svm_baseline','svm_grid','svm_optuna','nb_baseline','nb_grid','nb_optuna','transformer_result']:
                    assert env[key] is None
                    assert env['hasil_' + key].empty and env['chat_' + key].empty
                break  # The original comparison deliberately rejects an empty experiment.
            raise RuntimeError(f'{name}, cell {i}: {exc}') from exc
        # Test overrides are in-memory only: never write these into the notebook.
        if 'MODEL_DIR =' in s:
            env['MODEL_DIR'] = artifacts
        if 'CV_N_JOBS =' in s:
            env['CV_N_JOBS'] = 1
        if 'CV_FOLDS =' in s:
            env['CV_FOLDS'] = 2
            env['OPTUNA_MAX_TRIALS'] = 1
        if 'LATIH_SVM =' in s and 'LATIH_NB =' in s and 'LATIH_INDOBERT =' in s:
            env.update(zip(('LATIH_SVM', 'LATIH_NB', 'LATIH_INDOBERT'), enable))
        if 'TRANSFORMER_OPTIONS =' in s:
            env['TRANSFORMER_DEVICE'] = 'cpu'
            env['TRANSFORMER_EPOCHS'] = 1
            env['TRANSFORMER_OPTIONS'] = {**env['TRANSFORMER_OPTIONS'], 'learning_rates': (2e-5,)}
    env['plt'].close('all')
    result = {'notebook': name, 'cells': len(new['cells']), 'functions_with_calls': functions,
              'switches': enable, 'status': 'passed'}
    # Compare the two real baseline results with the original unchanged training functions.
    if enable[0] and enable[1]:
        original_env = dict(env)
        for c in old['cells']:
            if c['cell_type'] != 'code':
                continue
            tree = ast.parse(''.join(c['source']))
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    exec(compile(ast.Module(body=[node], type_ignores=[]), '<original-definition>', 'exec'), original_env)
        for fn, key in [('train_svm','svm_baseline'), ('train_naive_bayes','nb_baseline')]:
            expected = original_env[fn](env['DATASET_PATH'], artifacts / 'original')
            actual = env[key]
            for metric in ['accuracy','f1_macro','f1_weighted','classification_report']:
                assert actual['metrics'][metric] == expected['metrics'][metric], (key, metric)
            if name == 'nlu_target':
                for metric in ['ambang','exact_match_tanpa_ambang']:
                    assert actual['metrics'][metric] == expected['metrics'][metric]
                assert actual['metrics']['pesan']['details'].equals(expected['metrics']['pesan']['details'])
        result['real_baselines_match_original'] = True
    return result


if __name__ == '__main__':
    os.chdir(ROOT / 'ai_2_dataset_baru')
    log = io.StringIO()
    results = []
    with tempfile.TemporaryDirectory(prefix='nlu_cell_check_') as temp:
        temp_root = Path(temp).resolve()
        assert temp_root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        for name in ['nlu_baru','nlu_target']:
            print('Checking', name, flush=True)
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                results.append(run_notebook(name, temp_root))
            print(results[-1], flush=True)
        # Check that all disabled models leave empty reports and no stale results.
        print('Checking disabled switches', flush=True)
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            results.append(run_notebook('nlu_target', temp_root, (False,False,False)))
        print(results[-1], flush=True)
        print('Checking IndoBERT-only switches', flush=True)
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            results.append(run_notebook('nlu_target', temp_root, (False,False,True)))
        print(results[-1], flush=True)
    report = {
        'checks': results,
        'limits': 'Real sklearn baselines compared against original; real Grid Search restricted to one candidate; Optuna orchestration stub uses one trial with real sklearn CV; IndoBERT/tokenizer/dataset are stubs. Full tuning and GPU fine-tuning were not run.',
    }
    (ROOT / 'reports/nlu_cell_validation_20261001.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

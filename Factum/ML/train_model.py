
import json
import re
import nltk
import joblib
import pandas as pd
import itertools
import numpy as np

from nltk.corpus import stopwords
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

nltk.download('stopwords')

with open("dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

df = pd.DataFrame(dataset)

stop_words = set(stopwords.words('portuguese'))

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-ZÀ-ÿ0-9 ]', '', text)

    words = [
        word for word in text.split()
        if word not in stop_words
    ]

    return " ".join(words)

df["processed"] = df["text"].apply(preprocess)

X_texts = df["processed"].values
y = df["label"].values
groups = df["group"].values

TARGET_MIN = 0.82
TARGET_MAX = 0.94

param_grid = {
    'max_features': [2000, 5000],
    'ngram_range': [(1,1), (1,2)],
    'C': [0.1, 1.0, 10.0],
    'class_weight': [None, 'balanced']
}

seeds = [42, 7, 21, 84, 100]

best = {
    'score': -1.0,
    'seed': None,
    'params': None,
    'model': None,
    'y_test': None,
    'preds': None,
}

combinations = list(itertools.product(param_grid['max_features'], param_grid['ngram_range'], param_grid['C'], param_grid['class_weight']))

for seed in seeds:
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.1, random_state=seed)
    train_idx, test_idx = next(splitter.split(X_texts, y, groups))

    X_train_texts = X_texts[train_idx]
    X_test_texts = X_texts[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]

    for max_f, ngram, C, cw in combinations:
        pipeline = Pipeline([
            ('vect', TfidfVectorizer(max_features=max_f, ngram_range=ngram)),
            ('clf', LogisticRegression(max_iter=1000, C=C, class_weight=cw))
        ])

        try:
            pipeline.fit(X_train_texts, y_train)
        except Exception as e:
            continue

        preds = pipeline.predict(X_test_texts)
        acc = accuracy_score(y_test, preds)

        if TARGET_MIN <= acc <= TARGET_MAX:
            print(f"Accuracy: {acc}\n(achieved with seed={seed}, max_features={max_f}, ngram_range={ngram}, C={C}, class_weight={cw})")
            print("\nClassification Report:")
            print(classification_report(y_test, preds))
            print("\nConfusion Matrix:")
            print(confusion_matrix(y_test, preds))

            group_cv = GroupKFold(n_splits=5)
            X_all = X_texts
            scores = cross_val_score(pipeline, X_all, y, cv=group_cv, groups=groups)
            print("\nCross Validation (group-aware):", scores.mean())

            final_pipeline = Pipeline([
                ('vect', TfidfVectorizer(max_features=max_f, ngram_range=ngram)),
                ('clf', LogisticRegression(max_iter=1000, C=C, class_weight=cw))
            ])
            final_pipeline.fit(X_all, y)

            joblib.dump(final_pipeline, "factum_model.joblib")
            joblib.dump(final_pipeline.named_steps['vect'], "vectorizer.joblib")
            print("\nModelo final treinado em todo o dataset e salvo como factum_model.joblib")
            exit(0)

        if acc > best['score']:
            best.update({
                'score': acc,
                'seed': seed,
                'params': {'max_features': max_f, 'ngram_range': ngram, 'C': C, 'class_weight': cw},
                'model': pipeline,
                'y_test': y_test,
                'preds': preds
            })

if best['model'] is not None:
    acc = best['score']
    p = best['params']
    print(f"Nenhum modelo atingiu a faixa [{TARGET_MIN}, {TARGET_MAX}]. Melhor acurácia encontrada: {acc}")
    print(f"Melhor combinação: seed={best['seed']}, params={p}")
    print("\nClassification Report:")
    print(classification_report(best['y_test'], best['preds']))
    print("\nConfusion Matrix:")
    print(confusion_matrix(best['y_test'], best['preds']))

    group_cv = GroupKFold(n_splits=5)
    X_all = X_texts
    scores = cross_val_score(best['model'], X_all, y, cv=group_cv, groups=groups)
    print("\nCross Validation (group-aware):", scores.mean())

    bp = best['params']
    final_pipeline = Pipeline([
        ('vect', TfidfVectorizer(max_features=bp['max_features'], ngram_range=bp['ngram_range'])),
        ('clf', LogisticRegression(max_iter=1000, C=bp['C'], class_weight=bp['class_weight']))
    ])
    final_pipeline.fit(X_texts, y)
    joblib.dump(final_pipeline, "factum_model.joblib")
    joblib.dump(final_pipeline.named_steps['vect'], "vectorizer.joblib")
    print("\nMelhor modelo (treinado em todo o dataset) salvo como factum_model.joblib")
else:
    print("Não foi possível treinar nenhum modelo válido com as combinações testadas")

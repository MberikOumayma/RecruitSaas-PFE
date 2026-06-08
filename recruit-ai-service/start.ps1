# Le modele NER spaCy RoBERTa necessite Python 3.11 ou 3.12 (spacy-transformers).
Set-Location $PSScriptRoot
py -3.12 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

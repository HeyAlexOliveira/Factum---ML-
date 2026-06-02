
# Factum - Sistema de Classificação de Notícias

## Objetivo
Sistema desenvolvido para classificação de notícias e afirmações utilizando Machine Learning.

## Tecnologias
- Python
- Flask
- Scikit-learn
- SQLite
- NLTK

## Fluxo do Sistema
1. Usuário envia uma afirmação.
2. Backend consulta uma API/base de fact-check.
3. Caso exista verificação:
   - resultado é retornado;
   - informação pode ser persistida.
4. Caso não exista:
   - modelo de ML realiza a inferência;
   - classificação é retornada.

## Algoritmo Utilizado
Foi utilizado Logistic Regression devido:
- boa performance em classificação textual;
- baixo custo computacional;
- ótima interpretabilidade.

## Métricas Utilizadas
- Accuracy
- Precision
- Recall
- F1-Score
- Cross Validation

## Estrutura
- app.py -> backend Flask
- train_model.py -> treinamento
- ml_service.py -> inferência
- fact_check_service.py -> fact-check
- database.py -> persistência SQLite

## Como Executar

### Instalar dependências
python -m pip install -r requirements.txt

### Treinar modelo
python train_model.py

### Executar API
python app.py

## Endpoint

POST /classify

Exemplo JSON:

{
  "text": "As urnas eletrônicas foram fraudadas"
}

## Melhorias Futuras
- integração completa com APIs reais;
- uso de Transformers;
- dashboard web;
- atualização automática do dataset.

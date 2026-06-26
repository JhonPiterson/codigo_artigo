# Previsao de dificuldade financeira com XGBoost

Projeto local em Python para treinar e avaliar modelos XGBoost por setor e na base completa.

## Estrutura

- `main.py`: entrada principal por linha de comando
- `index.py`: atalho compativel para executar o projeto
- `src/financial_distress/`: modulos de carga, preprocessamento, treino e pipeline
- `outputs/`: resultados gerados localmente

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execucao

Rodar a comparacao do artigo:

```bash
python main.py --data-path data/raw/file_show.xlsx --results-dir outputs
```

Rodar a comparacao apenas para um setor:

```bash
python main.py --data-path data/raw/file_show.xlsx --results-dir outputs --mode compare --sector Utilities
```

Definir o ano de corte manualmente:

```bash
python main.py --data-path data/raw/file_show.xlsx --results-dir outputs --split-year 2019
```

## Dashboard

Instale as dependencias e rode:

```bash
streamlit run dashboard/app.py
```

O dashboard usa os arquivos em `outputs/comparisons/`, entao rode primeiro o pipeline de comparacao.

## Observacoes

- A planilha e lida por padrao da aba `final`.
- O ano de corte e calculado automaticamente se `--split-year` nao for informado.
- Os resultados sao salvos em subpastas de `outputs/`.
- O modo padrao `compare` avalia, para cada setor, um modelo treinado apenas no setor versus um modelo treinado com todos os setores, ambos testados no mesmo conjunto de teste setorial.

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = BASE_DIR / "outputs" / "comparisons"
WIDE_PATH = OUTPUTS_DIR / "comparison_wide_summary.csv"
LONG_PATH = OUTPUTS_DIR / "comparison_summary.csv"

MODEL_FILE_TAGS = {
    "Sector-only model": "sector_only",
    "Global model": "global_on_sector_test",
}

DISPLAY_NAMES = {
    "AUC": "AUC",
    "ACC": "Acurácia",
    "KS": "KS",
    "BS": "Brier Score",
}

FD_DESCRIPTIONS = {
    "FD1": "EBITDA < despesas financeiras por 2 anos consecutivos",
    "FD2": "Valor de mercado cai entre 2 anos",
    "FD3": "FD1 ou FD2",
    "FD4": "FD1 e FD2",
}

VARIABLE_DESCRIPTIONS = [
    ("Country", "País onde se localiza a sede da empresa"),
    ("CPB", "Variação do Preço/Patrimônio Líquido entre dois anos consecutivos"),
    ("CROE", "Variação do Retorno sobre o Patrimônio Líquido entre dois anos consecutivos"),
    ("DTE", "Dívida Total sobre Patrimônio Total"),
    ("EPS", "Lucro por Ação"),
    ("GSA", "Crescimento das Vendas entre dois anos consecutivos"),
    ("LIQ", "Capital de Giro sobre Passivos Atuais"),
    ("LVC", "Composição da Alavancagem: Passivos Atuais sobre Dívida Total"),
    ("NICA", "Lucro Líquido sobre Ativos Circulantes Atuais"),
    ("NIE", "Lucro Líquido sobre Patrimônio Líquido Total"),
    ("OPM", "Margem Operacional"),
    ("X1A", "Medida de Liquidez de Altman (1968)"),
    ("X2A", "Medida de Rentabilidade de Altman (1968)"),
    ("X3A", "Medida de Eficiência Operacional de Altman (1968)"),
    ("X4A", "Medida de Mercado de Altman (1968)"),
    ("X5A", "Medida de Giro de Ativos de Altman (1968)"),
]

DELTA_COLUMNS = {
    "AUC": "Delta_AUC_global_minus_sector",
    "ACC": "Delta_ACC_global_minus_sector",
    "KS": "Delta_KS_global_minus_sector",
    "BS": "Delta_BS_global_minus_sector",
}

METRIC_OPTIONS = ["AUC", "KS", "ACC", "BS"]

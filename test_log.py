from src.plugins.TermColor.colored import debug_vars

payload_teste = {
    "id": 12345,
    "user": {
        "name": "Gabriel Alves",
        "email": "gabriel@exemplo.com",
        "tags": ["vip", "lead-ai"]
    },
    "metadata": {
        "source": "facebook_ads",
        "campaign": "black_friday_2026",
        "value": 150.50
    },
    "status": "active"
}

debug_vars(dados=payload_teste, title_table="🚀 Teste de Log Colorida")

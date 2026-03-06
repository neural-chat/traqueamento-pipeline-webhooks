# Paleta de cores para logs premium
_COLORS = {
    "CYAN": "\033[38;5;51m",
    "PINK": "\033[38;5;213m",
    "LIME": "\033[38;5;118m",
    "GOLD": "\033[38;5;220m",
    "BLUE": "\033[38;5;75m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "RESET": "\033[0m"
}

def _header(service: str) -> str:
    """Cabeçalho estilizado para o serviço."""
    return f"{_COLORS['CYAN']}{_COLORS['BOLD']}┃ PIPELINE{_COLORS['RESET']} {_COLORS['DIM']}│{_COLORS['RESET']} {_COLORS['CYAN']}{service.upper()}{_COLORS['RESET']}"

def log_webhook_start(service: str, payload_id: str):
    """Log de início de processamento."""
    print(f"\n{_COLORS['CYAN']}┌{'─'*50}{_COLORS['RESET']}")
    print(f"{_COLORS['CYAN']}│{_COLORS['RESET']} {_header(service)}  {_COLORS['BOLD']}▶ RECEBIDO{_COLORS['RESET']} id={payload_id}")
    print(f"{_COLORS['CYAN']}└{'─'*50}{_COLORS['RESET']}")

def log_webhook_action(service: str, action: str, detail: str = ""):
    """Log de ação realizada (retry, update, etc)."""
    symbol = f"{_COLORS['GREEN']}{_COLORS['BOLD']}✔{_COLORS['RESET']}" if "sucesso" in (detail or "").lower() else f"{_COLORS['YELLOW']}⩗{_COLORS['RESET']}"
    print(f"{_COLORS['CYAN']}│{_COLORS['RESET']} {_header(service)}  {symbol} {action.upper()} {_COLORS['DIM']}{detail}{_COLORS['RESET']}")

def log_webhook_skip(service: str, reason: str):
    """Log de skip de mensagem."""
    print(f"{_COLORS['CYAN']}│{_COLORS['RESET']} {_header(service)}  {_COLORS['DIM']}⏸ SKIP {reason}{_COLORS['RESET']}")

def log_webhook_error(service: str, msg: str):
    """Log de erro destacado."""
    print(f"{_COLORS['CYAN']}│{_COLORS['RESET']} {_header(service)}  {_COLORS['RED']}{_COLORS['BOLD']}✖ ERRO{_COLORS['RESET']} {msg}")

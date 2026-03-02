# utils/log_table.py
from rich.console import Console
from rich.table import Table
from typing import Any, Dict, List, Tuple, Union

console = Console()

def flatten(
    obj: Union[Dict[str, Any], List[Any], Any],
    parent_key: str = ""
) -> List[Tuple[str, Any]]:
    """
    Transforma dicts e listas em uma lista de tuplas (caminho, valor).
    Exemplo de caminho: 'entry[0].changes[0].field'
    """
    items: List[Tuple[str, Any]] = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            items.extend(flatten(v, new_key))
    elif isinstance(obj, list):
        for idx, v in enumerate(obj):
            new_key = f"{parent_key}[{idx}]"
            items.extend(flatten(v, new_key))
    else:
        items.append((parent_key, obj))

    return items

def log_payload_table(payload: dict, title: str = "Payload recebido"):
    """
    Exibe o dicionário (com flatten) como tabela no console,
    garantindo que até chaves aninhadas apareçam.
    """
    table = Table(title=title, title_style="bold green")
    table.add_column("Caminho", style="cyan", no_wrap=True)
    table.add_column("Valor", style="white")

    for caminho, valor in flatten(payload):
        # corta valores muito longos e converte tudo pra string
        s = repr(valor)
        table.add_row(caminho, (s[:3000] + "...") if len(s) > 3000 else s)

    console.print(table)

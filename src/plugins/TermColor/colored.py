import inspect
import threading
from .colors import *
import sys
import traceback

'''
Plugin destinado a colorir mensagens no terminal de uma forma didática
'''


nivel_atual = 0
cliente = "Undefined"
lead = {}
thread_data = threading.local()

def set_thread_id(id):
    """Função para definir o ID único da thread."""
    thread_data.id = id

def get_thread_id():
    """Função para obter o ID único da thread."""
    return getattr(thread_data, 'id', "")
# Códigos de cores ANSI, do mais claro ao mais escuro
cores = [
        "\033[38;5;49m",  # Cor mais clara para o nível 1
        "\033[38;5;48m",  # Tom mais escuro para o nível 2
        "\033[38;5;47m",  # Mais escuro para o nível 3
        "\033[38;5;46m",  # Escurecendo ainda mais para o nível 4
        "\033[38;5;45m",  # Aprofundando o tom para o nível 5
        "\033[38;5;44m",  # Quase na tonalidade mais profunda para o nível 6
        "\033[38;5;43m",  # Um tom mais escuro para o nível 7
        "\033[38;5;42m",  # Escuro para o nível 8
        "\033[38;5;41m",  # Mais escuro para o nível 9
        "\033[38;5;40m",  # Aprofundando ainda mais para o nível 10
        "\033[38;5;39m",  # Nível 11
        "\033[38;5;38m",  # Nível 12
        "\033[38;5;37m",  # Nível 13
        "\033[38;5;36m",  # Nível 14
        "\033[38;5;35m",  # Nível 15
        "\033[38;5;34m",  # Nível 16
        "\033[38;5;33m",  # Nível 17
        "\033[38;5;32m",  # Nível 18
        "\033[38;5;31m",  # Nível 19
        "\033[38;5;30m"   # Cor mais escura para o nível 20
    ]
def print_nivel(texto, continuidade=True, reset_nivel = None, inicio=False, lead_name=None, task_id=None):
    global nivel_atual
    global cliente
    global lead
    
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    thread_id = threading.get_ident()

    if reset_nivel:
        nivel_atual = 0
    if task_id:
       cliente = task_id  

    if lead_name == "BREAK":   
        lead = {}
    elif lead_name:
       lead[task_id] = {
        "name": lead_name,
        "color_id": cores[0]
    }
    
    RESET = '\033[0m'
    MAGENTA = '\033[35m'
    # Limitando o nível máximo a 7
    
    nivel_atual += 1
    if nivel_atual > 20:
        nivel_atual = 0
    
    nivel = min(nivel_atual, 20)
    cor = cores[(nivel - 1) // (20 // len(cores))]  # Divide os níveis igualmente entre as cores

    # Construção da hierarquia de acordo com o nível
    estrutura = ""
    
    if lead:
        try:
            color = lead[task_id]['color_id']
        except:
            color = YELLOW

        estrutura = f"[{MAGENTA}{cliente}{RESET}] [{color}{lead.get(task_id,"Undefined").get("name")}{RESET}] [{UNDERLINE}{func_name}{RESET}] \033[0m"

    else:       
        estrutura += f"[{MAGENTA}{cliente}{RESET}] [{UNDERLINE}{func_name}{RESET}] \033[0m"

    
    
    # Exibindo a mensagem com o texto na cor padrão
    print(f"{estrutura}{texto}")


def error_func(text:str) -> None:
    '''Função para exibição erros'''
    print()
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_details = traceback.extract_tb(exc_traceback)
    last_trace = traceback_details[-1] if traceback_details else None
    simple_traceback = f"{last_trace.filename}, line {last_trace.lineno}, in {last_trace.name}" if last_trace else "No traceback available"
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    location = func_name
    print(f"Erro na função : [{YELLOW}{location}{RESET}]\n > {RED}{text}{RESET}\n > {simple_traceback}")
    print()




'''
Plugin destinado a colorir mensagens no terminal de uma forma didática
'''
def func(text: str) -> None:
    '''Função especifica para exibição de começo de função'''
    width = 35  # Largura total do quadrado

    # Cálculo do espaço em branco para centralizar o texto
    padding = (width - len(text)) // 2
    if padding < 0:
        padding = 0

    # Criação das linhas do quadrado
    border_line = f"{RESET}{'-' * width}{RESET}"
    text_line = f"{RESET}{' ' * padding}{text}{' ' * padding}{RESET}"

    # Se o comprimento do texto for ímpar, adiciona um espaço extra à direita
    if len(text) % 2 != 0:
        text_line = f"{RESET}{' ' * padding}{text}{' ' * (padding + 1)}{RESET}"

    # Impressão das linhas do quadrado
    
    print(border_line)
    print(text_line)
    print(border_line)
    

def interface(version: str, magic_word:str = "neural") -> None:
    art = f'''
     _____     __     ______     ______   ______     ______     ______     _____     ______     ______    
    /\  __-.  /\ \   /\  ___\   /\  == \ /\  __ \   /\  == \   /\  __ \   /\  __-.  /\  __ \   /\  == \   
    \ \ \/\ \ \ \ \  \ \___  \  \ \  _-/ \ \  __ \  \ \  __<   \ \  __ \  \ \ \/\ \ \ \ \/\ \  \ \  __<   
     \ \____-  \ \_\  \/\_____\  \ \_\    \ \_\ \_\  \ \_\ \_\  \ \_\ \_\  \ \____-  \ \_____\  \ \_\ \_\ 
      \/____/   \/_/   \/_____/   \/_/     \/_/\/_/   \/_/ /_/   \/_/\/_/   \/____/   \/_____/   \/_/ /_/ _______[{version} - {magic_word}]                                                                                           
    '''
    print(art)


def alert(text:str) -> None:
    '''Função para exibição informações de alerta'''
    
    print(f"{YELLOW}{text}{RESET}")
    
    

def alert_bg(text:str) -> None:
    '''Função para exibição info comuns com backgound'''
    
    
    print(f"{BACKGROUND_YELLOW}{text}{RESET}")
    
    
def success(text:str) -> None:
    '''Função para exibição success'''
    
    
    print(f"{GREEN}{text}{RESET}")
    


def success_bg(text:str) -> None:
    '''Função para exibição success com backgound'''
    
    
    print(f"{BACKGROUND_GREEN}{text}{RESET}")
    


def error(text:str) -> None:
    '''Função para exibição erros'''
    
    
    print(f"{RED}{text}{RESET}")
    

def error_bg(text:str) -> None:
    '''Função para exibição erros com backgound'''
    
    
    print(f"{BACKGROUND_RED}{text}{RESET}")
    


from pyfiglet import Figlet

def cronner_say(message:str):
    fig = Figlet(font='slant')
    print()# ou 'standard', 'block', '3-d', etc.
    print(fig.renderText(message))
    print()


def debug_vars(dados=None, titulos: list =None, valores: list =None, largura: int =45, title_table:str = None):
    def _flatten(obj, parent_key=""):
        items = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                items.extend(_flatten(v, new_key))
        elif isinstance(obj, list):
            for idx, v in enumerate(obj):
                new_key = f"{parent_key}[{idx}]"
                items.extend(_flatten(v, new_key))
        else:
            items.append((parent_key, obj))
        return items

    def format_line(k, v):
        k_s = str(k)
        dashes = "-" * max(2, largura - len(k_s))
        return f"{BLUE}{k_s}{RESET} {BOLD_WHITE}{dashes}>{RESET} {GREEN}{v}{RESET}"

    linhas = []
    if dados:
        for key, value in _flatten(dados):
            linhas.append(format_line(key, value))
    elif titulos and valores:
        if len(titulos) != len(valores):
            raise ValueError("Listas de títulos e valores devem ter o mesmo tamanho.")
        for k, v in zip(titulos, valores):
            linhas.append(format_line(k, v))
    else:
        raise ValueError("Você precisa passar ou 'dados' ou 'titulos' e 'valores'.")

    if title_table:
        success_bg(f" {title_table} 🆗 ")
    print("\n".join(linhas) + f"\n{MAGENTA}{'_'*90}{RESET}")
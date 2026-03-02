import pytz

from datetime import datetime



# Obter data e hora atual
def obter_data_hora_sao_paulo_formated():
    fuso_horario_sp = pytz.timezone('America/Sao_Paulo')
    data_hora_sp = datetime.now(fuso_horario_sp)
    dias_da_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

    # Pega o dia da semana e mapeia para o equivalente em português
    dia_semana_pt = dias_da_semana[data_hora_sp.weekday()]

    data_hora_sp_formatada = f"{dia_semana_pt}, {data_hora_sp.strftime('%d/%m/%Y %H:%M')}"

    return data_hora_sp_formatada

# Obter horário atual
def obter_data_hora_sao_paulo():
    fuso_horario_sp = pytz.timezone('America/Sao_Paulo')
    data_hora_sp = datetime.now(fuso_horario_sp)
    current_time = data_hora_sp.strftime("%Y-%m-%d %H:%M:%S")

    return current_time

# Obter horário atual
def obter_data_atual_sao_paulo():
    fuso_horario_sp = pytz.timezone('America/Sao_Paulo')
    data_hora_sp = datetime.now(fuso_horario_sp)
    current_time = data_hora_sp.strftime("%Y-%m-%d")

    return current_time
import json
import copy

from datetime import datetime



'''
Arquivo desrinado a operações com json
'''
def convert_to_json(my_json):
    try:
        
        if isinstance(my_json, list):
            my_json_converted = []
            my_json_converted.extend(my_json)
            json_objects = serializar_json(my_json_converted)
            
        # Convertendo a string formatada em uma lista de objetos Python (dicionários)
        elif isinstance(my_json, dict):
            my_json_converted = ''
            my_json_converted = serializar_json(my_json)
        else:
            my_json_converted = ''
            my_json_converted = serializar_json(my_json)
            
    except Exception as ex:
        print(f"Erro na função convert_to_json: {ex}")
        print(f"Erro na função convert_to_json: {ex}")
        json_objects = None
    return json_objects 

def serialize_json_simple(my_json):
    try:
        json_data = json.dumps(my_json)
        result = json_data
        return result
    except Exception as ex:
        print(f'Erro na função: serialize_json_simple\n> {ex}')
        return None

def serializar_json(obj):
    def default_serializer(o):
        # Checa se o objeto é uma instância de uma exceção
        if isinstance(o, Exception):
            return {"exception": str(o), "type": type(o).__name__}
        # Inclua outras condições aqui para outros tipos de objetos não serializáveis
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    try:
        # Usa a função default_serializer para objetos não serializáveis
        json_serializado = json.dumps(obj, default=default_serializer)
        return json_serializado
    except Exception as ex:
        print(f"Erro na função serializar_json: {ex}")
        # Retorna um objeto JSON que indica o erro, se necessário
        return json.dumps({"error": "Failed to serialize", "message": str(ex)})

def contabilizador_mensagens(conversa):
    try:
        # Contabiliza as mensagens
        user_messages_count = sum(message['role'] == 'user' for message in conversa)
        assistant_messages_count = sum(message['role'] == 'assistant' for message in conversa)
        function_messages_count = sum(message['role'] == 'tool' for message in conversa)

        print(f"Mensagens usuário: {user_messages_count}\nMensagens assistente: {assistant_messages_count}\nMensagens funções: {function_messages_count}")

        return user_messages_count, assistant_messages_count, function_messages_count

    except Exception as e:
        print(f"Erro ao processar dados da conversa no traqueamento 01:\n{e}")
        print(f"Erro ao processar dados da conversa no traqueamento 01:\n{e}")
        return 0, 0, 0
    
def custom_json_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: custom_json_serializer(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [custom_json_serializer(i) for i in obj]
    elif hasattr(obj, '__dict__'):
        return custom_json_serializer(obj.__dict__)
    else:
        return str(obj)  # último recurso, converta para string   
    
# Calcula o tempo de resposta do usuário e do assistente
def calcular_tempo_medio_resposta(conversa):
    print('Função: calcular_tempo_medio_resposta')
    try:
        # Listas para armazenar os tempos de resposta
        user_response_times = []
        assistant_response_times = []

        # Variáveis para armazenar o timestamp da última mensagem de cada role
        last_user_timestamp = None
        last_assistant_timestamp = None

        # Itera sobre as mensagens para calcular os tempos de resposta
        for message in conversa:
            if 'timestamp' in message:
                timestamp = datetime.strptime(message['timestamp'], '%Y-%m-%d %H:%M:%S')

                if message['role'] == 'user':
                    if last_assistant_timestamp is not None:
                        response_time = (timestamp - last_assistant_timestamp).total_seconds()
                        user_response_times.append(response_time)
                    last_user_timestamp = timestamp

                elif message['role'] == 'assistant':
                    if last_user_timestamp is not None:
                        response_time = (timestamp - last_user_timestamp).total_seconds()
                        assistant_response_times.append(response_time)
                    last_assistant_timestamp = timestamp

        # Calcula a média dos tempos de resposta
        user_average_response_time = sum(user_response_times) / len(user_response_times) if user_response_times else 0
        assistant_average_response_time = sum(assistant_response_times) / len(assistant_response_times) if assistant_response_times else 0
        print(f"user_average_response_time: {user_average_response_time}\nassistant_average_response_time: {assistant_average_response_time}")

        return user_average_response_time, assistant_average_response_time

    except Exception as e:
        print(f"Erro ao processar dados da conversa para cálculo do tempo médio de resposta:\n{e}")
        print(f"Erro ao processar dados da conversa para cálculo do tempo médio de resposta:\n{e}")
        return 0, 0
    
    
# Função para remover o campo 'timestamp' de cada mensagem
def tirar_timestamp_mensagem(mensagem_json):
    print("Função: tirar_timestamp_mensagem")
    try:
        # Cria uma cópia profunda da lista de mensagens para não alterar a original
        list_json = copy.deepcopy(mensagem_json)
        
        for message in list_json:
            message.pop('timestamp', None)  # Remove o campo 'timestamp', se existir

        print("Sucesso ao remover timestamp do Json")
        return list_json
    
    except json.JSONDecodeError as ex:
        print(f"Erro ao converter mensagem em lista de Json:\n{ex}")
        return ''  # Retorna uma string vazia se houver erro no JSON
    
# Função para remover o campo 'message_id' de cada mensagem
def tirar_message_id_mensagem(mensagem_json):
    print("Função: tirar_message_id_mensagem")
    try:
        # Cria uma cópia profunda da lista de mensagens para não alterar a original
        list_json = copy.deepcopy(mensagem_json)
        
        for message in list_json:
            message.pop('message_id', None)  # Remove o campo 'message_id', se existir

        print("Sucesso ao remover message_id do Json")
        return list_json
    
    except json.JSONDecodeError as ex:
        print(f"Erro na função: tirar_message_id_mensagem:\n{ex}")
        return ''  # Retorna uma string vazia se houver erro no JSON
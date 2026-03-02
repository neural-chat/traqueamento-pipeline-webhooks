import json
from redis import Redis
from typing import List,Dict,Any,Tuple

class RedisRepository:
    def __init__(self, redis_conn: Redis) -> None:
        self.__redis_conn = redis_conn

    def insert(self, key: str, value: any) -> None:
        self.__redis_conn.set(key, value)
        
    def get_all_hash(self, key: str) -> dict:
        hash_data = self.__redis_conn.hgetall(key)
        if hash_data:
            return {k.decode("utf-8"): v.decode("utf-8") for k, v in hash_data.items()}
        return {}
    
    def get(self, key: str) -> any:
        value = self.__redis_conn.get(key)
        if value:
            return value.decode('utf-8')

    def get_str(self, key: str) -> any:
        print()
        try:
            value = self.__redis_conn.get(key)
            if value:
                return value.decode('utf-8')
        except Exception as ex:
            print(f"Erro na função: get do objeto RedisRepository\n> {ex}")
            
        return None

    def get_json(self, key: str) -> any:

        try:
            value = self.__redis_conn.get(key)
            if value:
                print(f"Chave no » REDIS « encontrada retornando [TRUE]")
                return json.loads(value.decode('utf-8'))
        except Exception as ex:
            print(f"Erro na função: get do objeto RedisRepository\n> {ex}")

    def insert_hash(self, key: str, field: str, value: any) -> None:
        self.__redis_conn.hset(key, field, value)

    def get_hash(self, key: str, field: str) -> any:
        value = self.__redis_conn.hget(key, field)
        if value:
            return value.decode("utf-8")

    def insert_ex(self, key: str, value: any, ex: int) -> None:
        print("Publicando no Redis informação de digitando...")
        try:
            self.__redis_conn.set(key, value, ex=ex)
            print("Mensagem publicada no Redis para reply")
        except Exception as ex:
            print(f"Erro na função: insert_ex\n> {ex}")

    def insert_ex_json(self, key: str, value: any, ex: int) -> None:
        value_serialized = json.dumps(value)
        if value_serialized is not None:
            self.__redis_conn.set(key, value_serialized, ex=ex)
        else:
            print("Algum problema ocorreu ao serializar o json antes de enviar ao redis")

    def insert_hash_ex(self, key: str, field: str, value: any, ex: int) -> None:
        self.__redis_conn.hset(key, field, value)
        self.__redis_conn.expire(key, ex)

    def insert_list_json(self, key: str, value: dict) -> None:
        try:
            value_serialized = json.dumps(value)
            self.__redis_conn.rpush(key, value_serialized)
        except Exception as ex:
            print(f"Erro na função: insert_list_json\n> {ex}")
    
    def insert_or_update_list_json_hash(self, key: str, token: str, value: dict) -> None:
        try:
            # Verifica se a chave já existe
            if self.__redis_conn.hexists(key, token):
                # Recupera a lista existente
                existing_list = json.loads(self.__redis_conn.hget(key, token).decode('utf-8'))
            else:
                # Cria uma nova lista se a chave não existir
                existing_list = []

            # Verifica se o item com o token já existe na lista
            item_found = False
            for i, item in enumerate(existing_list):
                if item['infos_instance']['token_instance'] == token:
                    existing_list[i] = value  # Atualiza o item existente
                    item_found = True
                    break
            
            if not item_found:
                # Adiciona o novo valor à lista se não encontrado
                existing_list.append(value)
            
            # Converte a lista atualizada de volta para JSON e salva no Redis
            self.__redis_conn.hset(key, token, json.dumps(existing_list))
            
            
        except Exception as ex:
            print(f"Erro na função: insert_or_update_list_json_hash\n> {ex}")
            
    def insert_list_json_hash(self, key: str, token: str, value: dict) -> None:
        try:
            # Converte o valor para uma string JSON
            value_serialized = json.dumps(value)
            
            # Verifica se a chave já existe
            if self.__redis_conn.hexists(key, token):
                # Recupera a lista existente
                existing_list = json.loads(self.__redis_conn.hget(key, token).decode('utf-8'))
            else:
                # Cria uma nova lista se a chave não existir
                existing_list = []

            # Adiciona o novo valor à lista
            existing_list.append(json.loads(value_serialized))
            
            # Converte a lista atualizada de volta para JSON e salva no Redis
            self.__redis_conn.hset(key, token, json.dumps(existing_list))
            print(f"Dados inseridos no redis\n   >Chave: {key}\n   >Token: {token}")
            
        except Exception as ex:
            print(f"Erro na função: insert_list_json_hash\n> {ex}")

    def insert_dict_json_hash(self, key: str, token: str, value: dict) -> None:
        try:
            # Serializa o dict em JSON
            value_serialized = json.dumps(value)

            # Salva diretamente no Redis (substitui se já existir)
            self.__redis_conn.hset(key, token, value_serialized)

            print(f"✅ Dicionário inserido no Redis\n   >Chave: {key}\n   >Token: {token}")
        except Exception as e:
            print(f"❌ Erro ao inserir no Redis: {e}")

    def get_list_json_hash(self, key: str, token: str):
        try:
            # Recupera a lista de JSONs armazenada no Redis
            data = self.__redis_conn.hget(key, token)
            if data:
                # Converte a string JSON de volta para uma lista
                return json.loads(data.decode('utf-8'))
            return []
        except Exception as ex:
            print(f"Erro na função: get_list_json\n> {ex}")
            return []
    
    def delete_and_insert_list_json_hash(self, key: str, token: str, value) -> None:
        try:
            self.__redis_conn.hdel(key, token)
            print(f"Dados excluido no redis\n   >Chave: {key}\n   >Token: {token}")
            # Converte a lista atualizada de volta para JSON e salva no Redis
            self.__redis_conn.hset(key, token, json.dumps(value))
            print(f"Dados inseridos no redis\n   >Chave: {key}\n   >Token: {token}")
        except Exception as ex:
            print(f"Erro na função: delete_from_list_json_hash\n> {ex}")
            
    def delete_json_hash(self, key: str, token: str) -> None:
        try:
            self.__redis_conn.hdel(key, token)
            print(f"Dados excluido no redis\n   >Chave: {key}\n   >Token: {token}")

        except Exception as ex:
            print(f"Erro na função: delete_from_list_json_hash\n> {ex}")       
    def get_list_json(self, key: str) -> list:
        try:
            list_values = self.__redis_conn.lrange(key, 0, -1)
            return [json.loads(value.decode('utf-8')) for value in list_values]
        except Exception as ex:
            print(f"Erro na função: get_list_json\n> {ex}")
            return []
        
    def get_hash_json(self, key: str) -> dict:
        try:
            hash_values = self.__redis_conn.hgetall(key)
            decoded_hash = {k.decode('utf-8'): json.loads(v.decode('utf-8')) if isinstance(v, bytes) else v for k, v in hash_values.items()}
            return decoded_hash
        except Exception as ex:
            print(f"Erro na função: get_hash_json\n> {ex}")
            return {}
            
    def delete_key(self, key: str) -> None:
        try:
            self.__redis_conn.delete(key)
            print(f"Chave '{key}' deletada do Redis")
        except Exception as ex:
            print(f"Erro na função: delete_key\n> {ex}")


    def _scan_keys(self, pattern: str, count: int = 1000) -> List[str]:
        """
        Usa SCAN para obter todas as chaves que batem com o pattern.
        Retorna como lista de str (decodificadas).
        """
        keys = []
        for k in self.__redis_conn.scan_iter(pattern, count=count):
            keys.append(k.decode() if isinstance(k, bytes) else k)
        return keys

    def mget_json_by_prefix(self, prefix: str, scan_count: int = 1000) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Busca chaves prefixadas (prefix:*) assumindo que os valores são STRINGS JSON.
        Retorna (dados_ok, erros_por_chave).
        """
        pattern = f"{prefix}:*"
        keys = self._scan_keys(pattern, count=scan_count)
        if not keys:
            print(f"Nenhuma chave encontrada para pattern [{pattern}]")
            return {}, {}

        with self.__redis_conn.pipeline() as p:
            for k in keys:
                p.get(k)
            values = p.execute()

        out: Dict[str, Any] = {}
        errors: Dict[str, str] = {}
        for k, v in zip(keys, values):
            if v is None:
                continue
            try:
                out[k] = json.loads(v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else v)
            except Exception as ex:
                snippet = (v[:120] if isinstance(v, (bytes, bytearray)) else str(v)[:120])
                errors[k] = f"{ex} | raw={snippet!r}"
        return out, errors

    def mget_hashes_by_prefix(self, prefix: str, scan_count: int = 1000) -> Dict[str, Dict[str, Any]]:
        """
        Busca chaves prefixadas (prefix:*) assumindo que os valores são HASHES.
        Faz HGETALL em pipeline e tenta JSON-deserializar cada field.
        """
        pattern = f"{prefix}:*"
        keys = self._scan_keys(pattern, count=scan_count)
        if not keys:
            print(f"Nenhuma chave encontrada para pattern [{pattern}]")
            return {}

        with self.__redis_conn.pipeline() as p:
            for k in keys:
                p.hgetall(k)
            results = p.execute()

        out: Dict[str, Dict[str, Any]] = {}
        for k, h in zip(keys, results):
            parsed = {}
            for fk, fv in h.items():
                field = fk.decode() if isinstance(fk, bytes) else fk
                val = fv.decode() if isinstance(fv, bytes) else fv
                try:
                    parsed[field] = json.loads(val)
                except Exception:
                    parsed[field] = val
            out[k] = parsed
        return out

    def mget_redisjson_by_prefix(self, prefix: str, scan_count: int = 1000, path: str = ".") -> Dict[str, Any]:
        """
        (Opcional) Se você usa RedisJSON (JSON.SET/GET).
        """
        pattern = f"{prefix}:*"
        keys = self._scan_keys(pattern, count=scan_count)
        if not keys:
            print(f"Nenhuma chave encontrada para pattern [{pattern}]")
            return {}

        with self.__redis_conn.pipeline() as p:
            for k in keys:
                p.execute_command("JSON.GET", k, path)
            vals = p.execute()

        out: Dict[str, Any] = {}
        for k, v in zip(keys, vals):
            out[k] = None if v is None else json.loads(v)
        return out

    def fetch_by_prefix_auto(self, prefix: str, scan_count: int = 1000) -> Dict[str, Any]:
        """
        Detecta o tipo da primeira chave encontrada e delega:
        - string  -> mget_json_by_prefix
        - hash    -> mget_hashes_by_prefix
        - ReJSON* -> mget_redisjson_by_prefix
        """
        pattern = f"{prefix}:*"
        keys = self._scan_keys(pattern, count=scan_count)
        if not keys:
            print(f"Nenhuma chave encontrada para pattern [{pattern}]")
            return {}

        first_key = keys[0]
        try:
            t = self.__redis_conn.type(first_key)
            t = t.decode() if isinstance(t, bytes) else str(t)
        except Exception as ex:
            print(f"Falha ao detectar tipo de chave [{first_key}]: {ex}")
            t = "string"  # fallback comum

        t_lower = t.lower()
        if t_lower == "hash":
            return self.mget_hashes_by_prefix(prefix, scan_count)
        elif t_lower in ("string", "none"):
            data, _ = self.mget_json_by_prefix(prefix, scan_count)
            return data
        elif "rejson" in t_lower:  # ex: 'ReJSON-RL'
            return self.mget_redisjson_by_prefix(prefix, scan_count)
        else:
            print(f"Tipo de chave não suportado ({t}) em [{first_key}] — tentando como STRING JSON.")
            data, _ = self.mget_json_by_prefix(prefix, scan_count)
            return data
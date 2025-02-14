import json
import requests

from caddy_api.settings import CONFIG_FILE_PATH

# Configurações
CADDY_API_URL = "http://localhost:2019"


# Função para carregar a configuração do arquivo JSON
def load_config():
    with open(CONFIG_FILE_PATH, "r") as file:
        return json.load(file)


# Função para salvar a configuração no arquivo JSON
def save_config(config):
    with open(CONFIG_FILE_PATH, "w") as file:
        json.dump(config, file, indent=4)


# Função para buscar a configuração do Caddy atualizada
def get_caddy_config():
    response = requests.get(CADDY_API_URL + "/config")
    response.raise_for_status()
    return response.json()


# Função para aplicar configuração no Caddy
def update_caddy_config(config):
    response = requests.post(CADDY_API_URL + "/load", json=config)
    response.raise_for_status()
    return response.status_code

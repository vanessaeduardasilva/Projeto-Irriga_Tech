import network
import time
from machine import Pin, ADC
import dht
from umqtt.simple import MQTTClient
import ujson

# Configurações de rede Wi-Fi
SSID = "iPhone"  # Substitua pelo seu SSID
PASSWORD = "1234568x"  # Substitua pela senha da sua rede Wi-Fi

# Configurações do broker HiveMQ
BROKER = "broker.hivemq.com"  # Endereço do seu broker HiveMQ
PORTA = 1883  # Porta segura (com TLS)
CLIENTE_ID = "esp32_irrigacao"  # ID único do cliente MQTT
TOPICO_UMIDADE = "irrigacao/umidade"  # Tópico para publicar a umidade do solo
TOPICO_TEMPERATURA = "irrigacao/temperatura"  # Tópico para publicar a temperatura

# Credenciais do broker HiveMQ
USUARIO = ""  # Substitua pelo seu usuário (se necessário)
SENHA = ""  # Substitua pela sua senha (se necessário)

# Configuração do sensor de umidade de solo
PINO_SENSOR = 36  # Pino ADC para o sensor de umidade

# Configuração do módulo de relé
pin_rele = 26  # Pino para o controle do relé
rele = Pin(pin_rele, Pin.OUT)

# Definição do número de amostras
NUMERO_AMOSTRAS = 5

# Função para conectar ao Wi-Fi
def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)
    while not wifi.isconnected():
        print("Conectando ao Wi-Fi...")
        time.sleep(1)
    print("Conectado ao Wi-Fi")

# Função para conectar ao broker MQTT HiveMQ
def conectar_mqtt():
    cliente = MQTTClient(CLIENTE_ID, BROKER, PORTA, USUARIO, SENHA)  # ssl=True para conexão segura
    cliente.connect()
    print("Conectado ao broker HiveMQ")
    return cliente

# Função para ler a umidade do solo
def ler_umidade_solo():
    pino_sensor = Pin(PINO_SENSOR, Pin.IN)
    adc = ADC(pino_sensor)
    adc.atten(ADC.ATTN_11DB)

    somatoria = 0

    for i in range(1, NUMERO_AMOSTRAS + 1):
        leitura_sensor = adc.read()
        somatoria += leitura_sensor
        tensao = leitura_sensor * (3.3 / 4095)  # Ajuste para resolução do ADC do ESP32 (0-4095)
        print("Amostra {} | Leitura: {} | Tensão: {:.2f}".format(i, leitura_sensor, tensao))
        time.sleep_ms(1000)

    media = somatoria / NUMERO_AMOSTRAS
    return int(media)

# Função para acionar o relé
def acionar_rele():
    rele.value(1)  # Liga o relé
    print("Irrigação ligada")
    time.sleep(5)  # Tempo de irrigação por 5 segundos
    rele.value(0)  # Desliga o relé
    print("Irrigação desligada")

# Conectar ao Wi-Fi e ao MQTT antes de iniciar o loop principal
conectar_wifi()
cliente_mqtt = conectar_mqtt()

# Loop principal
while True:
    umidade = ler_umidade_solo()
    print("Umidade do solo:", umidade)
    

    # Medir a temperatura e umidade do ambiente (se for usar o sensor DHT11)
    # sensor.measure()  # Descomente esta linha se for usar o sensor DHT11
    # temp = sensor.temperature()
    # print('Temperatura: %3.1f C' % temp)

    # Publicar a umidade do solo no MQTT
    dados = {
        "umidade": umidade,
        # "temp": temp,  # Se estiver usando o DHT11
        # "humidity": humidity  # Se estiver usando o DHT11
    }
    cliente_mqtt.publish(TOPICO_UMIDADE, ujson.dumps(dados))
    print(f"Publicado no MQTT: {TOPICO_UMIDADE} -> {umidade}")

    # Publicar a temperatura (se for usar o DHT11)
    # mensagem_temperatura = ujson.dumps({"temperatura": temp})
    # cliente_mqtt.publish(TOPICO_TEMPERATURA, mensagem_temperatura)
    # print(f"Publicado no MQTT: {TOPICO_TEMPERATURA} -> {mensagem_temperatura}")

    # Acionar o relé se a umidade do solo estiver abaixo de um valor desejado
    if umidade > 3500:  # Defina o limite de umidade para acionar a irrigação
        acionar_rele()

    time.sleep(10)  # Aguarda 10 segundos antes de verificar novamente a umidade

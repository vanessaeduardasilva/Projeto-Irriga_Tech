// Definindo o broker e o tópico MQTT
const brokerUrl = 'ws://broker.hivemq.com:8000/mqtt';  // Usando WebSocket não seguro
const topicUmidade = 'irrigacao/umidade';  // Tópico MQTT para umidade

// Criação do cliente MQTT
const client = mqtt.connect(brokerUrl);

// Elemento HTML para exibir os dados
const humidityElement = document.getElementById('humidity');

// Função para atualizar a leitura de umidade na página
function updateData(umidade) {
  humidityElement.innerText = umidade ? `${umidade}%` : 'Erro ao ler umidade';
}

// Conectar ao broker MQTT
client.on('connect', () => {
  console.log('Conectado ao broker MQTT');
  client.subscribe(topicUmidade, (err) => {
    if (!err) {
      console.log(`Subscrito no tópico: ${topicUmidade}`);
    } else {
      console.log(`Erro ao se inscrever no tópico ${topicUmidade}:`, err);
    }
  });
});

// Receber as mensagens do MQTT
client.on('message', (topic, message) => {
  console.log(`Mensagem recebida no tópico ${topic}: ${message.toString()}`);
  
  // Verificar se a mensagem é do tópico da umidade
  if (topic === topicUmidade) {
    const umidade = JSON.parse(message.toString()).umidade;
    updateData(umidade);  // Atualizar a umidade na página
  }
});

// Lidar com erros de conexão
client.on('error', (err) => {
  console.log('Erro de conexão MQTT:', err);
});

// Função para atualizar o gráfico de pizza com base na umidade (0 a 100)
function updatePieChart(umidade) {
  const pieChart = document.querySelector('.pie-chart');
  const pieCenter = document.querySelector('.pie-center');
  
  // Define o ângulo do preenchimento baseado na umidade
  const degree = (umidade / 100) * 360;
  
  // Atualiza o fundo do gráfico de pizza com o preenchimento
  pieChart.style.background = `conic-gradient(#4CAF50 ${degree}deg, #d3d3d3 ${degree}deg)`;
  
  // Exibe o valor da umidade no centro do gráfico
  pieCenter.textContent = `${umidade}%`;
}

// Exemplo de uso: Atualizando o gráfico para 75% de umidade
updatePieChart(75);

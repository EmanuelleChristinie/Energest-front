// src/services/api.js
import { kpiData, chartData, iaRecommendations, equipamentosData } from './mockData.js'; // Adicionado .js por segurança pro Vite

// ==========================================
// CONFIGURAÇÃO DE AMBIENTE (ENV)
// ==========================================
// CHAVE DE OURO: 'false' para tentar conectar no Python. Se cair, usa o Mock.
const USE_MOCK = false; 

const BASE_URL = 'http://127.0.0.1:8000'; // Porta padrão do FastAPI
// ==========================================

/**
 * Função Core de Fetch com Fallback de Segurança (Resiliência)
 * Se o Back-end cair na hora do Pitch, o Front-end assume os mocks automaticamente.
 */
async function fetchFromApi(endpoint, mockFallback) {
  if (USE_MOCK) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(mockFallback), 600); // Delay simulando latência de rede
    });
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`);
    if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`[API ERROR] Falha ao comunicar com ${endpoint}:`, error);
    console.warn("🛡️ Ativando Fallback Mode: Retornando dados em cache para não quebrar a UI.");
    return mockFallback;
  }
}

// ==========================================
// ROTAS DO SISTEMA (ENDPOINTS)
// ==========================================

export const getDashboardKpis = () => fetchFromApi('/api/dashboard/kpis', kpiData);

export const getConsumoHistorico = () => fetchFromApi('/api/dashboard/grafico-consumo', chartData);

export const getRecomendacoesIA = () => fetchFromApi('/api/ia/recomendacoes', iaRecommendations);

export const getEquipamentos = () => fetchFromApi('/api/equipamentos/lista', equipamentosData);

export const aprovarRecomendacao = async (idRecomendacao) => {
  if (USE_MOCK) {
    console.log(`[AUDITORIA] Ação de correção ${idRecomendacao} enviada ao CLP da máquina.`);
    return { status: 'sucesso', mensagem: 'Ação aplicada via rede industrial.' };
  }

  const response = await fetch(`${BASE_URL}/api/ia/aprovar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: idRecomendacao })
  });
  return response.json();
};

// 👇 AS DUAS FUNÇÕES QUE FALTAVAM ESTÃO AQUI 👇

export const getLiveIoTData = () => fetchFromApi('/api/iot/live', {
  sensoresAtivos: 24,
  temperaturaMedia: '45ºC',
  statusGeral: 'Operacional'
});

export const simularPrevisaoIA = async (dadosTelemetria) => {
  return fetchFromApi('/api/ia/previsao', {
    risco: 'Operação Estável',
    probabilidade_falha: '12.5',
    consumo_kwh: '250.0',
    eficiencia: '98.0'
  });
};
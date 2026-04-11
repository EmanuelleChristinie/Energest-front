import os
import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ==========================================
# CONFIGURAÇÕES DE CAMINHO (O segredo para o Pytest passar)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# O model.pkl está um nível acima da pasta /app (conforme seu print)
model_path = os.path.join(BASE_DIR, "..", "model.pkl")

# Carregamos o modelo APENAS UMA VEZ usando o caminho dinâmico
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    print(f"⚠️ Alerta: Modelo não encontrado em {model_path}")
    model = None

# ==========================================
# CONFIGURAÇÃO DO APP
# ==========================================
app = FastAPI(title="Energy Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class EnergyData(BaseModel):
    temperature: float
    load_percentage: float
    operating_hours: float
    maintenance_status: int
    machine_age_years: float

# ==========================================
# ROTAS DA API
# ==========================================

@app.get("/")
async def root():
    return {"message": "EnerGest API is running"}

@app.get("/api/equipamentos")
async def get_equipamentos():
    try:
        # Busca o CSV dentro de app/models/energy_data.csv
        csv_path = os.path.join(BASE_DIR, "models", "energy_data.csv")
        
        if not os.path.exists(csv_path):
            return JSONResponse(
                status_code=404, 
                content={"erro": f"Arquivo não encontrado em: {csv_path}"}
            )

        df = pd.read_csv(csv_path)
        df_recent = df.tail(20).copy()
        
        df_recent['id'] = ['MAQ-' + str(i).zfill(3) for i in range(1, len(df_recent) + 1)]
        df_recent['nome'] = [f'Equipamento Industrial {i}' for i in range(1, len(df_recent) + 1)]
        df_recent['status'] = df_recent['maintenance_status'].apply(
            lambda x: 'Operacional' if x == 1 else 'Atenção'
        )
        
        return JSONResponse(content=df_recent.to_dict(orient="records"))
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})

@app.post("/predict")
async def predict(data: EnergyData):
    if model is None:
        return JSONResponse(status_code=503, content={"erro": "Modelo de IA não carregado"})
    
    input_df = pd.DataFrame([data.model_dump()])
    prediction = model.predict(input_df)
    return {"previsao": round(float(prediction[0]), 2)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
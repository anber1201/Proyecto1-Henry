
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pandas as pd
from fastapi import FastAPI
from scipy.sparse import csr_matrix
import pickle
from funciones import get_recommendation, get_playtime_by_genre , get_user_by_genre, get_users_recommend, sentiment_analysis, get_worst_developer

  # Asegúrate de ajustar la ruta de importación según tu estructura de directorios

app = FastAPI()

@app.get("/PlayTimeGenre/{genero}")
def PlayTimeGenre(genero: str):
    result = get_playtime_by_genre(genero)
    return result


app = FastAPI()



@app.get("/")
def index():
    return {"disculpa,escribiste /docs al final?"}



@app.get("/PlayTimeGenre/{genero}")
def PlayTimeGenre(genero: str):
    result1 = get_playtime_by_genre(genero)
    return result1



@app.get("/UserForGenre/{genero}")
async def UserForGenre(genero: str):
    result2 = get_user_by_genre(genero)
    return result2



@app.get("/UsersRecommend/{anio}")
async def UsersRecommend(año: int):
    result3 = get_users_recommend(año)
    return result3


@app.get("/UsersWorstDeveloper/{anio}")
async def worst_developer(año: int):
    result4 = get_worst_developer(año)
    return result4


@app.get("/sentiment_analysis/{developer}")
async def sentimento_analysis(developer: str):
    result5 = sentiment_analysis(developer)
    return result5


@app.get("/recommendacion_juego/{item_id}")
async def recomendacion_juego(item_id: int):
    similar_items = get_recommendation(item_id)
    return similar_items


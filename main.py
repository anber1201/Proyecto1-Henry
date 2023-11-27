
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import pandas as pd
from fastapi import FastAPI
from scipy.sparse import csr_matrix
import pickle

app = FastAPI()



@app.get("/")
def index():
    return {"disculpa,escribiste /docs al final?"}



@app.get("/PlayTimeGenre/{genero}")
def PlayTimeGenre(genero: str):
    df_final = pd.read_parquet('PIMLops-STEAM/DF_final.parquet')
    df_filtered = df_final[df_final['genres'] == genero]
    if df_filtered.empty:
        return {"message": f"No data found for genre: {genero}"}
    playtime_sum = df_filtered.groupby('release_date')['playtime_forever'].sum() 
    year_max_playtime = playtime_sum.idxmax()
    max_playtime = playtime_sum.max()
    del df_final, df_filtered, playtime_sum
    return {"Año de lanzamiento con más horas jugadas para el género: " + genero : str(year_max_playtime), "Horas jugadas": str(max_playtime)}

@app.get("/UserForGenre/{genero}")
async def UserForGenre(genero: str):
    try:
        df_final = pd.read_parquet('PIMLops-STEAM/DF_final.parquet')
        df_filtered = df_final[df_final['genres'] == genero]
        playtime_sum = df_filtered.groupby(['user_id', 'year'])['playtime_forever'].sum() 
        user_max_playtime = playtime_sum.groupby('user_id').sum().idxmax()
        playtime_by_year = playtime_sum.loc[user_max_playtime].to_dict()
        del df_final, df_filtered, playtime_sum
        return {"Usuario con más horas jugadas para el género: " + genero : user_max_playtime, "Horas jugadas": playtime_by_year}
    except Exception as e:
        return {"error": str(e)}


@app.get("/UsersRecommend/{anio}")
async def UsersRecommend(año: int):
    ReviewsxGames = pd.read_parquet('PIMLops-STEAM/df_reviewsG.parquet')
    df_filtered = ReviewsxGames[(ReviewsxGames['year'] == año) & (ReviewsxGames['recommend'] == True) & (ReviewsxGames['sentiment_analysis'] >= 1)]
    recommend_count = df_filtered['item_name'].value_counts()
    top_3_games = recommend_count.nlargest(3).index.tolist()
    del ReviewsxGames, df_filtered, recommend_count
    return [{"Puesto 1" : top_3_games[0]}, {"Puesto 2" : top_3_games[1]}, {"Puesto 3" : top_3_games[2]}]

@app.get("/UsersWorstDeveloper/{anio}")
async def UsersWorstDeveloper(año: int):
    ReviewsxGames = pd.read_parquet('PIMLops-STEAM/df_reviewsG.parquet')
    df_filtered = ReviewsxGames[(ReviewsxGames['year'] == año) & (ReviewsxGames['recommend'] == False) & (ReviewsxGames['sentiment_analysis'] == 0)]
    negative_reviews_count = df_filtered['developer'].value_counts()
    top_3_bad_developers = negative_reviews_count.nlargest(3).index.tolist()
    del ReviewsxGames, df_filtered, negative_reviews_count
    return [{"Puesto 1" : top_3_bad_developers[0]}, {"Puesto 2" : top_3_bad_developers[1]}, {"Puesto 3" : top_3_bad_developers[2]}]

@app.get("/sentiment_analysis/{developer}")
async def sentiment_analysis(developer: str):
    ReviewsxGames = pd.read_parquet('PIMLops-STEAM/df_reviewsG.parquet')
    df_filtered = ReviewsxGames[ReviewsxGames['developer'] == developer]
    sentiment_count = df_filtered['sentiment_analysis'].value_counts().to_dict()
    result = {developer : ['Negative = ' + str(sentiment_count.get(0, 0)), 'Neutral = ' + str(sentiment_count.get(1, 0)), 'Positive = ' + str(sentiment_count.get(2, 0))]}
    del ReviewsxGames, df_filtered, sentiment_count
    return result




@app.get("/recommendacion_juego/{item_id}")
async def recomendacion_juego(item_id: int):
    df_final = pd.read_parquet('PIMLops-STEAM/DF_final.parquet')
    df_final = df_final[['item_id', 'user_id', 'recommend']]  # keep only necessary columns
    sparse_matrix = csr_matrix(pd.crosstab(df_final['item_id'], df_final['user_id'], values=df_final['recommend'], aggfunc='sum').fillna(0))
    similitud = cosine_similarity(sparse_matrix)
    indices_similares = {item_id: similitud[item_index].argsort()[-6:-1][::-1] for item_index, item_id in enumerate(df_final['item_id'].unique().tolist())}
    with open('indices_similares.pkl', 'wb') as f:
        pickle.dump(indices_similares, f)
    with open('indices_similares.pkl', 'rb') as f:
        indices_similares = pickle.load(f)
    similar_items = [df_final['item_id'].unique().tolist()[i] for i in indices_similares[item_id]]
    del df_final, sparse_matrix, similitud, indices_similares
    return similar_items
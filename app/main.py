# app/main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd

from app.db import engine
from app.llm_explainer import explain_with_template

app = FastAPI(title="E-commerce Product Recommender API")

# Serve static files under /static and serve index.html at root
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return FileResponse(os.path.join("app", "static", "index.html"))

# --- Load tables helper (robust) ---
def load_tables():
    # Return empty DataFrames if tables do not exist yet
    try:
        users = pd.read_sql("SELECT * FROM users", engine)
    except Exception:
        users = pd.DataFrame(columns=["id", "name", "email"])

    try:
        products = pd.read_sql("SELECT * FROM products", engine)
    except Exception:
        products = pd.DataFrame(columns=["id", "name", "category", "price"])

    try:
        interactions = pd.read_sql("SELECT * FROM user_interactions", engine)
    except Exception:
        interactions = pd.DataFrame(columns=["id", "user_id", "product_id", "event_type", "timestamp"])

    return users, products, interactions

@app.on_event("startup")
def startup_load():
    global users, products, interactions
    users, products, interactions = load_tables()
    print("✅ Data loaded from database (or empty tables if not present)")

# --- Simple Recommendation Logic ---
def recommend_products(user_id: int, top_n: int = 3):
    # If products empty, return empty DataFrame
    if products.empty:
        return pd.DataFrame(columns=["id", "name", "category", "price"])

    user_interactions = interactions[interactions["user_id"] == user_id]
    if user_interactions.empty:
        # safe sample: if fewer rows than top_n, return all
        return products.sample(n=min(top_n, len(products)), replace=False).reset_index(drop=True)

    merged = user_interactions.merge(products, left_on="product_id", right_on="id")
    if merged.empty or "category" not in merged:
        return products.sample(n=min(top_n, len(products)), replace=False).reset_index(drop=True)

    top_category = merged["category"].mode()[0]
    recs = products[products["category"] == top_category]
    if recs.empty:
        return products.sample(n=min(top_n, len(products)), replace=False).reset_index(drop=True)

    recs = recs.sample(n=min(top_n, len(recs)), replace=False).reset_index(drop=True)
    return recs

# --- API Endpoint ---
@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int, top_n: int = 3):
    global users, products, interactions
    recs = recommend_products(user_id, top_n)
    result = []

    # safe user lookup
    user_row = users[users["id"] == user_id]
    user_name = user_row["name"].values[0] if not user_row.empty else f"User {user_id}"

    for _, row in recs.iterrows():
        user_cat_count = 0
        try:
            user_cat_count = interactions.merge(products, left_on="product_id", right_on="id") \
                                         .query("user_id == @user_id and category == @row['category']") \
                                         .shape[0]
        except Exception:
            user_cat_count = 0

        explanation = explain_with_template(user_name, row["name"], row.get("category", ""), user_cat_count)
        result.append({
            "product": row["name"],
            "category": row.get("category", ""),
            "price": float(row["price"]) if "price" in row and pd.notna(row["price"]) else None,
            "explanation": explanation
        })

    return {"user": user_name, "recommendations": result}

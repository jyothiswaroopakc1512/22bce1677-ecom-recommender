# app/llm_explainer.py
def explain_with_template(user_name, product_name, category, user_cat_count):
    if user_cat_count > 0:
        return f"We recommended '{product_name}' to {user_name} because they showed interest in {category} items {user_cat_count} time(s)."
    else:
        return f"'{product_name}' is a new {category} item we think {user_name} might like based on similar user behavior."

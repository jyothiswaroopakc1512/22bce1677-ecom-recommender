# app/sample_data.py
from sqlalchemy.orm import Session
from datetime import datetime
from app.db import engine
from app.models import Base, User, Product, UserInteraction

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        # Users (idempotent insert by email)
        seed_users = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
        for u in seed_users:
            exists = session.query(User).filter_by(email=u["email"]).first()
            if not exists:
                session.add(User(name=u["name"], email=u["email"]))
        session.commit()

        # Products (simple insert if table empty)
        prod_count = session.query(Product).count()
        if prod_count == 0:
            products = [
                Product(name="Blue T-Shirt", category="Clothing", price=19.99),
                Product(name="Running Shoes", category="Footwear", price=59.99),
                Product(name="Coffee Mug", category="Home", price=9.99),
                Product(name="Black Jeans", category="Clothing", price=39.99)
            ]
            session.add_all(products)
            session.commit()

        # Interactions (only add if table empty)
        inter_count = session.query(UserInteraction).count()
        if inter_count == 0:
            interactions = [
                UserInteraction(user_id=1, product_id=1, event_type="view", timestamp=datetime.now()),
                UserInteraction(user_id=1, product_id=4, event_type="purchase", timestamp=datetime.now()),
                UserInteraction(user_id=2, product_id=3, event_type="view", timestamp=datetime.now())
            ]
            session.add_all(interactions)
            session.commit()

        print("✅ Sample data inserted (idempotent)")

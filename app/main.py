# C:\Users\ianes\Desktop\BigData-2025.1\app\main.py
from flask import Flask
from app.config import Config
from app.db.mysql_db import db
from app.swagger.swagger_setup import configure_swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Configura Swagger (Flask-RESTX)
    api = configure_swagger(app)

    # Importa e registra os namespaces
    from app.controllers.user_controller import user_ns
    from app.controllers.product_controller import product_ns
    from app.controllers.address_controller import address_ns
    from app.controllers.credit_card_controller import credit_card_ns

    # As rotas serão /users, /products, /address, /credit_card, etc.
    api.add_namespace(user_ns, path="/users")
    api.add_namespace(product_ns, path="/products")
    api.add_namespace(address_ns, path="/address")
    api.add_namespace(credit_card_ns, path="/credit_card")

    return app


if __name__ == "__main__":
    flask_app = create_app()
    with flask_app.app_context():
        db.create_all()  # Cria as tabelas no MySQL (caso não existam)
    print("Rotas registradas:")
    for rule in flask_app.url_map.iter_rules():
        print(rule, rule.endpoint)

    flask_app.run(debug=True)

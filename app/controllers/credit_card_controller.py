# app/controllers/credit_card_controller.py
from flask_restx import Namespace, Resource, fields
from flask import request
from datetime import datetime
from app.db.mysql_db import db
from app.models.credit_card_model import CreditCard

credit_card_ns = Namespace(
    "credit_card",
    description="Operações relacionadas a cartões de crédito do usuário"
)

# Definindo o modelo de cartão para documentação (Swagger)
credit_card_model = credit_card_ns.model("CreditCardModel", {
    "numero": fields.String(required=True, description="Número do cartão de crédito"),
    "dtExpiracao": fields.String(required=True, description="Data de expiração em formato (dd/mm/yyyy)"),
    "cvv": fields.String(required=True, description="Código de segurança do cartão"),
    "saldo": fields.Float(required=True, description="Saldo inicial disponível no cartão")
})

@credit_card_ns.route("/<int:user_id>")
class CreditCardList(Resource):
    @credit_card_ns.expect(credit_card_model, validate=True)
    @credit_card_ns.response(201, "Cartão criado com sucesso")
    @credit_card_ns.response(400, "Erro ao criar cartão de crédito")
    def post(self, user_id):
        """
        Cria um novo cartão de crédito para o usuário informado.
        Exemplo de body (JSON):
        {
          "numero": "4000123456789010",
          "dtExpiracao": "2027-04-11T03:02:45.999Z",
          "cvv": "123",
          "saldo": 5000
        }
        """
        data = credit_card_ns.payload
        try:
            dt_exp = data.get("dtExpiracao")
            if dt_exp:
                # Tenta converter a string "dd/mm/yyyy" para um objeto datetime
                try:
                    dt_exp = datetime.strptime(dt_exp, "%d/%m/%Y")
                except ValueError:
                    return {"error": "Formato de data inválido. Use dd/mm/yyyy."}, 400
            else:
                return {"error": "Data de expiração é obrigatória."}, 400
            new_card = CreditCard(
                user_id=user_id,
                numero=data["numero"],
                dtExpiracao=dt_exp,
                cvv=data["cvv"],
                saldo=data["saldo"]
            )

            db.session.add(new_card)
            db.session.commit()

            return {
                "message": "Cartão criado com sucesso",
                "card": new_card.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

@credit_card_ns.route("/<int:user_id>/<int:card_id>")
class CreditCardResource(Resource):
    @credit_card_ns.response(200, "Sucesso")
    @credit_card_ns.response(404, "Cartão não encontrado")
    def get(self, user_id, card_id):
        """Retorna um cartão pelo ID e usuário."""
        card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return {"error": "Cartão não encontrado"}, 404
        return {"card": card.to_dict()}, 200

    @credit_card_ns.response(204, "Cartão deletado com sucesso")
    @credit_card_ns.response(404, "Cartão não encontrado")
    def delete(self, user_id, card_id):
        """Deleta um cartão específico de um usuário."""
        card = CreditCard.query.filter_by(id=card_id, user_id=user_id).first()
        if not card:
            return {"error": "Cartão não encontrado"}, 404
        db.session.delete(card)
        db.session.commit()
        return "", 204
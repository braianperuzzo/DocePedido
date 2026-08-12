"""Modelo de dados de cliente da Doce Pedido."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from aplicacao import banco


class Cliente(UserMixin, banco.Model):
    """Representa uma conta de cliente autenticável."""
    id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(120), nullable=False)
    email = banco.Column(banco.String(255), unique=True, nullable=False, index=True)
    cpf = banco.Column(banco.String(11), unique=True, nullable=True, index=True)
    senha_hash = banco.Column(banco.String(255), nullable=False)
    telefone = banco.Column(banco.String(20))
    ativo = banco.Column(banco.Boolean, nullable=False, default=True)
    data_cadastro = banco.Column(
        banco.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    pedidos = banco.relationship("Pedido", back_populates="cliente", lazy=True)

    @property
    def is_active(self):
        return self.ativo

    def definir_senha(self, senha):
        """Gera e armazena o hash seguro da senha."""
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        """Compara uma senha ao hash armazenado."""
        return check_password_hash(self.senha_hash, senha)

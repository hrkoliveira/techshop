"""
Testes unitários para a classe ShoppingCart.

Convenções (docs/DIRETRIZES_IA.md):
- Padrão AAA obrigatório com comentários explícitos.
- Tipagem completa (mypy).
- pytest puro, sem unittest.
"""

import pytest
from src.cart import ShoppingCart
from src.models import Product


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cart() -> ShoppingCart:
    """Retorna um carrinho vazio para cada teste."""
    return ShoppingCart()


@pytest.fixture
def product_a() -> Product:
    """Produto padrão A — R$ 100,00."""
    return Product(id=1, name="Teclado", price=100.00)


@pytest.fixture
def product_b() -> Product:
    """Produto padrão B — R$ 200,00."""
    return Product(id=2, name="Mouse", price=200.00)


@pytest.fixture
def product_c() -> Product:
    """Produto padrão C — preço decimal — R$ 0,10."""
    return Product(id=3, name="Cabo USB", price=0.10)


# ---------------------------------------------------------------------------
# Caminhos felizes
# ---------------------------------------------------------------------------


def test_add_item_carrinho_vazio_item_adicionado(
    cart: ShoppingCart, product_a: Product
) -> None:
    """Adicionar um item a um carrinho vazio deve registrar exatamente 1 item."""
    # Arrange
    quantity = 1

    # Act
    cart.add_item(product_a, quantity)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].product.id == product_a.id
    assert cart.items[0].quantity == quantity


def test_add_item_multiplos_distintos_todos_registrados(
    cart: ShoppingCart, product_a: Product, product_b: Product
) -> None:
    """Adicionar produtos distintos deve criar entradas separadas no carrinho."""
    # Arrange — dois produtos diferentes

    # Act
    cart.add_item(product_a, 1)
    cart.add_item(product_b, 2)

    # Assert
    assert len(cart.items) == 2


def test_add_item_existente_incrementa_quantidade(
    cart: ShoppingCart, product_a: Product
) -> None:
    """Adicionar um produto já presente deve somar a quantidade, não duplicar."""
    # Arrange
    cart.add_item(product_a, 1)

    # Act
    cart.add_item(product_a, 3)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 4


def test_remove_item_existente_removido(
    cart: ShoppingCart, product_a: Product, product_b: Product
) -> None:
    """Remover um produto existente deve deixar apenas os demais no carrinho."""
    # Arrange
    cart.add_item(product_a, 1)
    cart.add_item(product_b, 1)

    # Act
    cart.remove_item(product_a.id)

    # Assert
    assert len(cart.items) == 1
    assert cart.items[0].product.id == product_b.id


def test_calculate_total_sem_desconto_retorna_soma_correta(
    cart: ShoppingCart, product_a: Product, product_b: Product
) -> None:
    """Total sem desconto deve ser a soma de preço × quantidade de cada item."""
    # Arrange
    cart.add_item(product_a, 2)  # 2 × 100 = 200
    cart.add_item(product_b, 1)  # 1 × 200 = 200

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == pytest.approx(400.00)


def test_calculate_total_with_discount_10_percent_aplicado(
    cart: ShoppingCart, product_a: Product
) -> None:
    """Compras acima de R$ 500 devem receber 10% de desconto."""
    # Arrange
    cart.add_item(product_a, 6)  # 600.00 > 500 → 10% off → 540.00

    # Act
    total = cart.calculate_total_with_discount()

    # Assert
    assert total == pytest.approx(540.00)


def test_calculate_total_with_discount_20_percent_aplicado(
    cart: ShoppingCart, product_a: Product
) -> None:
    """Compras acima de R$ 1000 devem receber 20% de desconto."""
    # Arrange
    cart.add_item(product_a, 11)  # 1100.00 > 1000 → 20% off → 880.00

    # Act
    total = cart.calculate_total_with_discount()

    # Assert
    assert total == pytest.approx(880.00)


# ---------------------------------------------------------------------------
# Casos de borda
# ---------------------------------------------------------------------------


def test_calculate_total_carrinho_vazio_retorna_zero(cart: ShoppingCart) -> None:
    """Carrinho sem itens deve retornar total 0.0 sem lançar exceção."""
    # Arrange — carrinho já vazio pela fixture

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == pytest.approx(0.0)


def test_calculate_total_with_discount_carrinho_vazio_retorna_zero(
    cart: ShoppingCart,
) -> None:
    """Desconto sobre carrinho vazio deve retornar 0.0 sem lançar exceção."""
    # Arrange — carrinho já vazio pela fixture

    # Act
    total = cart.calculate_total_with_discount()

    # Assert
    assert total == pytest.approx(0.0)


def test_remove_item_inexistente_nao_lanca_excecao(
    cart: ShoppingCart, product_a: Product
) -> None:
    """Remover ID que não existe não deve lançar exceção nem alterar o carrinho."""
    # Arrange
    cart.add_item(product_a, 1)

    # Act
    cart.remove_item(product_id=999)

    # Assert
    assert len(cart.items) == 1


def test_calculate_total_preco_decimal_precisao_correta(
    cart: ShoppingCart, product_c: Product
) -> None:
    """Preços com múltiplas casas decimais devem ser somados com precisão via approx."""
    # Arrange
    cart.add_item(product_c, 3)  # 3 × 0.10 = 0.30 (suscetível a erro de float)

    # Act
    total = cart.calculate_total()

    # Assert
    assert total == pytest.approx(0.30)


@pytest.mark.parametrize(
    "total_price, quantity, expected",
    [
        (500.00, 1, 500.00),   # exatamente 500 → sem desconto
        (500.01, 1, 450.009),  # 1 centavo acima → 10% off
        (1000.00, 1, 900.00),  # exatamente 1000 → 10% off
        (1000.01, 1, 800.008), # 1 centavo acima de 1000 → 20% off
    ],
)
def test_calculate_total_with_discount_limiares(
    cart: ShoppingCart, total_price: float, quantity: int, expected: float
) -> None:
    """Valida o comportamento exato nos limiares de desconto (boundary values)."""
    # Arrange
    product = Product(id=99, name="Produto Limiar", price=total_price)
    cart.add_item(product, quantity)

    # Act
    total = cart.calculate_total_with_discount()

    # Assert
    assert total == pytest.approx(expected)

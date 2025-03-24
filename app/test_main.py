import datetime
from collections.abc import Callable

import pytest

from app.main import outdated_products


@pytest.fixture
def freeze_today(
    monkeypatch: pytest.MonkeyPatch
) -> Callable[[datetime.date], None]:
    def _set_date(mock_date: datetime.date) -> None:
        class FrozenDate(datetime.date):
            @classmethod
            def today(cls) -> datetime.date:
                return mock_date

        monkeypatch.setattr(datetime, "date", FrozenDate)

    return _set_date


class TestOutdatedProducts:
    def test_returns_product_if_expired_before_today(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "milk",
                "expiration_date": datetime.date(2022, 2, 1),
                "price": 100,
            }
        ]

        result = outdated_products(products)

        assert result == ["milk"]

    def test_excludes_product_if_expiration_is_today(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "cheese",
                "expiration_date": datetime.date(2022, 2, 2),
                "price": 250,
            }
        ]

        result = outdated_products(products)

        assert result == []

    def test_excludes_product_if_expiration_after_today(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "juice",
                "expiration_date": datetime.date(2022, 2, 3),
                "price": 70,
            }
        ]

        result = outdated_products(products)

        assert result == []

    def test_returns_only_expired_products_from_mixed_list(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "eggs",
                "expiration_date": datetime.date(2022, 2, 1),
                "price": 60,
            },
            {
                "name": "bread",
                "expiration_date": datetime.date(2022, 2, 2),
                "price": 20,
            },
            {
                "name": "fish",
                "expiration_date": datetime.date(2022, 2, 3),
                "price": 150,
            },
        ]

        result = outdated_products(products)

        assert result == ["eggs"]

    def test_returns_all_products_if_all_are_expired(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "yogurt",
                "expiration_date": datetime.date(2022, 1, 30),
                "price": 80,
            },
            {
                "name": "kefir",
                "expiration_date": datetime.date(2022, 1, 25),
                "price": 75,
            },
        ]

        result = outdated_products(products)

        assert result == ["yogurt", "kefir"]

    def test_returns_empty_list_if_all_products_are_fresh(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "butter",
                "expiration_date": datetime.date(2022, 2, 3),
                "price": 120,
            },
            {
                "name": "jam",
                "expiration_date": datetime.date(2022, 2, 5),
                "price": 90,
            },
        ]

        result = outdated_products(products)

        assert result == []

    def test_returns_empty_list_if_product_list_is_empty(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        result = outdated_products([])

        assert result == []

    def test_raises_key_error_if_expiration_key_is_missing(
        self,
        freeze_today: Callable[[datetime.date], None],
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "milk",
                "price": 100,
            }
        ]

        with pytest.raises(KeyError):
            outdated_products(products)

    @pytest.mark.parametrize(
        "invalid_date",
        [
            "2022-01-01",
            None,
            123456
        ],
    )
    def test_raises_type_error_if_expiration_type_is_invalid(
        self,
        freeze_today: Callable[[datetime.date], None],
        invalid_date: object,
    ) -> None:
        freeze_today(datetime.date(2022, 2, 2))

        products = [
            {
                "name": "milk",
                "expiration_date": invalid_date,
                "price": 100,
            }
        ]

        with pytest.raises(TypeError):
            outdated_products(products)

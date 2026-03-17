import pandas as pd

from app import StockService


def test_query_stock_detects_sku_column():
    service = StockService()
    df = pd.DataFrame(
        [
            {"SKU": "ABC-123", "stock": 10},
            {"SKU": "XYZ-999", "stock": 2},
        ]
    )

    result = service.query_stock(df, "abc")

    assert len(result.records) == 1
    assert result.records[0]["stock"] == 10


def test_find_sku_column_with_custom_name():
    service = StockService()
    df = pd.DataFrame([{"codigo_producto": "P-1", "stock": 3}])

    result = service.query_stock(df, "P-1", sku_column="codigo_producto")

    assert len(result.records) == 1

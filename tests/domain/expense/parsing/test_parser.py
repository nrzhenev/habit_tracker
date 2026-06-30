import json
import datetime

import pytest

from app.expense.schema import ExpenseParsed
from app.expense.parsing.parser import parse_expense_response

pytestmark = pytest.mark.unit


def test_should_parse_full_expense():
    result = parse_expense_response(
        '{"occurred_at":"2025-01-01T00:00:00+00:00","amount":500.0,"currency":"RUB",'
        '"category":"food","place":"Perekrestok","items":["bread","milk"]}'
    )
    assert result == ExpenseParsed(
        occurred_at=datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc),
        amount=500.0,
        currency="RUB",
        category="food",
        place="Perekrestok",
        items=["bread", "milk"],
    )


def test_should_parse_minimal_expense():
    result = parse_expense_response('{"currency":"USD","items":["coffee"]}')
    assert result == ExpenseParsed(
        occurred_at=None,
        amount=None,
        currency="USD",
        category=None,
        place=None,
        items=["coffee"],
    )


def test_should_raise_on_missing_currency():
    with pytest.raises(ValueError, match="currency"):
        parse_expense_response('{"items":["coffee"]}')


def test_should_raise_on_missing_items():
    with pytest.raises(ValueError, match="items"):
        parse_expense_response('{"currency":"USD"}')


def test_should_raise_on_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        parse_expense_response("not json")

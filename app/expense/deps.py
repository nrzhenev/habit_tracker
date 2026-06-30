from app.expense.parsing.client import LLMExpenseParser


def get_expense_parser() -> LLMExpenseParser:
    return LLMExpenseParser()

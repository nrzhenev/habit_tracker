from app.core.llm_client import LLMClient
from app.core.structured_llm_task import StructuredLLMTask
from app.expense.parsing.parser import parse_expense_response
from app.expense.parsing.prompts import build_expense_parsing_prompt
from app.expense.schema import ExpenseParsed


class LLMExpenseParser(StructuredLLMTask[ExpenseParsed]):
    def __init__(self, client: LLMClient | None = None):
        super().__init__(build_expense_parsing_prompt, parse_expense_response, client)


expense_parser = LLMExpenseParser()

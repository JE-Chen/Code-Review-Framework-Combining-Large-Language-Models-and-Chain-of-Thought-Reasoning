from Skills.code_review import CODE_REVIEW_SKILL_TEMPLATE
from Skills.code_explainer import CODE_EXPLAINER_TEMPLATE
from codes.run.ask_functions import rag_ask

code_explainer_prompt = CODE_EXPLAINER_TEMPLATE

rag_ask(code_explainer_prompt, "CODE_EXPLAINER_TEMPLATE")

code_review_prompt = CODE_REVIEW_SKILL_TEMPLATE

rag_ask(code_review_prompt, "CODE_EXPLAINER_TEMPLATE")

from Skills.code_review import CODE_REVIEW_SKILL_TEMPLATE
from Skills.code_explainer import CODE_EXPLAINER_TEMPLATE
from codes.run.ask_functions import get_rag_docs

code_explainer_prompt = CODE_EXPLAINER_TEMPLATE

get_rag_docs(code_explainer_prompt, "CODE_EXPLAINER_TEMPLATE")

code_review_prompt = CODE_REVIEW_SKILL_TEMPLATE

get_rag_docs(code_review_prompt, "CODE_EXPLAINER_TEMPLATE")

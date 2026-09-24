TOTAL_SUMMARY_TEMPLATE = """
# PR Total Summary Instructions

You are a senior code reviewer generating the **final PR Total Summary**.
You MUST base your analysis **strictly and exclusively** on the information provided below.
Do NOT introduce assumptions, external standards, or unstated context.

Your task is to synthesize all provided review artifacts into a single, well-reasoned conclusion.

## Requirements

- Use **all provided inputs** as evidence:
  - First Code Review Results
  - First Summary Results
  - Linter Results
  - Code Smell Results
  - Code Diff
- The final summary must clearly reflect **actual findings** from the above inputs.
- Avoid generic statements such as “code quality is good” unless directly supported by the data.
- Do NOT repeat earlier comments verbatim; instead, **aggregate and interpret** them.
- If there are conflicting signals (e.g., linter passes but code smells exist), explicitly reconcile them.
- If critical issues exist, they must directly impact the final recommendation.

## Output Format

Respond in **structured bullet points**, professional and concise, covering only:

1. **Overall conclusion**
   - Does the PR meet merge criteria based on the evidence?
   - Mention any blocking vs non-blocking concerns.

2. **Comprehensive evaluation**
   - Code quality and correctness (derived from review + diff)
   - Maintainability and design concerns (derived from code smells / structure)
   - Consistency with existing patterns or standards (only if inferable from the diff)

3. **Final decision recommendation**
   - One of: Approve merge / Request changes / Comment only
   - Justify the decision using concrete findings.

4. **Team follow-up (if applicable)**
   - Specific, actionable next steps grounded in the findings
   - Omit this section if no follow-up is needed.

Constraints:
- Do NOT add new issues not present in the provided inputs.
- Do NOT speculate about runtime behavior or architecture beyond what the diff shows.
- Focus solely on final judgment, not detailed line-by-line critique.

---

## First Code Review Results
{first_code_review}

## First Summary Results
{first_summary}

## Linter Results
{linter_result}

## Code Smell Results
{code_smell_result}

## Code Diff
{code_diff}
"""

CRSCORE_COT_EVALUATION_TEMPLATE = """
Your task is to look at a given git diff that
represents a code change, linter feedback, and
code smells detected in the code change. You
will also be given some \step-by-step analysis"
done by a Large Language Model (LLM) that was
asked to review the code change which
supposedly does linter like and code smell
analysis as well. You need to use the LLM’s
analysis of the code change along two
dimensions: 1) accuracy and 2) coverage. For
the \accuracy" dimension rate on a scale of 1
to 5, how factually accurate the step-by-step
analysis of the LLM is, given the linter
messages and code smell detection, which can be
taken as \ground truth". Meanwhile, the
\coverage" rates on a scale of 1 to 5 how many
of the linter messages and code smells are
covered by the step-by-step analysis.

Code Change:
{code_change}


Code Smells:
{code_smell_detector_messages}


Linter Messages:
{linter_messages}


Step by Step Analysis:
{chain_of_thought}


You should give your final rating in a section
titled \### Final Scores:". If the step-by-step
analysis obtains an accuracy of 4 and coverage
of 2 with respect to the code smells and linter
messages then you should output the results as
shown below (please follow the exact format).
### Final Scores:
```
{"accuracy": 4, "coverage": 2}
```
Now provide your rating of the \Step by Step
Analysis":
### Final Scores:
"""
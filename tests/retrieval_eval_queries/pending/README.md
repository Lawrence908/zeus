# pending/ — proposed retrieval-eval queries awaiting human review

Themis (the minting job) drops proposed ground-truth queries here as
`pending/<date>.yaml`. Files in this directory are **excluded** from the scored
suite. Promotion into the active suite (`../profile_questions.yaml` or
`../knowledge_questions.yaml`) is a human action, the same as accepting a new
baseline. See the Themis spec for the review flow.

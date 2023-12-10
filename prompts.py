from langchain.prompts import PromptTemplate


# Mapping stage prompt
map_template = """The following is a section of a wikipedia article:
{docs}
Solely based on the information in this section,
 provide concise summary (target 3 sentences) of the main 
 facts, themes, and/or subjects of the article found in this section.
Do not guess any part of the answer.
If there is insufficent information to provide an answer in this section,
 just write "None" or "N/A".
Helpful Answer:"""
map_prompt = PromptTemplate.from_template(map_template)


# Reduce stage prompt
reduce_template = """The following is set of summaries from sections of a wikipedia article:
{docs}
Take these and distill it into a concise 1 to 3 sentence answers to simple questions relevant to the subject in a form such as "What is ARTICLE_SUBJECT?" or "Why people get ARTICLE_SUBJECT?" or "Who was ARTICLE_SUBJECT?" or "What happened during ARTICLE_SUBJECT?".
Your response should be in a structured Question: Answer: format.
Helpful Answer:"""
reduce_prompt = PromptTemplate.from_template(reduce_template)


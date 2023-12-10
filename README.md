# Wikipedia Shrinker

Quick experiment to shrink Wikipedia pages into a few simple question/answer pairs.
Thought experiment posed here https://twitter.com/ShaanVP/status/1732528736376160506

I'm been meaning to look at some practical ways in which a local LLM could out perform calling an API and this seemed like a decent test.  While I had some anecdotal evidence a local 7B model can complete favorably with a model like gpt3 over an API in terms of tokens/sec and latency to first token, the quality of results can be lower.  But often that quality seems to be more about the amount of data compressed into the model than the reasoning abilties of the model.  For a lot of AI applications like RAG or this summarization task I assumed the lossy compressed knowledge could be counter productive.  So I wanted to see if I could get a decent result with a small model.

# Preparing

## wikipedia dumps
Wikipedia provides a dump of all the articles in xml format.  Google it for more details, I didn't keep great notes.  compressed it's about 20GB and uncompressed it a little over 90GB

I got mine from a mirror like below
```
mkdir xml
cd xml
wget https://wikimedia.bringyour.com/enwiki/20231201/enwiki-20231201-pages-articles.xml.bz2
bunzip2 enwiki-20231201-pages-articles.xml.bz2
```
Reason this was dumb:
* I didn't need to unzip the library will read it in the bz2 format.
* And anyway if I had to start over would have just been better to use the wikipedia api.

Though I should be able to collect stats over the whole dataset if I wanted.

## ollama
I downloaded ollama from https://ollama.ai/ and installed it before starting.  Worked super easy on my Ubuntu machine.

Any ollama models should be pulled like `ollama pull mistral` before running.

And `ollama serve` should be running in the background.  This just starts a local api that will then start the model when needed.

## python dependencies
I'm using python 3.10.  If I did my work right you should be able to get the dependencies install localy with a simple pip command.
```
pip install -r requirements.txt
```

## OpenAI
You'll need to have the environment variable `OPENAI_API_KEY` set to use gpt-3.5-turbo

# Running

To run ollama with mistral:
```
./main.py
```

For gpt-3.5-turbo:
```
./main.py --llm gpt-3.5-turbo --max_token 4096
```

# Results

Overall I think have some validation to my hunch that a local model can be competitive with an API.

## Speed
Not very scientific but running for an hour I can repeatably get these results over time.  The gap is bigger when the text to analyze is bigger than the 4K context window of the gpt-3.5-turbo model, a better openai model would likely be faster.  Mistral has 8K context window so it's not as big of a gap but when you have 20K token articles it a few more calls to the API which adds up.

| Model           | Avg Time per Article |
|-----------------|-----------------|
| mistral 7B      | 14s             |
| gpt-3.5-turbo   | 20s             |


## Quality
The quality of the results varies.  While gpt-3.5-turbo seems a little too long most of the time, it seems to make fewer egregious mistakes.  But take this with a grain of salt it's a very small sample size so it's ancecdotal and subjective.

### gpt-3.5-turbo
```
Anarchism

Q: What is anarchism?
A: Anarchism is a political philosophy and movement that aims to eliminate authority and hierarchical institutions, advocating for stateless societies and voluntary associations.

Q: What are the different schools of thought within anarchism?
A: The different schools of thought within anarchism include social anarchism and individualist anarchism, each with their own approaches and perspectives on issues such as the rejection of the state and the importance of individual autonomy.

Q: What are some key issues in anarchism?
A: Key issues in anarchism include disagreements over values, ideology, and tactics, as well as debates on the compatibility of capitalism, nationalism, and religion with anarchism. Anarchist attitudes towards the state, gender and sexuality, education, and the arts are also explored.

Q: What does the section on tertiary sources, further reading, and external links discuss?
A: The section provides additional resources related to philosophical anarchism, including criticisms, defenses, and arguments for it. It also includes a link to an online research center on the history and theory of anarchism.

Time: 19.158660888671875

ABBA

Q: Who was ABBA?
A: ABBA was a Swedish pop supergroup formed in 1972 by Agnetha Fältskog, Björn Ulvaeus, Benny Andersson, and Anni-Frid Lyngstad.

Q: What happened during ABBA's early success?
A: During their early success, ABBA won the Eurovision Song Contest in 1974, released their debut album "Ring Ring," and achieved international stardom with hits like "Waterloo" and "Dancing Queen."

Q: What happened during ABBA's period of superstardom?
A: During their period of superstardom from 1976 to 1981, ABBA released successful albums like "Arrival" and "ABBA: The Album," embarked on major tours, and had hits such as "Money, Money, Money" and "Take a Chance on Me."

Q: What happened after ABBA's unofficial breakup in 1982?
A: After their unofficial breakup in 1982, the members of ABBA had various performances and collaborations, experienced a resurgence of public interest in their music in the 1990s and early 2000s, and made reunion appearances in 2005 and 2008.

Q: What happened during ABBA's activities from 2016 to 2022?
A: From 2016 to 2022, ABBA reunited for special events, worked on a new "digital entertainment experience" featuring avatars called ABBAtars, released a sequel to the movie Mamma Mia!, recorded new songs, and announced a new album and concert residency featuring their digital avatars.

Q: What is ABBA's discography, tours, and awards?
A: ABBA released several studio albums from 1973 to 1981, with their most recent album "Voyage" released in 2021. They had concert tours and residencies, including the upcoming ABBA Voyage residency from 2022 to 2024. ABBA also received numerous awards and nominations throughout their career.

Time: 53.08847522735596
```

## mistral 7B
```
Anarchism


What is Anarchism?
Anarchism is an ideology and political philosophy that opposes all forms of authority, hierarchy, and oppression. It emerged in the 19th century as a response to capitalism, nationalism, and religion, and has since evolved into various tendencies and schools of thought. Key issues include the state, technology, humanism, enlightenment, civilisation, and democracy.

Why do people get Anarchism?
Anarchists believe that individuals should be free from oppressive institutions and authorities, including governments, corporations, and other forms of power. The anarchist vision is one of self-governance through direct democracy, mutual aid, and collective action. Anarchism has been criticized for being impractical or utopian, but many anarchists argue that it is the only way to achieve a truly just and equal society.

What are the different types of Anarchism?
There are various types of anarchism, including anarcho-syndicalism, mutualism, and libertarian communism.

Time: 12.352948665618896

ABBA

* What is ABBA?
ABBA is a Swedish pop group consisting of Agnetha Fältskog, Björn Ulvaeus, Benny Andersson, and Anni-Frid Lyngstad. They were active from 1972 to 1982, had numerous hits during their career, and won several awards.
* Who composed music for ABBA?
ABBA was a successful pop group that composed its own music. The group consisted of Agnetha Fältskog, Anni-Frid Lyngstad, Björn Ulvaeus, and Benny Andersson. They wrote and performed their music together.
* What did ABBA do after they broke up in 1982?
After breaking up in 1982, Agnetha Fältskog, Björn Ulvaeus, and Benny Andersson continued working together as songwriters, while Anni-Frid Lyngstad pursued a solo career in Europe before returning to Sweden in 1996.

Time: 27.74633765220642
```


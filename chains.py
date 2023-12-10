from langchain.chains.llm import LLMChain
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import Ollama
from langchain.chat_models import ChatOpenAI

from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

from prompts import map_prompt, map_template, reduce_prompt, reduce_template


ollama_types = [
    "mistral",
    "llama2",
    "llama2:13b",
    "orca-mini",
    "codellama",
    "vicuna",
    "neural-chat",
    "starling-lm"
]
openai_types = ["gpt-3.5-turbo"]


class WikipediaShrinker():

    def __init__(self, llm_type, max_token, verbose):
        self.verbose = verbose
        # The maximum number of tokens to use in the LLM
        # hack intended to make sure that the LLM doesn't go over the max token limit
        # when composing map reduce prompts.
        # Theory is to overestimate the number of tokens in the prompts
        #  and subtract from the max token limit.
        # Not sure if it's necessary.
        self.max_token = max_token - max(len(map_template.split(" ")), len(reduce_template.split(" ")))*2
        self.ollama_types = ollama_types
        self.openai_types = openai_types
        self.text_splitter = self.setup_text_splitter()
        self.llm = self.select_llm(llm_type)
        self.chain = self.build_llm_chain()

    def setup_text_splitter(self):
        # more sizing hacks of questionable utility to keep the LLM from going over the max token limit
        chunk_size = self.max_token * 0.8
        chunk_overlap = self.max_token * 0.05
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return text_splitter

    def select_llm(self, llm_type):
        if llm_type in self.ollama_types:
            if self.verbose:
                # streams the output of the LLM to stdout
                llm = Ollama(model=llm_type, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
            else:
                llm = Ollama(model=llm_type)
        elif llm_type in self.openai_types:
            llm = ChatOpenAI(temperature=0, model_name=llm_type)
        else:
            raise ValueError(f"Unknown llm_type: {llm_type}")
        return llm

    def build_llm_chain(self):

        # This chain is used to summarize sections of a wikipedia article
        map_chain = LLMChain(llm=self.llm, prompt=map_prompt)

        # This chain is use to summarize a set of summaries of sections of a wikipedia article from the map_chain
        reduce_chain = LLMChain(llm=self.llm, prompt=reduce_prompt)

        # Combines summaries using reduce_chain
        combine_documents_chain = StuffDocumentsChain(
            llm_chain=reduce_chain,
            # Variable name in the prompt embedded in reduce_chain
            document_variable_name="docs"
        )

        # Iteratively combines summaries
        reduce_documents_chain = ReduceDocumentsChain(
            # Collapses documents into a single document
            combine_documents_chain=combine_documents_chain,
            # TODO: Okay this is from the langchain tutorial, but I don't understand it.
            # shouldn't this be the map_chain or something like it?
            collapse_documents_chain=combine_documents_chain,
            # How big the prompt text can be
            token_max=self.max_token,
        )

        # Iterates over the documents and runs the map_chain on each section
        map_reduce_chain = MapReduceDocumentsChain(
            llm_chain=map_chain,
            reduce_documents_chain=reduce_documents_chain,
            # Variable name in the prompt embedded in map_chain
            document_variable_name="docs",
            # Return the results of the map steps in the output
            return_intermediate_steps=False,
        )

        return map_reduce_chain

    def shrink_article(self, text):
        # To use the langchain stuff we need to wrap the text in a Document
        docs = [Document(page_content=text)]
        # Split the document into chunks
        split_docs = self.text_splitter.split_documents(docs)
        # Run the chain for the article
        return self.chain.run(split_docs)

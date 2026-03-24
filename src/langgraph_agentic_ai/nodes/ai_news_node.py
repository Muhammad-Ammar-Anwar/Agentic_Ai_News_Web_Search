from requests import Response
from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
from urllib3 import response

class AiNewsNode:
    def __init__(self,llm):
        """
        Intialize the AINewsNode with API Keys for Tavily and Groq
        """

        self.tavily = TavilyClient()
        self.llm = llm

        self.state = {}

    
    def fetch_news(self,state:dict) -> dict:
        """
        Fetch AI news based on the specified frequency.

        Args:
            state (dict) : The state dictionary containing the 'frequency'.

        Returns:
            dict : The state dictionary containing the 'news'.
        """

        frequency = state['messages'][-1].content.lower()
        self.state['frequency'] = frequency
        time_range_map = {'daily':'d','weekly':'w','monthly':'m','yearly':'y'}
        days_map = {'daily':1,'weekly':7,'monthly':30,'yearly':365}

        resp = self.tavily.search(
            query=f"Top artificial intelligence (AI) technology news globally",
            topic="news",
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=15,
            days=days_map[frequency],
            # include_domain=["techcrunch.come","venturebeat.com/ai,..."] 
            )

        state['news_data'] = resp.get('results', [])
        self.state['news_data'] = state['news_data']
        return state

    def summarize_news(self,state:dict) -> dict:
        """
        Summarize the fetched news using an LLM.

        Args:
            state (dict) : The state dictionary containing the 'news_data'.

        Returns:
            dict : Updated state with 'summary' key containing the summarized news.
        """
        news_item = state['news_data']
        
        prompt_template = ChatPromptTemplate.from_messages([
            (
                "system","""Summarize AI news articles into markdown format. For each item include:
                - Date in **YYYY-MM-DD** format PST timezone
                - Concise sentences summary from latest news
                - Sort news by data wise (latest first)
                - source URL as link

                Use format:
                ### [Date]
                 - [Summary](URL)
                
                """
            ),
            ("user","Articles: \n {articles}")
        ])

        articles_str = "\n\n".join([
            f"Content: {item.get('content','')}\nURL : {item.get('url','')}\nDate: {item.get('published_date','')}"
            for item in news_item
        ])
        
        response= self.llm.invoke(prompt_template.format(articles=articles_str))
        state['summary'] = response.content
        self.state['summary']= state['summary']
        return self.state

    def save_result(self,state):
        frequency = self.state['frequency']
        summary = self.state['summary']
        filename = f"./AINews/{frequency}_summary.md"
        with open(filename,'w') as f :
            f.write(f'# {frequency.capitalize()} AI News Summary\n\n')
            f.write(summary)

        self.state['filename'] = filename
        return self.state

        

from tools import web_search_tool,search_weather,find_current_date,youtube_search,cal_distance,publish_facebook_post
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from rich import print

load_dotenv()

llm1 = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite"
)

llm2=ChatGoogleGenerativeAI(
    model='gemini-3.1-flash-lite',
    temperature=0.7
)

promt="""
You are CryptoRaja, a concise voice assistant.

Rules:
1. Answer only what the user asks.
2. Keep answers short and useful.
3. For simple questions, give a direct answer in 1-3 sentences.
4. Do not give long explanations unless the user asks for details.
5. For calculations, give the result directly.
6. For follow-up questions, remember the previous conversation.
7. Use tools only when necessary.
8. If the user asks for current information, use the appropriate tool.
9. Never add unrelated information.
"""

#create agent 1
def agent_1():
    return create_agent(
        model=llm1,
        tools=[web_search_tool,search_weather,find_current_date,youtube_search,cal_distance],
        system_prompt=promt
    )
    

#create another Agent to generate the post
def facebook_agent():
    return create_agent(
        model=llm2,
        tools=[],
        system_prompt='''
        You are a professional Facebook content writer.

Your job is to create engaging Facebook posts based on the user's topic.

Rules:

1. Write a natural and engaging Facebook post.
2. Do not explain how you created the post.
3. Do not say "Here is your post".
4. Use emojis when appropriate.
5. Use short paragraphs.
6. Add relevant hashtags at the end.
7. Do not invent facts.
8. Do NOT publish the post yourself.
9. Your job is only to generate the Facebook post.
10. Return only the final post content.
        '''
        
    )
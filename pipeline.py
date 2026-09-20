from dotenv import load_dotenv
from agents import agent_1,facebook_agent
from tools import publish_facebook_post
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage

load_dotenv()
state={}
def agent_1_pipeline(topic:str)->str:
    
    search_agent=agent_1()
    search_result=search_agent.invoke( {    
        "messages": [
            (
                "user",
                f"Find recent, reliable and detailed information about: {topic}"
            )
        ]
    })
    state['search_result']=(
        search_result['messages'][-1].content[0]['text']
    )
    
    return state['search_result']

#create facebook Agent 
def generate_facebook_post(topic:str)->str:
    agent_2=facebook_agent()
    result=agent_2.invoke(
        {
            "messages":[
            (
                'user',
                f'generate a proper facebook post on the about{topic}'
            )
        ]
            }
    )
    state['facebook_message']=(result['messages'][-1].content[0]['text'])
    return state['facebook_message']

#publish the post
def post_facebook(message:str)->str:
    result=publish_facebook_post.invoke({
        'message':message
    })
    return result
    
# if __name__=="__main__":
    
#     message=[SystemMessage("You are a very Helpful AI assistant")]
#     while True:
#         user=input("YOU: ")
#         if not user:
#             continue
#         if user.lower() in ['stop','break','exit']:
#                 print("Good bey")
#                 break
#         message.append(HumanMessage(user))
#         try:
#             result=agent_1_pipeline(message)
#             message.append(AIMessage(result))
#             print("QS: ",user)
#             print("AI: ",result)
#         except Exception as e:
#             print("Error: ",e)
        
# store=generate_facebook_post("generate facebook post about the current Cricket report")
# print(store)
# result=post_facebook(store)
# print(result)

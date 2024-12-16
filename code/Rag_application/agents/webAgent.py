from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
import os 
from fpdf import FPDF
from dotenv import load_dotenv
load_dotenv()

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

print(os.environ.get("OPENAI_API_KEY"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# Define a set of instructions for the AI agent
instructions = """You are an experienced legal researcher who always finds ATLEAST 4-5 most relevant Indian legal cases on the Internet for the given user query. Return the output of 4-5 Indian cases in the following structured format: 1)Between whom was the case fought? 2) What was the accusation? 3) What was the judgement of the case? 4)What punishment was given in the case? 5) Under what section of constitution/ IPC was the person convicted? 6) Brief description of the case in atleast 200 words"""

# Retrieve a template for creating AI functions from the hub
base_prompt = hub.pull("langchain-ai/openai-functions-template")

# Customize the base prompt with the specific instructions
prompt = base_prompt.partial(instructions=instructions)

# Initialize the ChatOpenAI with the GPT-4 model and a temperature setting of 0 for deterministic responses
llm = ChatOpenAI(model_name="gpt-4", temperature=0, api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize a custom search tool named TavilySearchResults
api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_API_KEY)
tavily_tool = TavilySearchResults(api_wrapper=api_wrapper)

# Aggregate the tools into a list for easy access
tools = [tavily_tool]

# Create an AI agent with the specified LLM and tools, and the customized prompt
agent = create_openai_functions_agent(llm, 
                                      tools, 
                                      prompt)

# Set up an executor for the agent, specifying the agent, tools, and enabling verbose output
agent_executor = AgentExecutor(agent=agent, 
                               tools=tools, 
                               verbose=True)

# result = agent_executor.invoke({"input": "Shivani Gupta, a software engineer, recently discovered that her employer, Zen Digital Pvt. Ltd., has been monitoring her personal phone activities without her explicit consent. The company installed tracking software on her work laptop, which allegedly accessed her phone data when connected to the laptop via Bluetooth or USB. Shivani claims this data includes her personal text messages, private photos, and social media activity. She argues that the company's actions have violated her right to privacy and caused significant mental distress. Zen Digital Pvt. Ltd., in its defense, states that the tracking software is part of its employee productivity monitoring policy, which is outlined in the company's terms of employment. However, Shivani asserts that she was not informed about the extent of the data being monitored or that her personal devices would be affected. Shivani is now seeking legal recourse under the right to privacy and relevant provisions of Indian law, including constitutional guarantees and any applicable penal sections regarding unauthorized access to private data."})


def WebAgentTavily(query):
    result = agent_executor.invoke({"input": query})
    pdf.multi_cell(0, 10, result['output'])

    # Save the PDF to a file
    output_pdf_path = "./data/relevant_cases.pdf"
    pdf.output(output_pdf_path)

# WebAgentTavily("Shivani Gupta, a software engineer, recently discovered that her employer, Zen Digital Pvt. Ltd., has been monitoring her personal phone activities without her explicit consent. The company installed tracking software on her work laptop, which allegedly accessed her phone data when connected to the laptop via Bluetooth or USB. Shivani claims this data includes her personal text messages, private photos, and social media activity. She argues that the company's actions have violated her right to privacy and caused significant mental distress. Zen Digital Pvt. Ltd., in its defense, states that the tracking software is part of its employee productivity monitoring policy, which is outlined in the company's terms of employment. However, Shivani asserts that she was not informed about the extent of the data being monitored or that her personal devices would be affected. Shivani is now seeking legal recourse under the right to privacy and relevant provisions of Indian law, including constitutional guarantees and any applicable penal sections regarding unauthorized access to private data.")
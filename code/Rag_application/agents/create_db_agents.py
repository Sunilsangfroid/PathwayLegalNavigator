from guidance import models
from guidance import guidance
from guidance import models, gen
from guidance import select
from guidance.models import OpenAI
from guidance.library._role import system , assistant
import os

# Extract the last assistant output
def sanitize(lm_content):
    lm_content = str(lm_content)
    segments = lm_content.split('<|im_end|>')
    # Find the last assistant segment
    for segment in reversed(segments):
        if "<|im_start|>assistant" in segment:
            # Extract and clean the output
            return segment.split("<|im_start|>assistant")[-1].strip()
    return None

@guidance
def lexicographer(lm, query): # Selects Most Relevant legal keyword 

    legal_keywords = [
        # Criminal Law
        "Murder", "Manslaughter", "Assault", "Battery", "Kidnapping",
        "Domestic violence", "Sexual assault", "Stalking", "Theft", "Burglary",
        "Robbery", "Arson", "Embezzlement", "Fraud", "Shoplifting", "Vandalism",
        "Drug possession", "Drug trafficking", "drunk driving", "Jaywalking",
        "Disorderly conduct", "Trespassing","Rape",
        
        # Civil Law - Contracts
        "Breach of contract", "Non-compete clause", "Indemnity",
        "Misrepresentation", "Force majeure"
        
        # Civil Law - Torts
        "Negligence", "Defamation", "False imprisonment",
        "Intentional infliction of emotional distress", "Invasion of privacy",
        
        # Civil Law - Property Law
        "Easement", "Encroachment", "Adverse possession",
        "Landlord-tenant disputes", "Zoning",
        
        # Family Law
        "Divorce", "Custody", "Alimony", "Child support", 
        "Adoption", "Domestic partnership", "Guardianship","Abortion",
        
        # Corporate Law
        "Incorporation", "Shareholder disputes", "Insider trading",
        "Mergers and acquisitions", "Antitrust", "Bankruptcy", "Compliance",
        
        # Employment Law
        "Discrimination", "Harassment", "Retaliation", "Wrongful termination",
        "Wage theft", "Overtime pay", "Employment contracts", "Whistleblower",
        
        # Intellectual Property Law
        "Patent", "Trademark", "Copyright", "Trade secret", "Infringement","Non Disclosure Agreement"
        
        # Environmental Law
        "Pollution", "Conservation", "Wildlife protection",
        "Climate change regulations", "Hazardous waste",
        
        # Cyber and Technology Law
        "Cybercrime", "Data breach", "Privacy law", "Hacking", "Digital piracy",
        
        # Tax Law
        "Tax evasion", "Tax fraud", "Deductions",
        "Capital gains", "Income tax",
        
        # International Law
        "Extradition", "Diplomatic immunity", "War crimes",
        "Human rights", "Sanctions",
        
        # Miscellaneous
        "Litigation", "Arbitration", "Mediation", "Statute of limitations",
        "Due process", "Habeas corpus", "Subpoena", "Injunction",
        "Liability", "Burden of proof", "" 
    ]

    with system():
        # lm += f'Determine if the following input question comes under legal domain or not. Input: {query} Answer:'
    
        lm += f'only write the answer that match from {legal_keywords}, What topic does this query about, Query: {query} \n Answer:'
    with assistant():
        lm += select(legal_keywords,recurse=True, name = 'a', skip_checks=True)

    legal_keywords.remove(lm['a'])
    print(sanitize(lm),"saniz")
    return lm

@guidance
def case_summarizer(lm, query):
    print(lm)
    with system():
        lm += (
            f"""You are an expert legal assistant specializing in summarizing legal queries for research purposes. 
            Your goal is to convert the user's input into a precise, well-written summary that highlights the key 
            legal facts, questions, and context relevant to their case. Ensure the summary is concise, professional, 
            and focuses on actionable details for further legal research. 
            
            Always refine the user's query for clarity and effectiveness in retrieving legal statutes, case law, 
            or procedural guidance. End the refined query with '**'.
            
            Question: {query}
            Answer:"""
        )
    print(lm)
    with assistant():
        lm += gen(stop='\n')
    return lm

@guidance
def IPC(lm, query):
    
    # Step 1: Check if IPC is required
    with system():
        lm += (
            f"""Determine if the following query requires referring to any IPC section.
            Respond with 'Yes' if IPC is needed and 'No' otherwise.
            Query: {query}
            Response:"""
        )
    with assistant():
        lm += select(["Yes", "No"], name="requires_ipc")

    requires_ipc = str(lm["requires_ipc"])

    # Step 2: If IPC is required, find relevant sections
    if(requires_ipc == "Yes"):
        print(lm)
        with system():
            lm += f'Give all relevant IPC sections corresponding to the given query, Do not return any empty response. give the most relevant sections of IPC related to the query. In the Final response just provide the section without any explanation. \n Query: {query} \n Section number:' 
        with assistant():
            lm += gen(stop='\n')
        print(lm)
        return lm
    else:
        return None
    
@guidance
def Constitution(lm, query):
    
    # Step 1: Check if Constitution is required
    with system():
        lm += (
            f"""Determine if the following query requires referring to any Constitution articles.
            Respond with 'Yes' if Constitution is needed and 'No' otherwise.
            Query: {query}
            Response:"""
        )
    with assistant():
        lm += select(["Yes", "No"], name="requires_constitution")

    requires_constitution = str(lm["requires_constitution"])

    # Step 2: If Constitution is required, find relevant sections
    if(requires_constitution == "Yes"):
        print(lm)
        with system():
            lm += f'Give all relevant constitution articles corresponding to the given query, Do not return any empty response. give the most relevant articles of Constitution related to the query. In the Final response just provide the articles without any explanation. \n Query: {query} \n Articles:' 
        with assistant():

            lm += gen(stop='\n')
        print(lm)
        return lm
    else:
        return None

# Agents
def initialize_model():
    lm = models.OpenAI("gpt-3.5-turbo", api_key=os.environ['OPENAI_API_KEY'])
    return lm

# Lexicographer Agent
def LexicographerAgent(user_case):
    print(user_case)
    lm = initialize_model()
    lm += lexicographer(user_case)
    return sanitize(lm)

# Case Summarizer Agent
def CaseSummarizerAgent(user_query):
    lm = initialize_model()
    lm += case_summarizer(user_query)
    print(lm)
    with open("case_summary.txt", "w") as f:
        f.write(str(sanitize(lm)))
    
    IPCLinkerAgent(user_query)
    JurisCodeAgent(user_query)

# IPC Agent
def IPCLinkerAgent(user_query):
    lm = initialize_model()
    lm += IPC(user_query)

    if(lm is not None):
        with open("ipc_sections.txt", "w") as f:
            f.write(str(sanitize(lm)))

# Constitution Agent
def JurisCodeAgent(user_query):
    lm = initialize_model()
    lm += Constitution(user_query)

    if(lm is not None):
        with open("constitution_sections.txt", "w") as f:
            f.write(str(sanitize(lm)))

# Web Search Agent
@guidance
def Web_search(lm, query):
    print(lm)
    with system():
        lm += (
            f"""
            You are an advanced legal web search agent with expertise in identifying relevant case laws. 
            Your task is to find and summarize cases based on the user's query. When performing this task:
            
            1. Identify 5 cases that are relevant to the query.
            2. For each case, provide a structured summary containing:
                - Case Name and Citation
                - Court and Jurisdiction
                - Decision Date
                - Key Legal Issues
                - Judgment Summary
                - Relevance to the user's query
            
            Ensure that the output is well-structured and focuses on actionable insights. If any part of the query is ambiguous, infer the most logical interpretation for conducting the search. Output the results in a clear, structured format as shown below:

            ---
            **Structured Case Summary:**
            - **Case Name and Citation:** [Name, Citation]
            - **Court and Jurisdiction:** [Court, Jurisdiction]
            - **Decision Date:** [Date]
            - **Key Legal Issues:** [Key Issues in brief]
            - **Judgment Summary:** [Brief summary of the judgment]
            - **Relevance to Query:** [How this case relates to the user's query]
            ---
            
            Query to analyze: "{query}"
            """
        )
    print(lm)
    with assistant():
        lm += gen(stop='\n')
    return lm


def WebAgent(user_query):
    lm = initialize_model()
    lm += Web_search(user_query)
    return sanitize(lm)
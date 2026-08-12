from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import PromptTemplate,load_prompt

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile")

st.header("Research Tool")

paper_input = st.selectbox(
    "Select the research paper name:",
    [
        "Attention is all you need",
        "BERT: pre training of deep bidirectional transformer",
        "GPT-3 Language models are few shot learners",
        "Diffusion models are beats GANS on image synthesis"
    ]
)

style_input = st.selectbox(
    "Select explanation style:",
    [
        "Beginner friendly",
        "Technical",
        "Code-Oriented",
        "Mathematical"
    ]
)

length_input = st.selectbox(
    "Select the length of the input:",
    [
        "Short (1-2 paragraphs)",
        "Medium (3-5 paragraphs)",
        "Long (detailed)"
    ]
)

# Template
template=load_prompt('template.json')

if st.button("Summarize"):

    prompt = template.invoke({
        "paper_input": paper_input,
        "style_input": style_input,
        "length_input": length_input
    })

    result = model.invoke(prompt)

    st.write(result.content)

#prompttemplate can be also replaced with f string but the thing is with this we can also do validation at developement so  there is no any propblme during the production like ve can give validate_template=True so it will check the inputs given in the input_varibale and the template and if it wrong the number is wrong then it will giev the error during the development only 

#next we can also reuse the template menas if the same template  is used multiple times then we can save this template using the json file and can be used in multiple files
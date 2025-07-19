import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from groq import GroqError
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

# Session state to persist email
if "generated_email" not in st.session_state:
    st.session_state.generated_email = ""

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize LLM
def get_llm():
    return ChatGroq(
        temperature=0.7,
        groq_api_key=groq_api_key,
        model_name="LLaMA3-70b-8192"
    )

llm = get_llm()

st.set_page_config(page_title="Cold Email Generator", layout="wide")
st.title("🚀 AI-Powered Cold Email Generator with ChromaDB")

# Sidebar inputs
st.sidebar.header("1. Careers Page URL and Portfolio")
careers_url = st.sidebar.text_input("Enter Careers Page URL to scrape job listings")
portfolio_file = st.sidebar.file_uploader("Or upload your portfolio CSV", type=["csv"])

st.sidebar.header("2. Email Details")
sender_email = st.sidebar.text_input("Your Gmail address")
sender_password = st.sidebar.text_input("Gmail App Password", type="password")
receiver_email = st.sidebar.text_input("Recipient's Email")

st.header("Generate Cold Email")

# Scrape job listings if URL provided
job_description = ""
if careers_url:
    try:
        import requests
        from bs4 import BeautifulSoup
        res = requests.get(careers_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        job_elem = soup.find(['h2', 'h3'], string=True)
        job_description = job_elem.get_text(strip=True) if job_elem else ''
        desc_elem = job_elem.find_next('p') if job_elem else None
        if desc_elem:
            job_description += ' - ' + desc_elem.get_text(strip=True)
        st.success("✅ Job data scraped successfully")
    except Exception as e:
        st.error(f"Error scraping URL: {e}")

# Helper: Retry wrapper for Groq API
def generate_email(portfolio_text, max_retries=3):
    prompt = f"""
You are an expert cold email writer.

Based on the following portfolio:
{portfolio_text}

Write a cold email to a company offering software or web development services.
Keep it short, professional, and impressive.
"""
    for attempt in range(1, max_retries + 1):
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            st.warning(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(attempt)
    st.error("❌ Our AI engine is currently unavailable. Please try again later.")
    return None

# Set up ChromaDB if portfolio file is uploaded
if portfolio_file:
    df = pd.read_csv(portfolio_file)
    st.write("**Preview of your portfolio:**")
    st.dataframe(df)

    tech_stack_docs = [Document(page_content=f"Tech Stack: {row[0]}\nLink: {row[1]}") for _, row in df.iterrows()]
    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    split_docs = text_splitter.split_documents(tech_stack_docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory="chroma_data")

    if st.button("Generate Email"):
        query_result = vectordb.similarity_search(job_description, k=1)
        relevant_portfolio = query_result[0].page_content if query_result else ""

        combined_text = f"""Job Description: {job_description}\n{relevant_portfolio}"""
        generated_email = generate_email(combined_text)

        if generated_email:
            st.session_state.generated_email = generated_email

# Always show "Generated Email" and Send section if email exists
if st.session_state.generated_email:
    st.subheader("📝 Generated Email")
    st.text_area("Email body", value=st.session_state.generated_email, height=300)

    st.subheader("📤 Send Email")
    subject = st.text_input("Email Subject", value="AI-Powered Dev Services Inquiry")
    if st.button("Send Email"):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(st.session_state.generated_email, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            st.success("✅ Email sent successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error sending email: {e}")

else:
    st.info("Upload your portfolio CSV and fill in details in the sidebar to get started.")

🚀 AI-Powered Cold Email Generator
An AI-driven Streamlit app that scrapes job descriptions from company websites, matches them with your portfolio using ChromaDB, and generates personalized cold emails using the LLaMA3 model via Groq API.

✨ Features
🔍 Scrape job listings from company career pages

📊 Match job requirements with your tech portfolio

🧠 Generate cold emails using Groq’s LLaMA3 model

📬 Send emails directly via Gmail SMTP

💡 Clean, animated Streamlit UI

🛠 Tech Stack
Python

Streamlit

Groq API (LLaMA3)

ChromaDB

LangChain

BeautifulSoup

SMTP








🚀 Installation & Setup Instructions

1. Clone the Repository

git clone https://github.com/your-username/cold-email-generator.git
cd cold-email-generator

2. Create a Virtual Environment

For Windows:
python -m venv venv
venv\Scripts\activate

For macOS/Linux:
python3 -m venv venv
source venv/bin/activate

3. Install Required Packages

pip install -r requirements.txt

4. Add Your Groq API Key

Create a file named .env in the root folder and add this line:
GROQ_API_KEY=your_groq_api_key_here

5. Run the Application

streamlit run app/main.py

6. (Optional) Gmail SMTP Setup for Sending Emails

- Enable 2-Step Verification in your Gmail account.
- Generate an App Password.
- Use this App Password in the sidebar where it asks for your Gmail credentials.








import streamlit as st #used for frontend coding in the localhost
import requests #create connection btwn user(client) and website(server)
import ssl #certificate to create secure connection
import socket #used for communication(channel)
from urllib.parse import urlparse #parse url
import google.generativeai as genai #importing google genai


# configuring ai part of the website
genai.configure(api_key="") #configure api key
model = genai.GenerativeModel("gemini-2.5-flash") #configure model

#check for https 
def check_url(url):
    if url.startswith("https"): #check if url starts with https
        return True
    else:
        return False

def check_ssl(domain):
    try:
        cnction = ssl.create_default_context() #secure connection
        with cnction.wrap_socket(socket.socket(),server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain,443))
            cert = s.getpeercert()
        return True
    except:
        return False

def check_headers(url):
    
    security_headers = [
        "Content Security Policy",
        "Strict Transport Security",#https connection
        "X-Frame-Options",
        "X-XSS-Protection",
    ]

    result = {}

    try:
        r = requests.get(url)
        headers = r.headers
        
        for header in security_headers:
            if header in headers:
                result[header] = True
            else:
                result[header] = False
    except:
        print("connection dint happen btwn user and website")
    
    return result


def calculate_score(https,ssl_cert,headers):

    score = 0

    if https:
        score+=20
    
    if ssl_cert:
        score+=20
    
    if headers["Content Security Policy"]:
        score+=20
    
    if headers["Strict Transport Security"]:
        score+=20

    if headers["X-Frame-Options"]:
        score+=15

    if headers["X-XSS-Protection"]:
        score+=5

    return score

def generate_feedback(url,score,headers):
    
    prompt = f"""

    i have created a website analyzer and analyzed the url, i will give you the website url {url},security score {score} and finally the headers {headers} value which i got it from my test. based on the score suggest some improvement in 3 lines if the score is not equal to 100

    """
    response = model.generate_content(prompt)

    return response.text


st.title("Website Security Analyzer")
st.write("Welcome to the website security analyzer")

url = st.text_input("Enter website URL (e.g., https://example.com/):")

if st.button("Scan Website"):
    if url:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        with st.spinner("Scanning website..."):
            https = check_url(url)
            ssl_valid = check_ssl(domain)
            certificate = check_headers(url)
            
            try:
                score = calculate_score(https, ssl_valid, certificate)
                feedback = generate_feedback(url, score, certificate)
            except Exception as e:
                score = "Error"
                feedback = f"Failed to generate feedback. Ensure your API key is configured or the URL is responsive. Error details: {e}"
        
        st.header("Security Report")
        
        st.write(f"**Website URL:** {url}")
        st.write(f"**Check HTTPS:** {https}")
        st.write(f"**Check SSL:** {ssl_valid}")
        
        st.subheader("Security Headers")
        if certificate:
            for h in certificate:
                st.write(f"**{h}:** {certificate[h]}")
        else:
            st.warning("Could not establish a connection to verify headers.")
        
        st.subheader("Security Score")
        st.write(f"**{score}/100**")
        
        st.subheader("Feedback Given")
        st.info(feedback)
    else:
        st.warning("Please enter a website URL to scan.")

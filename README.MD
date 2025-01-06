# genai-path-planer
A GenAI-powered personal academic advisor designed for high school students.

This is a Streamlit web application that leverages Amazon Cognito for user authentication. It integrates with Amazon Bedrock's Anthropic Claude models as the LLMs to process and evaluate requests.

## Start the app
### Clone source code to your local drive
```
git clone https://github.com/lanazhang/genai-path-planer
cd genai-path-planer
```
### Create Python Virtual Environment
```
python3 -m venv .venv
source .venv/bin/activate
```
### Install dependencies
```
pip install -r requirements.txt
```
### Set up secrets to your local streamlit sceret.toml file
At **~/.streamlit/scerets.toml** with proper values
```
COGNITIO_POOL_ID = ""
COGNITIO_APP_CLIENT_ID = ""
AWS_KEY = ""
AWS_SECRET = ""
AWS_REGION = ""
```
### Start the streamlit app
```
streamlit run app.py
```
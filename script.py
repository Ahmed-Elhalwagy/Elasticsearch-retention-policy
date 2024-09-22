from dotenv import load_dotenv
import os
import datetime
import time
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

### Elasticsearch configuration
elasticsearch_host= os.getenv('ELASTICSEARCH_HOST')
username = os.getenv('ELASTICSEARCH_USERNAME')
password = os.getenv('ELASTICSEARCH_PASSWORD')
index_name = os.getenv('ELASTICSEARCH_INDEX_NAME')

### Record the time of the test
timestamp = datetime.datetime.today()


def check_index_health(index):
    print(elasticsearch_host)
    print(f'API request to /_cat/indices/{index}')
    url = f'{elasticsearch_host}/_cat/indices/{index}?format=json&bytes=mb'
    health_check_response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, verify=False)
    data = health_check_response.json()
    
    print(f'Status Code: {health_check_response.status_code}')
    index_size = data[0]["store.size"]
    print(f'Current "{index}" index size is {index_size} mb')

    return int(index_size)

def delete_index_docs(index):
    body = {
     "query": {
     "match_all": {}
   }} 
    print(f'API request to /{index}/_delete_by_query')
    url= f'{elasticsearch_host}/{index}/_delete_by_query'
    delete_query_resposnse = requests.post(url, auth=HTTPBasicAuth(username, password), json=body, headers=headers, verify=False)  
    
    print(f'Status Code: {delete_query_resposnse.status_code}')
    print("All docs has been marked as deleted")
    
def forcemerge(index):
    print(f'API request to /{index_name}/_forcemerge?only_expunge_deletes=true')

    url= f"{elasticsearch_host}/{index_name}/_forcemerge?only_expunge_deletes=true"
    forcemerge_resposnse = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, verify=False)  
    
    print(f'Status Code: {forcemerge_resposnse.status_code}')
    print("All docs marked as deleted has been completly deleted")

def send_email(index_name, index_size, timestamp):
    html_content = ""
    with open('email-template.html', 'r') as file:
        html_content = file.read()
    
    html_content = html_content.replace('{timestamp}', str(timestamp))
    html_content = html_content.replace('{index_size}', str(index_size))
    html_content = html_content.replace('{index_name}', index_name)
    
    sender_email = os.getenv('SENDER_EMAIL_ADDRESS')
    app_password = os.getenv('EMAIL_ADDRESS_APP_PASSWORD')
    receiver_email = os.getenv('RECIEVER_EMAIL_ADDRESS')
    subject = "Task 2"
    email_server = os.getenv('EMAIL_HOST')
    email_port = os.getenv('EMAIL_PORT')

    # Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP(email_server, email_port)
        server.starttls()
        server.login(sender_email, app_password)  # Log in with app password
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error occurred while sending the email: {e}")


def main():
    current_index_size = check_index_health(index_name) 
    if current_index_size >= 1:
        delete_index_docs(index_name)
        print('2 Seconds delay')
        time.sleep(2)
        forcemerge(index_name)
    
    send_email(index_name, current_index_size, timestamp)
    
if __name__ == '__main__':
    main()
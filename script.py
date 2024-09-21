import datetime
import time
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

### Elasticsearch username, password and index name
username = 'elastic'
password = '########'
index_name = 'halwagyy-index'

#### start the check health HTTP request
print(f'API request to /_cat/indices/{index_name}')

url = f'https://66.135.30.87:9200/_cat/indices/{index_name}?format=json&bytes=mb'
health_check_response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, verify=False)
data = health_check_response.json()

print(f'Status Code: {health_check_response.status_code}')

index_size = data[0]["store.size"]
timestamp = datetime.datetime.today()

print(f'Current {index_name} index size is {index_size} mb')

### check if the index size is bigger than 1 mb
if int(index_size) >= 1:
    body = {
     "query": {
     "match_all": {}
   }} 
    
    print(f'API request to /{index_name}/_delete_by_query')
    url= f'https://66.135.30.87:9200/{index_name}/_delete_by_query'
    delete_query_resposnse = requests.post(url, auth=HTTPBasicAuth(username, password), json=body, headers=headers, verify=False)  
    
    print(f'Status Code: {delete_query_resposnse.status_code}')
    print("All docs has been marked as deleted")
    
    print('2 Seconds delay')
    time.sleep(2)
    
    print(f'API request to /{index_name}/_forcemerge?only_expunge_deletes=true')

    url= f"https://66.135.30.87:9200/{index_name}/_forcemerge?only_expunge_deletes=true"
    forcemerge_resposnse = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, verify=False)  
    
    print(f'Status Code: {forcemerge_resposnse.status_code}')
    print("All docs marked as deleted has been completly deleted")

### send a report
html_sytle="""
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            background-color: #f4f4f4;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        h1 {
            text-align: center;
            color: #333;
        }
"""
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report Page</title>
    <style>{html_sytle}</style>
</head>
<body>

    <h1>Report</h1>
    
    <table>
        <thead>
            <tr>
                <th>Time</th>
                <th>Size (MB)</th>
                <th>Index Name</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{timestamp}</td>
                <td>{index_size}</td>
                <td>{index_name}</td>
            </tr>
        </tbody>
    </table>

</body>
</html>
<
"""

sender_email = ""
app_password = "#####" # temporary Google Application password

receiver_email = ""
subject = "Task 2"

# Setup the MIME
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(html_content, 'html'))

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)  # Log in with app password
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error occurred while sending the email: {e}")

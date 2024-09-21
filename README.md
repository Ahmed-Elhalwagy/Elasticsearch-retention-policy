This script simply queries the health of a specific index, then deletes all old docs and reclaims the disk space. You can edit the age of the documents that should be deleted.
***
Install Required packages
```
pip install -r requirements.txt
```
Create a `.env`  File
```
ELASTICSEARCH_HOST=https://IP_ADDRESS:9200
ELASTICSEARCH_USERNAME=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_INDEX_NAME=

SENDER_EMAIL_ADDRESS=
EMAIL_ADDRESS_APP_PASSWORD=
RECIEVER_EMAIL_ADDRESS=
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

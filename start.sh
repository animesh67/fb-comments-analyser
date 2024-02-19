#!/bin/sh
source "./virtual_env/bin/activate"

pip3 install -r requirements.txt
scrapyd & python3 manage.py runserver & cd fbcrawl
scrapyd-deploy -p 
cd ..

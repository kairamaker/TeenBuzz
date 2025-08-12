#!/bin/bash
cd "/Users/kairaschool/Downloads/TeenBuzz"
source teenbuzz_env/bin/activate
python auto_fetch_articles.py >> daily_fetch.log 2>&1

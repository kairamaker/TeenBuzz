#!/bin/bash
# Manual article fetch script
cd "$(dirname "$0")"
source teenbuzz_env/bin/activate
python fetch_real_articles_local.py

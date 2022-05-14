#!#usr/bin/env bash
set -euo pipeline

curl https://data.statmt.org/news-crawl/en/news.2007.en.shuffled.deduped.gz --output en_2007.gz
curl https://data.statmt.org/news-crawl/ru/news.2016.ru.shuffled.deduped.gz --output ru_2016.gz
curl https://data.statmt.org/news-crawl/es/news.2008.es.shuffled.deduped.gz --output es_2008.gz
gzip -d *.gz

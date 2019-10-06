FROM python:3.7.4-buster
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
ADD . /code/arsenal_america_pub_scraper
WORKDIR /code/arsneal_america_pub_scraper/arsenal_america_pub_scraper

FROM python:3.10.8-slim

RUN apt update && apt-get install --assume-yes libxml2-dev libxslt1-dev zip unzip coq

WORKDIR ccg2lambda_pipe
COPY . .

RUN pip install -r requirements.txt

RUN python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('punkt')"

RUN ./ccg2lamp/en/install_candc.sh

CMD [ "tail", "-f", "/dev/null" ]
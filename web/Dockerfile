FROM python:3
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN pip install ./en_core_web_sm-2.0.0.tar.gz
RUN python -m spacy download en_core_web_sm
CMD ["python", "app.py"]
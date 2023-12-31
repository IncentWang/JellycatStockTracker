FROM continuumio/anaconda3

WORKDIR /app

COPY . /app/

RUN conda env create -f environment.yml

EXPOSE 8000

RUN conda init bash

RUN chmod +x ./start.sh

ENTRYPOINT ["./start.sh"]

FROM python:3.6
MAINTAINER Roy Meissner <meissner@informatik.uni-leipzig.de>

#WORKDIR /opt/docker

# ---------------- #
#   Installation   #
# ---------------- #

#ADD app/ .

RUN mkdir /recommender
WORKDIR /recommender

COPY . /recommender

#COPY requirements.txt .
RUN pip install -r requirements.txt

# ----------------- #
#   Configuration   #
# ----------------- #

EXPOSE 9000

# ----------- #
#   Cleanup   #
# ----------- #

RUN apt-get update && \
    		apt-get autoremove -y && \
		apt-get -y clean && \
		rm -rf /var/lib/apt/lists/*

# -------- #
#   Run!   #
# -------- #

#ENTRYPOINT ["python app/appmain.py"]

CMD python app/appmain.py

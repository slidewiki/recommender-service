FROM python:3
MAINTAINER Jaume Jordán <jjordan@dsic.upv.es>


ARG BUILD_ENV=local
ENV BUILD_ENV ${BUILD_ENV}

# ---------------- #
#   Installation   #
# ---------------- #

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# ----------------- #
#   Configuration   #
# ----------------- #

EXPOSE 80

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

CMD [ "python", "./app/appmain.py" ]

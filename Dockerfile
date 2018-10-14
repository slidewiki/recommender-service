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
RUN mkdir data

# ----------------- #
#   Configuration   #
# ----------------- #

EXPOSE 8000

# --------- #
#   Build   #
# --------- #
RUN python setup.py install

# -------- #
#   Run!   #
# -------- #

CMD [ "python", "./app/appmain.py" ]

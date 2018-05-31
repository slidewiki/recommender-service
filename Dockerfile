FROM python:3
MAINTAINER Roy Meissner <meissner@informatik.uni-leipzig.de>

# ---------------- #
#   Installation   #
# ---------------- #

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

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

CMD [ "python", "./app/appmain.py" ]

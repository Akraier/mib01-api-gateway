#
# Docker file for MessageInABottle S01 v1.0
#
FROM python:3.8
LABEL maintainer="MessageInABottle Squad01 API Gateway"
LABEL version="1.0"
LABEL description="MessageInABottle Application Squad01"

# creating the environment
COPY . /app
# moving the static contents
RUN ["mv", "/app/mib/static", "/static"]
# setting the workdir
WORKDIR /app

# installing all requirements
RUN ["pip", "install", "-r", "requirements.prod.txt"]

# exposing the port
EXPOSE 5000/tcp

# Main command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
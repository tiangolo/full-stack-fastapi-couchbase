FROM python:3.6

# Dependencies for Couchbase
RUN wget -O - http://packages.couchbase.com/ubuntu/couchbase.key | apt-key add -
RUN echo "deb http://packages.couchbase.com/ubuntu stretch stretch/main" > /etc/apt/sources.list.d/couchbase.list
RUN apt-get update && apt-get install -y libcouchbase-dev build-essential

RUN pip install --upgrade pip
RUN pip install celery==4.2.1 passlib[bcrypt] tenacity requests pydantic couchbase emails fastapi>=0.1.13 uvicorn gunicorn pyjwt python-multipart email_validator

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter notebook --ip=0.0.0.0 --allow-root
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyter ; fi"
EXPOSE 8888

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

CMD ["bash", "/app/backend-start.sh"]

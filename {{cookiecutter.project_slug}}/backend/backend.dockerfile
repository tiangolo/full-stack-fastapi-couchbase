FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

# Dependencies for Couchbase
RUN wget -O - http://packages.couchbase.com/ubuntu/couchbase.key | apt-key add -
RUN echo "deb http://packages.couchbase.com/ubuntu stretch stretch/main" > /etc/apt/sources.list.d/couchbase.list
RUN apt-get update && apt-get install -y libcouchbase-dev libcouchbase2-bin build-essential dos2unix

RUN pip install celery==4.2.1 passlib[bcrypt] tenacity requests couchbase emails "fastapi>=0.7.1" uvicorn gunicorn pyjwt python-multipart email_validator jinja2

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter notebook --ip=0.0.0.0 --allow-root
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyter ; fi"
EXPOSE 8888

COPY ./app /app
RUN find /app/*.sh -type f -print0 | xargs -0 dos2unix && apt-get --purge remove -y dos2unix && rm -rf /var/lib/apt/lists/*

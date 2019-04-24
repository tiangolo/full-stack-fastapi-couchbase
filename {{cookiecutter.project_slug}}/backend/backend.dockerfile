FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

# Dependencies for Couchbase
RUN wget -O - http://packages.couchbase.com/ubuntu/couchbase.key | apt-key add -
RUN echo "deb http://packages.couchbase.com/ubuntu stretch stretch/main" > /etc/apt/sources.list.d/couchbase.list
RUN apt-get update && apt-get install -y libcouchbase-dev libcouchbase2-bin build-essential

RUN pip install celery~=4.3 passlib[bcrypt] tenacity requests couchbase emails "fastapi>=0.16.0" uvicorn gunicorn pyjwt python-multipart email_validator jinja2

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyterlab ; fi"
EXPOSE 8888

COPY ./app /app

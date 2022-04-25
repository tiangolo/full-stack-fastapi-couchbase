FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

# Dependencies for Couchbase
RUN wget -O - https://packages.couchbase.com/clients/c/repos/deb/couchbase.key | apt-key add - && \
    OS_CODENAME=`cat /etc/os-release | grep VERSION_CODENAME | cut -f2 -d=` && \
    VERSION_ID=`cat /etc/os-release | grep VERSION_ID | cut -f2 -d= | cut -f2 -d'"'` && \
    echo "deb https://packages.couchbase.com/clients/c/repos/deb/debian${VERSION_ID} ${OS_CODENAME} ${OS_CODENAME}/main" > /etc/apt/sources.list.d/couchbase.list && \
    apt-get update && apt-get install -y libcouchbase3 libcouchbase-dev libcouchbase3-tools libcouchbase-dbg libcouchbase3-libev build-essential

RUN pip install \
    celery~=4.3 \
    passlib[bcrypt] \
    tenacity \
    requests \
    couchbase \
    emails \
    "fastapi>=0.16.0" \
    uvicorn \
    gunicorn \
    pyjwt \
    python-multipart \
    email_validator \
    jinja2

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyterlab ; fi"
EXPOSE 8888

COPY ./app /app

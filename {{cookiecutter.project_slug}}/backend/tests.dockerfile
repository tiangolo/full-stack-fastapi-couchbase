FROM python:3.6

RUN wget -O - https://packages.couchbase.com/clients/c/repos/deb/couchbase.key | apt-key add - && \
    OS_CODENAME=`cat /etc/os-release | grep VERSION_CODENAME | cut -f2 -d=` && \
    VERSION_ID=`cat /etc/os-release | grep VERSION_ID | cut -f2 -d= | cut -f2 -d'"'` && \
    echo "deb https://packages.couchbase.com/clients/c/repos/deb/debian${VERSION_ID} ${OS_CODENAME} ${OS_CODENAME}/main" > /etc/apt/sources.list.d/couchbase.list && \
    apt-get update && apt-get install -y libcouchbase-dev build-essential

RUN pip install requests pytest tenacity passlib[bcrypt] couchbase "fastapi>=0.16.0"

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyterlab ; fi"
EXPOSE 8888

COPY ./app /app

ENV PYTHONPATH=/app

COPY ./app/tests-start.sh /tests-start.sh

RUN chmod +x /tests-start.sh

# This will make the container wait, doing nothing, but alive
CMD ["bash", "-c", "while true; do sleep 1; done"]

# Afterwards you can exec a command /tests-start.sh in the live container, like:
# docker exec -it backend-tests /tests-start.sh

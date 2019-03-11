FROM python:3.6

RUN wget -O - http://packages.couchbase.com/ubuntu/couchbase.key | apt-key add -
RUN echo "deb http://packages.couchbase.com/ubuntu stretch stretch/main" > /etc/apt/sources.list.d/couchbase.list
RUN apt-get update && apt-get install -y libcouchbase-dev build-essential

RUN pip install requests pytest tenacity passlib[bcrypt] couchbase "fastapi>=0.7.1"

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter notebook --ip=0.0.0.0 --allow-root
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyter ; fi"
EXPOSE 8888

COPY ./app /app

ENV PYTHONPATH=/app

COPY ./app/tests-start.sh /tests-start.sh

RUN chmod +x /tests-start.sh

# This will make the container wait, doing nothing, but alive
CMD ["bash", "-c", "while true; do sleep 1; done"]

# Afterwards you can exec a command /tests-start.sh in the live container, like:
# docker exec -it backend-tests /tests-start.sh

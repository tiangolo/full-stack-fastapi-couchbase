FROM tiangolo/uwsgi-nginx-flask:python3.6

# Dependencies for Couchbase
RUN wget -O - http://packages.couchbase.com/ubuntu/couchbase.key | apt-key add -
RUN echo "deb http://packages.couchbase.com/ubuntu stretch stretch/main" > /etc/apt/sources.list.d/couchbase.list
RUN apt-get update && apt-get install -y libcouchbase-dev build-essential

RUN pip install --upgrade pip
RUN pip install flask flask-cors raven[flask] celery==4.1.1 passlib[bcrypt] flask-apispec flask-jwt-extended tenacity requests pydantic couchbase emails

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter notebook --ip=0.0.0.0 --allow-root
ARG env=prod
RUN bash -c "if [ $env == 'dev' ] ; then pip install jupyter ; fi"
EXPOSE 8888

COPY ./app /app
WORKDIR /app/

ENV STATIC_PATH /app/app/static
ENV STATIC_INDEX 1

EXPOSE 80

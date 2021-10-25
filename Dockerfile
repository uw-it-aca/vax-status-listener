FROM gcr.io/uwit-mci-axdd/django-container:1.3.3 as app-container

USER root
RUN apt-get update && apt-get install libpq-dev vim -y
USER acait

ADD --chown=acait:acait vs_listener/VERSION /app/vs_listener/
ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/
RUN . /app/bin/activate && pip install -r requirements.txt

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/

FROM gcr.io/uwit-mci-axdd/django-test-container:1.3.3 as app-test-container

COPY --from=app-container /app/ /app/

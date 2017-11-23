from python:3.6-alpine

ENV FLASK_APP app.py
ENV FLASK_DEBUG true
EXPOSE 80

COPY ../requirements.txt /requirements.txt
RUN pip install -r requirements.txt

COPY ../app.py /app.py
COPY ../settings.py /settings.py
COPY ../security.py /security.py
COPY ../signups.py /signups.py
COPY ../validation.py /validation.py

COPY ./demo_server.py /demo_server.py

WORKDIR /

# Run database init before starting dev server
ENTRYPOINT ["python"]
CMD ["demo_server.py"]

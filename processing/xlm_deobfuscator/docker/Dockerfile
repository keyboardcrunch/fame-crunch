FROM python:3

RUN pip install XLMMacroDeobfuscator

COPY script.py /app/script.py

VOLUME ["/data"]

WORKDIR /data

ENTRYPOINT ["python", "/app/script.py"]

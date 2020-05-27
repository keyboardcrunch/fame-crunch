FROM python:3

RUN pip install -U https://github.com/DissectMalware/XLMMacroDeobfuscator/archive/master.zip

COPY script.py /app/script.py

VOLUME ["/data"]

WORKDIR /data

ENTRYPOINT ["python", "/app/script.py"]

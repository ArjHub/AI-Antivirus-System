FROM remnux/remnux-distro:latest

RUN apt-get update && \
    apt-get install -y git

WORKDIR /app

COPY . .

RUN python3 -m pip install --upgrade pip

RUN pip install -r remnux.requirements .txt

EXPOSE 8000

CMD python3 app.py

FROM python:3
WORKDIR /opt/star-burger
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . .



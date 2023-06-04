FROM python:3.9
WORKDIR /opt/BurgerKing
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . .




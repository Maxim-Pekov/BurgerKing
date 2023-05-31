FROM node:16 as frontend
LABEL maintainer='MaxPekov'
WORKDIR /opt/BurgerKing
COPY ./assets ./assets
COPY ./bundles-src ./bundles-src
COPY ./package.json .
RUN npm install
RUN npm ci --omit=dev
RUN ./node_modules/.bin/parcel build ./bundles-src/index.js --dist-dir ./bundles --public-url="./"

FROM python:3.9
WORKDIR /opt/BurgerKing
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . .
COPY --from=frontend /opt/BurgerKing/bundles /opt/BurgerKing/bundles




FROM node:16
LABEL maintainer='MaxPekov'
WORKDIR /opt/BurgerKing
COPY ./assets ./assets
COPY ./bundles-src ./bundles-src
COPY ./package.json .
RUN npm install
RUN npm ci --omit=dev
RUN ./node_modules/.bin/parcel build ./bundles-src/index.js --dist-dir ./bundles --public-url="./"

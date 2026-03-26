FROM node:24-alpine

RUN apk add --no-cache python3 py3-pip

RUN npm install -g pm2

WORKDIR /app

COPY bots/requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

COPY package.json package-lock.json* ./
RUN npm install

COPY tsconfig.json ./
COPY src/ ./src/
RUN npm run build

CMD ["node", "dist/index.js"]

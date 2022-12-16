FROM --platform=$BUILDPLATFORM golang:1.19 as build

ARG K6_VERSION=0.41.0
ARG XK6_VERSION=0.8.1
ARG XK6_INFLUXDB_VERSION=0.2.2

COPY ./es6-template /tmp/es6-template
RUN tar czf /tmp/k6-template.tar.gz -C /tmp es6-template && rm /tmp/es6-template -r
ADD https://api.github.com/repos/grafana/xk6/tarball/tags/v${XK6_VERSION}       /tmp/xk6.tar.gz

RUN echo ":: Unpacking sources..." \
    && mkdir -p /tmp/build/xk6 \
    && cd /tmp/build/xk6 && tar xf /tmp/xk6.tar.gz --strip-components 1 \
    && echo ":: Building xk6..." \
    && GOPATH="/tmp" go install ./... \
    && echo ":: Building k6..." \
    && mkdir /tmp/output \
    && /tmp/bin/xk6 build v${K6_VERSION} --output /tmp/output/k6 \
        --with github.com/grafana/xk6-output-influxdb@v${XK6_INFLUXDB_VERSION}

FROM --platform=$BUILDPLATFORM python:3.11 as pybuild

WORKDIR /build
COPY ./server ./server
COPY ./setup.py ./setup.py
COPY ./requirements.txt ./requirements.txt
RUN python ./setup.py bdist_wheel \
    && ls -lah dist/k6webserver-*-py3-none-any.whl

FROM --platform=$BUILDPLATFORM node:16

RUN apt update -y && apt install -y python3 python3-pip python3-venv

RUN python3 -m venv /venv

RUN mkdir -p /usr/local/bin
COPY --from=build /tmp/output/k6 /usr/local/bin/k6

RUN install -g node -o node -d /workdir
WORKDIR /workdir

COPY --from=build /tmp/k6-template.tar.gz /tmp/k6-template.tar.gz
RUN tar xf /tmp/k6-template.tar.gz --strip-components 1 \
    && chown -R node:node . \
    && chmod -R 777 . \
    && rm /tmp/k6-template.tar.gz \
    && ls -lah

USER node

RUN npm install .
RUN npx browserslist@latest --update-db

USER root

COPY --from=pybuild /build/dist/k6webserver-*.whl /tmp/
RUN /venv/bin/pip install /tmp/k6webserver-*.whl \
    && rm /tmp/k6webserver-*.whl

COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

USER node

FROM --platform=$BUILDPLATFORM golang:1.19 as build

ARG K6_VERSION=0.41.0
ARG XK6_VERSION=0.8.1
ARG XK6_INFLUXDB_VERSION=0.2.2

ADD https://api.github.com/repos/grafana/k6-template-es6/tarball/heads/master   /tmp/k6-template.tar.gz
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

FROM --platform=$BUILDPLATFORM node:14.14

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

COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

USER node

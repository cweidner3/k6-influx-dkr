# XK6 Built K6 With InfluxDB v2 Support

[![Version](https://img.shields.io/github/v/release/cweidner3/k6-influx-dkr?label=GitHub%20Release)](https://github.com/cweidner3/k6-influx-dkr)
[![Docker](https://img.shields.io/docker/v/cweidner3/k6-influx-dkr?label=Latest%20Docker)](https://github.com/cweidner3/k6-influx-dkr)
[![Build Release Docker Images in CI](https://github.com/cweidner3/k6-influx-dkr/actions/workflows/push-rel-images.yml/badge.svg)](https://github.com/cweidner3/k6-influx-dkr/actions/workflows/push-rel-images.yml)

## Links

- [Repository](https://github.com/cweidner3/k6-influx-dkr)
- [DockerHub](https://hub.docker.com/r/cweidner3/k6-influx-dkr)

## Building

_Note: Requires docker-buildx for building the image as is._

```
~$ docker buildx build --platform linux/amd64 -t test:latest .
```

## Running

### Oneshot Runs

```bash
cat ./mytestscript.js | docker run -it --rm \
    --env K6_INFLUXDB_ORGANIZATION="${INFLUX_ORG}" \
    --env K6_INFLUXDB_BUCKET="${INFLUX_BUCKET}" \
    --env K6_INFLUXDB_TOKEN="${INFLUX_TOKEN}" \
    --env K6_INFLUXDB_INSECURE="${INFLUX_INSECURE}" \
    --network="host" \
    test:latest \
    -o xk6-influxdb="${INFLUX_HOST}"
```

### Webserver Mode

| Env Variable       | Description                                           |
|--------------------|-------------------------------------------------------|
| APP_USE_WEBSERVER  | Set to 1 to use the webserver.                        |
| APP_WEBSERVER_HOST | Listen host [default 0.0.0.0].                        |
| APP_WEBSERVER_PORT | Port to use [default 5050].                           |
| APP_SECRET         | Secret string used to start the load tests.           |
| INFLUX_HOST        | Host url where the InfluxDB instance is located.      |
| INFLUX_ORG         | Organization to use when publishing to InfluxDB.      |
| INFLUX_BUCKET      | Bucket to use when publishing to InfluxDB.            |
| INFLUX_TOKEN       | Token to use when publishing to InfluxDB.             |
| INFLUX_INSECURE    | Allow publishing to non-tls protected servers.        |
| LT_URL             | Load testing url to test against.                     |
| LT_VUS             | Virtual Users to use in load tests.                   |
| LT_ITERATIONS      | Iterations of the test script to run (must be > VUS). |
| BASE_URL           | Host address for injecting into browser recorder load tests that have been touched up with variables. |
| TX_PROTO           | Protocol used for url requests.                       |

To run the load tests.

```
~$ curl "http://localhost:5050/run?secret=<SECRET>"
OK
```

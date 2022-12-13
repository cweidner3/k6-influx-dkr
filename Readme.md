# XK6 Built K6 With InfluxDB v2 Support

## Links

- [Repository](https://github.com/cweidner3/k6-influx-dkr)
- [DockerHub](https://hub.docker.com/r/cweidner3/k6-influx-dkr)

## Building

_Note: Requires docker-buildx for building the image as is._

```
~$ docker buildx build --platform linux/amd64 -t test:latest .
```

# Traceroute

A home brewed implementation of traceroute in python using sockets.

## Usage

This project uses google's [python-fire](https://github.com/google/python-fire) for ease of use. Please make sure to install the requirements via `pip install -r requirements.txt` beforehand.

**NOTE**: Due to `socket` being used this has to be run with elevated privileges.

To use it as cli:
```
❯❯❯ sudo ./tracert.py traceroute google.com
tracing:    172.217.17.238  | timeout: 1s
192.168.178.1   | ttl: 1    | 1.67 ms
217.0.116.210   | ttl: 2    | 17.04 ms
87.190.177.62   | ttl: 3    | 17.29 ms
194.25.6.238    | ttl: 4    | 18.23 ms
80.157.129.174  | ttl: 5    | 18.7 ms
108.170.227.186 | ttl: 7    | 17.73 ms
172.217.17.238  | ttl: 8    | 17.67 ms
["80.157.129.174", 18.7]
```

To use it as module:
```

tracer = Trace()
slowest_hop, rtt = tracer.traceroute("192.168.178.73")
```

## Caveats / Todos / Issues

- Work around `sudo`-requirement
- Implement more traceroute features
#!/usr/bin/env python
"""
traceroute, homebrew style.

Author:
    Benedikt Koller
    kontakt@benkoller.de
"""
import socket
import time
import struct
import fire
import logging

logging.basicConfig(format="%(message)s", level=logging.INFO)


class Trace(object):
    """Display the route and transit delays for ICMP packets over a network."""

    def __init__(self):
        """Provide sockets in class-scope to save sockets."""
        self._port = 33434
        self._timeout = 1

    def _get_sockets(self):
        return \
            socket.socket(
                socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp')
            ), \
            socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp')
            )

    def _ping(self, ttl, ip):
        """Ping a target with fixed ttl."""
        recv, send = self._get_sockets()
        send.settimeout(self._timeout)
        recv.settimeout(self._timeout)
        send.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv.bind(("", self._port))
        start = time.time()
        send.sendto("", (ip, self._port))
        address = None
        resp_type = None
        resp_code = None
        try:
            packet, address = recv.recvfrom(1024)
            address = address[0]
            icmp_header = packet[20:28]
            resp_type, resp_code, _, _, _ = struct.unpack(
                'bbHHh', icmp_header)
        except socket.error:
            pass
        finally:
            stop = time.time()
            send.close()
            recv.close()
        # Use round to probihibt float shenanigans
        duration = round(((stop - start) * 1000), 2)
        return address, duration, resp_type, resp_code

    def _get_ip(self, target):
        """Try your best at making sense of user input."""
        ip = None
        try:
            socket.inet_aton(target)
            ip = target
        except socket.error:
            try:
                ip = socket.gethostbyname(target)
            except socket.error:
                raise ValueError(
                    "Your target is neither a valid hostname nor IP")
        return ip

    def traceroute(self, target):
        """
        Iteratively increase ttl to determine hops along the path.

        To use this you'll need to pass a valid IP or resolvable hostname.

        Example use from the CLI (asuming you're root):
            ./tracert.py traceroute 8.8.8.8
            ./tracert.py traceroute google.com

        TODO:
            * nicer outputs
            * copy more functionality of the UNIX traceroute
        """
        ip = self._get_ip(target)
        logging.info(
            "tracing: \t{ip} \t| timeout: {timeout}s".format(
                ip=ip, timeout=self._timeout)
        )
        ttl = 1
        hops = {}
        for i in range(1, 30):
            hop, duration, resp_type, resp_code = self._ping(ttl, ip)
            message = None
            if hop and resp_type != 0:
                hops[duration] = hop
                message = "{hop}\t| ttl: {ttl} \t| {time} ms".format(
                    hop=hop, ttl=ttl, time=duration)
            if message is not None:
                logging.info(message)
                logging.debug("ICMP response type/code: {type}/{code}".format(
                    type=resp_type,
                    code=resp_code)
                )
            ttl += 1
            if hop == ip or all([resp_type, resp_code]) == 3:
                # ICMP port unreachable (3/3) indicates we've reached the end.
                # Alternatively host might match target.
                logging.debug("- - - finished traceroute. - - -")
                break
        slowest_time = sorted(hops.iterkeys())[len(hops.keys()) - 1]
        slowest_hop = hops[slowest_time]
        return (slowest_hop, slowest_time)

if __name__ == '__main__':
    fire.Fire(Trace())

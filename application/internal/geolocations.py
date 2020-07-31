import ipinfo

from whatsmyip.ip import get_ip
from whatsmyip.providers import GoogleDnsProvider
from flask import request

class GeoLocations:
    """ GeoLocation Service."""
    def __init__(self, app=None):
        if app is not None:
            self.init(app)

    def init(self, app) -> None:
        self.token = app.config["IPINFO_TOKEN"]

    def location(self):
        """ Determines the location of the client accounting for typical proxy settings.
            In the event the request is coming from the same machine / loop back ip
            we'll attempt to resolve the actual IP address for the machine """
        
        if 'X-Real-IP' in request.headers:
            remote_addr = request.headers.get('X-Real-IP')
        elif 'X-Forwarded-For' in request.headers:
            remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
        else:
            remote_addr = getattr(request, "remote_addr", "untrackable")

        if remote_addr == "127.0.0.1" or remote_addr.startswith("192.168."):
            try:
                remote_addr = get_ip(GoogleDnsProvider)
            except Exception as e:
                print(str(e))
                remote_addr = "untrackable"
        
        details = None
        if remote_addr != "untrackable":
            details = ipinfo.getHandler(self.token).getDetails(remote_addr).all
        return details

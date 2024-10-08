import socket
import ssl


class RequestBuilder:
    def __init__(self, host, path, verb="GET", encoding="utf8"):
        self.host = host
        self.path = path
        self.verb = verb
        self.encoding = encoding
        self.httpVersion = "HTTP/1.1"
        self.headers = {
            "Host":         self.host,
            "Connection":   "close",
        }

    def add_header(self, key, val):
        self.headers[key] = val

    def build_request(self):
        assert self.host != ""
        assert self.path != ""
        request = "{} {} {}\r\n".format(self.verb, self.path, self.httpVersion)
        for k, v in self.headers.items():
            request += "{}: {}\r\n".format(k, v)
        request += "\r\n"
        # print(request)
        return request.encode(self.encoding)


class FileGrabber:
    def __init__(self, url):
        self.url = url
        assert self.url != ""

    def grab(self):
        with open(self.url, encoding="utf-8") as f:
            return f.read()


class URL:
    def __init__(self, url):
        # http://example.org
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file"]

        if self.scheme != "file":
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443

            if "/" not in url:
                url = url + "/"

            self.host, url = url.split("/", 1)
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)

            self.path = "/" + url
        else:
            self.file_grabber = FileGrabber(url)

    def request(self):
        if self.scheme == "file":
            content = self.file_grabber.grab()
            return content
        else:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP,
            )
            s.connect((self.host, self.port))

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                # this creates a new socket
                # but we reassign it, because if the connection
                # is encrypted, it doesn't make any sense to keep
                # using the old socket
                # server_hostname should match the Host request header
                s = ctx.wrap_socket(s, server_hostname=self.host)

            rb = RequestBuilder(self.host, self.path)
            rb.add_header("User-Agent", "brow-user")
            s.send(rb.build_request())

            response = s.makefile("r", encoding="utf-8", newline="\r\n")
            # status line
            statusline = response.readline()
            version, status, explanation = statusline.split(" ", 2)

            # response headers
            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n":
                    break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()

            # make sure this headers (special cases) are not present
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers

            # content
            content = response.read()
            s.close()
            return content


def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            # end="" tells Python not to print a new line char
            print(c, end="")


def load(url):
    body = url.request()
    show(body)


if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))

import socket
import sys
import mimetypes
import os


def response_ok(body, mimetype):
    """returns a basic HTTP response"""
    resp = []
    resp.append("HTTP/1.1 200 OK")
    resp.append("Content-Type: {0}".format(mimetype))
    resp.append("")
    resp.append(body)
    return "\r\n".join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return "\r\n".join(resp)


def response_not_found():
    """returns 404 File Not Found"""
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    return "\r\n".join(resp)  


def parse_request(request):
    first_line = request.split("\r\n", 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    print >>sys.stderr, 'request is okay'
    return uri  

def resolve_uri(uri):
    #import pdb; pdb.set_trace()
    home = 'webroot'
    filename = os.path.join(home, uri.lstrip('/'))
    if os.path.isfile(filename):
        mimetype = mimetypes.guess_type(filename)[0]
        body = open(filename, 'rb').read()
        return body, mimetype
    elif os.path.isdir(filename):
        listing = "\n".join(os.listdir(filename))
        return listing, 'text/plain'
    else:
        if not os.path.exists(filename):
            raise ValueError("File Not Found")
            print >>sys.stderr, "No such file found"
  

def server():
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print >>sys.stderr, "making a server on %s:%s" % address
    sock.bind(address)
    sock.listen(1)
    
    try:
        while True:
            print >>sys.stderr, 'waiting for a connection'
            conn, addr = sock.accept() # blocking
            try:
                print >>sys.stderr, 'connection - %s:%s' % addr
                request = ""
                while True:
                    data = conn.recv(1024)
                    request += data
                    if len(data) < 1024 or not data:
                        break

                try:
                    uri = parse_request(request)
                    body, mimetype = resolve_uri(uri)
                except NotImplementedError:
                    response = response_method_not_allowed()
                except ValueError:
                    response = response_not_found()    
                else:
                    response = response_ok(body, mimetype)

                print >>sys.stderr, 'sending response'
                conn.sendall(response)
            finally:
                conn.close()
            
    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)

"""Exercise the shipped Nginx routes locally without production TLS or ports."""
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None

def port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]

http_port, site_port = port(), port()
config = (ROOT / 'deploy/nginx.conf').read_text()
lines = []
for line in config.splitlines():
    if 'listen [::]' in line or 'ssl_certificate' in line or 'ssl_protocols' in line:
        continue
    lines.append(line.replace('listen 80;', f'listen 127.0.0.1:{http_port};')
                 .replace('listen 443 ssl;', f'listen 127.0.0.1:{site_port};')
                 .replace('/var/www/lmm.best/current', str(ROOT / 'site')))
opener = urllib.request.build_opener(NoRedirect)
def get(path, selected_port=site_port):
    try:
        response = opener.open(urllib.request.Request(
            f'http://127.0.0.1:{selected_port}{path}', headers={'Host': 'lmm.best'}), timeout=3)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.headers, response.read()

with tempfile.TemporaryDirectory(prefix='lmm-best-nginx-') as temp:
    directory = Path(temp)
    conf = directory / 'nginx.conf'
    conf.write_text(f'pid {directory}/nginx.pid;\nerror_log {directory}/error.log;\n'
                    'daemon off; master_process off; events {}\n'
                    'http { include /etc/nginx/mime.types; access_log off; types_hash_max_size 4096;\n'
                    + ''.join(f'{kind}_temp_path {directory}/{kind};\n' for kind in
                              ['client_body', 'proxy', 'fastcgi', 'uwsgi', 'scgi'])
                    + '\n'.join(lines) + '\n}\n')
    process = subprocess.Popen(['nginx', '-p', temp, '-c', str(conf)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for attempt in range(40):
            try:
                status, headers, body = get('/')
                break
            except urllib.error.URLError:
                if process.poll() is not None:
                    raise RuntimeError(process.communicate()[1].decode())
                time.sleep(.05)
        else:
            raise RuntimeError('Local Nginx did not become ready')
        assert status == 200 and body == (ROOT / 'site/index.html').read_bytes()
        for name in ['robots.txt', 'sitemap.xml', 'style.css', 'logo.png']:
            status, headers, body = get('/' + name)
            assert status == 200 and body == (ROOT / 'site' / name).read_bytes(), name
        assert get('/does-not-exist')[0] == 404
        status, headers, body = get('/index.html')
        assert status == 308 and headers['Location'] == 'https://lmm.best/'
        status, headers, body = get('/', http_port)
        assert status == 308 and headers['Location'] == 'https://lmm.best/'
        print('Nginx homepage, assets, 404 and canonical redirects passed')
    finally:
        if process.poll() is None:
            process.terminate()
        process.communicate(timeout=5)

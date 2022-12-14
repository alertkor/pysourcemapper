import uuid, sys, os
from requests_cache import CachedSession
from urllib.parse import urlparse
from seleniumwire import webdriver
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException

# declaration variables
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5026.0 Safari/537.36 Edg/103.0.1254.0'


def create_sourcemap_context(path):
    return f'//# sourceMappingURL={path}.map'


def interceptor(request):
    if request.path.endswith('.js'):
        sourcemap_context = create_sourcemap_context(urlparse(request.url).path.split('/')[-1])
        response = s.get(request.url, headers=request.headers)
        body = response.text
        request.create_response(
            status_code=response.status_code,
            headers={**response.headers},
            body=f'{body}\r\n{sourcemap_context}' if body.find('sourceMappingURL') == -1 else f'{body}',
        )


if __name__ == '__main__':
    try:
        uid = str(uuid.uuid1())
        s = CachedSession(uid)
        options = webdriver.ChromeOptions()
        options.add_argument(f'user-agent={USER_AGENT}')
        driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
        driver.request_interceptor = interceptor

        if len(sys.argv) != 1:
            if sys.argv[1].startswith('http://') or sys.argv[1].startswith('https://'):
                driver.get(sys.argv[1])

        while True:
            try:
                _ = driver.window_handles
            except WebDriverException as e:
                print('[-] Driver was closed.')
                os.remove(f'{uid}.sqlite')
                break
            print(end="\r")

    except SessionNotCreatedException:
        print('[-] Version mismatch: https://chromedriver.chromium.org/downloads')
        exit()

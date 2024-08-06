import binascii
import rsa
import base64
import requests
from bs4 import BeautifulSoup
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from urllib import parse

class Login(object):
    def __init__(self, base_url):
        # 初始化登录所需的URL和headers
        self.base_url = base_url
        self.key_url = parse.urljoin(base_url, '/jwglxt/xtgl/login_getPublicKey.html')
        self.login_url = parse.urljoin(base_url, '/jwglxt/xtgl/login_slogin.html')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': self.login_url
        }
        self.sess = requests.Session()
        self.cookies = ''
        self.cookies_str = ''

    def login(self, sid, password):
        try:
            # 获取CSRF token
            req = self.sess.get(self.login_url, headers=self.headers)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, 'html.parser')
            tokens = soup.find(id='csrftoken').get("value")

            # 获取RSA公钥
            res = self.sess.get(self.key_url, headers=self.headers)
            res.raise_for_status()
            res_json = res.json()
            n = res_json['modulus']
            e = res_json['exponent']

            # 加密密码
            encrypted_pwd = self.get_rsa(password, n, e)

            # 发送登录请求
            login_data = {
                'csrftoken': tokens,
                'yhm': sid,
                'mm': encrypted_pwd
            }
            response = self.sess.post(self.login_url, headers=self.headers, data=login_data)
            response.raise_for_status()

            # 保存cookies
            self.cookies = self.sess.cookies
            self.cookies_str = '; '.join([item.name + '=' + item.value for item in self.cookies])

        except requests.RequestException as e:
            print(f"网络错误: {e}")
        except Exception as e:
            print(f"出现了一个错误: {e}")

    @classmethod
    def encrypt_sqf(cls, pkey, str_in):
        # 使用RSA公钥加密
        private_keybytes = base64.b64decode(pkey)
        prikey = RSA.importKey(private_keybytes)
        signer = PKCS1_v1_5.new(prikey)
        signature = base64.b64encode(signer.encrypt(str_in.encode("utf-8")))
        return signature

    @classmethod
    def get_rsa(cls, pwd, n, e):
        # 使用RSA加密密码
        message = pwd.encode()
        rsa_n = int(binascii.b2a_hex(binascii.a2b_base64(n)), 16)
        rsa_e = int(binascii.b2a_hex(binascii.a2b_base64(e)), 16)
        key = rsa.PublicKey(rsa_n, rsa_e)
        encropy_pwd = rsa.encrypt(message, key)
        result = binascii.b2a_base64(encropy_pwd).decode('utf-8').strip()
        return result

import configparser
import requests
import login
import bs4

# 配置文件路径
CONF_FILE = './config.ini'

# 读取配置文件
cf = configparser.ConfigParser()
cf.read(CONF_FILE)
userName = cf.get("accountConfig", "userName")
passWord = cf.get('accountConfig', "passWord")
base_url = cf.get('baseConfig', "baseUrl")
isEnglishCourse = cf.get('baseConfig', "isEnglishCourse")

# 创建登录对象并执行登录
lgn = login.Login(base_url=base_url)
lgn.login(userName, passWord)

# 获取登录后的cookies字符串形式
cookie_str = lgn.cookies_str

# 设置HTTP请求头，包括cookies
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Cookie': cookie_str
}

# 发送请求，获得网页数据
res = requests.get(base_url + '/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default', headers=headers)
res.encoding = 'utf-8'
soup = bs4.BeautifulSoup(res.text, 'lxml')

# 从HTML中获取配置参数
def get_html_config(soup, parameter_name):
    try:
        value = soup.find(id=parameter_name).get("value")
        return value if value is not None else ''
    except AttributeError:
        return ''

# 封装公共请求数据部分
def prepare_data(common_params, additional_params=None):
    data = common_params.copy()
    if additional_params:
        data.update(additional_params)
    return data

# 定义用户类
class User(object):
    def __init__(self):
        # 初始化用户信息，使用配置文件或HTML配置
        self.kklxdm = cf.get("baseConfig", "kklxdm") or get_html_config(soup, 'firstKklxdm')
        self.xkxnm = cf.get("baseConfig", "xkxnm") or get_html_config(soup, 'xkxnm')
        self.xkxqm = cf.get("baseConfig", "xkxqm") or get_html_config(soup, 'xkxqm')
        self.njdm_id = cf.get("baseConfig", "njdm_id") or get_html_config(soup, 'njdm_id')
        self.zyh_id = cf.get("baseConfig", "zyh_id") or get_html_config(soup, 'zyh_id')
        self.xkkz_id = cf.get("baseConfig", "xkkz_id") or get_html_config(soup, 'xkkz_id')
        self.xsbj = cf.get("baseConfig", "xsbj") or get_html_config(soup, 'xsbj')
        self.header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31',
            'Accept': 'application/json',
            'Cookie': cookie_str
        }

    # 获取可选课程列表
    def get_course_list(self, keyW):
        url = base_url + '/jwglxt/xsxk/zzxkyzb_cxZzxkYzbDisplay.html'
        common_params = {
            'xkxnm': self.xkxnm,
            'xkxqm': self.xkxqm,
            'kklxdm': self.kklxdm,
            'kspage': 1,
            'jspage': 20,
            'yl_list[0]': 1
        }
        additional_params = {}
        if isEnglishCourse != 'false':
            additional_params = {
                'xsbj': self.xsbj,
                'xqh_id': '0',
                'jg_id': '0',
                'zyfx_id': 'wfx',
                'bh_id': '0',
                'xbm': '0',
                'xslbdm': '0',
                'ccdm': '0'
            }
        if keyW:
            additional_params['filter_list[0]'] = keyW
        data = prepare_data(common_params, additional_params)
        req = requests.post(url, data=data, headers=self.header)
        # print(req.text)
        return req.json()

    # 获取课程详情
    def get_course_detail(self, kch):
        url = base_url + '/jwglxt/xsxk/zzxkyzbjk_cxJxbWithKchZzxkYzb.html'
        common_params = {
            'bklx_id': 0,
            'njdm_id': self.njdm_id,
            'xkxnm': self.xkxnm,
            'xkxqm': self.xkxqm,
            'kklxdm': self.kklxdm,
            'kch_id': kch,
            'xkkz_id': self.xkkz_id
        }
        additional_params = {}
        if isEnglishCourse != 'false':
            additional_params = {
                'xsbj': self.xsbj,
                'xqh_id': '0',
                'jg_id': '0',
                'zyfx_id': 'wfx',
                'bh_id': '0',
                'xbm': '0',
                'xslbdm': '0',
                'ccdm': '0'
            }
        data = prepare_data(common_params, additional_params)
        req = requests.post(url, data=data, headers=self.header)
        return req.json()

    # 获取已选课程列表
    def get_choosed_list(self):
        url = base_url + '/jwglxt/xsxk/zzxkyzb_cxZzxkYzbChoosedDisplay.html'
        data = {'xkxnm': self.xkxnm, 'xkxqm': self.xkxqm}
        req = requests.post(url, data=data, headers=self.header)
        return req.json()

    # 选课
    def choose_course(self, jxb_ids, kch_id):
        url = base_url + '/jwglxt/xsxk/zzxkyzbjk_xkBcZyZzxkYzb.html'
        data = {
            'jxb_ids': jxb_ids,
            'kch_id': kch_id,
            'qz': 0,
            'njdm_id': self.njdm_id,
            'zyh_id': self.zyh_id
        }
        req = requests.post(url, data=data, headers=self.header)
        return req.json()

    # 退课
    def quit_course(self, jxb_ids):
        url = base_url + '/jwglxt/xsxk/zzxkyzb_tuikBcZzxkYzb.html'
        data = {'jxb_ids': jxb_ids}
        req = requests.post(url, data=data, headers=self.header)
        return req.json()

# 选择器常量
from mypy.modulefinder import verify_module

LOGIN_SELECTORS = {
    'login_url': 'https://example.com/login',  # 登录页面URL
    'username_input': '#username',
    'password_input': '#password',
    'login_button': '#login-button',
    'login_success': '#dashboard'
}

# 配置常量
CONFIG = {
    'DEFAULT_TIMEOUT': 10,
    'RETRY_TIMES': 3,
    'SCREENSHOT_DIR': 'screenshots'
}


# 百度搜索相关常量
BAIDU_SELECTORS = {
    'search_url': 'https://www.baidu.com',
    'search_input': '@name=wd',
    'search_button': '@value=百度一下'
}

# le相关配置
LE = {
    'url': 'https://sosovalue.com/zh/exp',
    'watch_btn' : 'text=观看', # 观看
    'verify_btn' : 'text=验证',
    'share_btn' : 'text=分享', #分享
    'quote_btn' : '引用', #引用
    'rf_btn' : '回复', #回复
    'rg' :'点赞',  # 点赞
    'verify_text':'text:验证失败',
    'success' : 'text=我已了解',
    'verify_fail_close' : '@xmlns=http://www.w3.org/2000/svg'
}


OFC_CONFIG = {
    'url': 'https://ofc.onefootball.com/s2/',
    'let_go' : "text=Let's go",
    'verify': 'text=Verify',
    'verify_time': 'text:23h'
}


XOS_CONFIG= {
    'url':'https://x.ink/airdrop',
    'check_in':'text=立即签到',
    'verify' : '今日已签到'
}
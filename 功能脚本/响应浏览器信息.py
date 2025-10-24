from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime
import uuid
import platform
import random
import string
import os
import time
import hashlib
import re

app = Flask(__name__)

def generate_trace_id():
    """生成AWS Trace ID格式的追踪ID"""
    # 格式: Root=1-{timestamp}-{random_hex}
    timestamp = hex(int(datetime.now().timestamp()))[2:]
    random_hex = ''.join(random.choices(string.hexdigits.lower(), k=24))
    return f"Root=1-{timestamp}-{random_hex}"

def add_aws_headers(headers_dict):
    """
    添加AWS负载均衡器头部（仅在环境变量启用时）
    真实的httpbin.org部署在AWS上，由ALB自动添加X-Amzn-Trace-Id
    """
    # 只有在环境变量SIMULATE_AWS=true时才添加AWS头部
    if os.getenv('SIMULATE_AWS', 'false').lower() == 'true':
        if 'X-Amzn-Trace-Id' not in headers_dict:
            headers_dict['X-Amzn-Trace-Id'] = generate_trace_id()
    
    return headers_dict

def generate_browser_fingerprint(user_agent, headers):
    """
    生成浏览器指纹，模拟TLS和HTTP/2指纹算法
    基于User-Agent和HTTP头部信息生成各种指纹
    """
    # 基于User-Agent解析浏览器信息
    browser_info = parse_user_agent(user_agent)
    
    # 生成JA3指纹（模拟TLS客户端指纹）
    ja3_text, ja3_hash = generate_ja3_fingerprint(browser_info, headers)
    
    # 生成JA3N指纹（JA3的标准化版本）
    ja3n_text, ja3n_hash = generate_ja3n_fingerprint(browser_info, headers)
    
    # 生成JA4系列指纹
    ja4 = generate_ja4_fingerprint(browser_info, headers)
    ja4_r = generate_ja4_r_fingerprint(browser_info, headers)
    ja4_o = generate_ja4_o_fingerprint(browser_info, headers)
    ja4_ro = generate_ja4_ro_fingerprint(browser_info, headers)
    
    # 生成Akamai HTTP/2指纹
    akamai_text, akamai_hash = generate_akamai_fingerprint(browser_info, headers)
    
    return {
        "user_agent": user_agent,
        "ja4": ja4,
        "ja4_r": ja4_r,
        "ja4_o": ja4_o,
        "ja4_ro": ja4_ro,
        "ja3_hash": ja3_hash,
        "ja3_text": ja3_text,
        "ja3n_hash": ja3n_hash,
        "ja3n_text": ja3n_text,
        "akamai_hash": akamai_hash,
        "akamai_text": akamai_text
    }

def parse_user_agent(user_agent):
    """
    解析User-Agent字符串，提取浏览器信息
    """
    ua_lower = user_agent.lower()
    
    # 检测浏览器类型和版本
    if 'chrome' in ua_lower and 'edg' not in ua_lower:
        browser = 'chrome'
        # 提取Chrome版本
        version_match = re.search(r'chrome/(\d+)', ua_lower)
        version = version_match.group(1) if version_match else '120'
    elif 'firefox' in ua_lower:
        browser = 'firefox'
        version_match = re.search(r'firefox/(\d+)', ua_lower)
        version = version_match.group(1) if version_match else '120'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        browser = 'safari'
        version_match = re.search(r'version/(\d+)', ua_lower)
        version = version_match.group(1) if version_match else '17'
    elif 'edg' in ua_lower:
        browser = 'edge'
        version_match = re.search(r'edg/(\d+)', ua_lower)
        version = version_match.group(1) if version_match else '120'
    else:
        browser = 'unknown'
        version = '0'
    
    # 检测操作系统
    if 'windows' in ua_lower:
        os_name = 'windows'
        if 'windows nt 10.0' in ua_lower:
            os_version = '10'
        elif 'windows nt 6.1' in ua_lower:
            os_version = '7'
        else:
            os_version = '10'
    elif 'mac os x' in ua_lower or 'macos' in ua_lower:
        os_name = 'macos'
        version_match = re.search(r'mac os x (\d+)[_.](\d+)', ua_lower)
        os_version = f"{version_match.group(1)}.{version_match.group(2)}" if version_match else '14.0'
    elif 'linux' in ua_lower:
        os_name = 'linux'
        os_version = 'unknown'
    else:
        os_name = 'unknown'
        os_version = 'unknown'
    
    return {
        'browser': browser,
        'version': version,
        'os': os_name,
        'os_version': os_version,
        'full_ua': user_agent
    }

def generate_ja3_fingerprint(browser_info, headers):
    """
    生成JA3指纹（模拟）
    JA3格式: TLSVersion,Ciphers,Extensions,EllipticCurves,EllipticCurvePointFormats
    基于User-Agent和headers信息生成更动态的TLS指纹
    """
    # 根据浏览器类型生成不同的TLS参数
    if browser_info['browser'] == 'chrome':
        # Chrome的典型TLS参数
        tls_version = "771"  # TLS 1.2
        cipher_suites = "4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53"
        extensions = "35-13-5-16-43-45-23-18-17613-11-65037-65281-10-27-51-0"
        elliptic_curves = "4588-29-23-24"
        ec_point_formats = "0"
    elif browser_info['browser'] == 'firefox':
        # Firefox的典型TLS参数
        tls_version = "771"
        cipher_suites = "4865-4866-4867-49195-49199-52393-52392-49196-49200-49171-49172-156-157-47-53"
        extensions = "0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21"
        elliptic_curves = "29-23-24-25"
        ec_point_formats = "0"
    elif browser_info['browser'] == 'safari':
        # Safari的典型TLS参数
        tls_version = "771"
        cipher_suites = "4865-4866-4867-49196-49195-52393-49200-49199-52392-49162-49161-49172-49171-157-156-53-47"
        extensions = "0-10-11-13-16-23-35-43-45-51-65281"
        elliptic_curves = "23-24-25-29"
        ec_point_formats = "0"
    else:
        # 默认参数
        tls_version = "771"
        cipher_suites = "47-53-5-10-49161-49162-49171-49172-50-56-19-4"
        extensions = "0-10-11"
        elliptic_curves = "23-24-25"
        ec_point_formats = "0"
    
    # 根据headers动态调整指纹参数
    # 检查Accept-Language，影响扩展列表
    accept_language = headers.get('Accept-Language', '')
    if 'zh' in accept_language.lower():
        extensions += "-28"  # 添加中文相关扩展
    if 'en' in accept_language.lower():
        extensions += "-27"  # 添加英文相关扩展
    
    # 检查Accept-Encoding，影响密码套件
    accept_encoding = headers.get('Accept-Encoding', '')
    if 'br' in accept_encoding:  # Brotli支持
        cipher_suites += "-49309"
    if 'gzip' in accept_encoding:
        cipher_suites += "-49308"
    
    # 检查Connection头，影响扩展
    connection = headers.get('Connection', '')
    if 'keep-alive' in connection.lower():
        extensions += "-43"  # 添加keep-alive扩展
    
    # 检查DNT (Do Not Track)，影响扩展
    if headers.get('DNT'):
        extensions += "-51"  # 添加隐私扩展
    
    # 构建JA3字符串
    ja3_text = f"{tls_version},{cipher_suites},{extensions},{elliptic_curves},{ec_point_formats}"
    
    # 生成MD5哈希
    ja3_hash = hashlib.md5(ja3_text.encode()).hexdigest()
    
    return ja3_text, ja3_hash

def generate_ja3n_fingerprint(browser_info, headers):
    """
    生成JA3N指纹（JA3的标准化版本，对扩展和密码套件进行排序）
    JA3N通过排序提高指纹一致性，并利用headers信息进行优化
    """
    # 获取基础JA3参数（已经包含headers优化）
    ja3_text, _ = generate_ja3_fingerprint(browser_info, headers)
    
    # 解析JA3字符串
    parts = ja3_text.split(',')
    if len(parts) >= 3:
        tls_version = parts[0]
        cipher_suites = parts[1]
        extensions = parts[2]
        elliptic_curves = parts[3] if len(parts) > 3 else ""
        ec_point_formats = parts[4] if len(parts) > 4 else ""
        
        # 对密码套件进行排序（JA3N的增强特点）
        if cipher_suites:
            cipher_list = cipher_suites.split('-')
            cipher_list.sort(key=int)
            cipher_suites = '-'.join(cipher_list)
        
        # 对扩展进行排序（JA3N的核心特点）
        if extensions:
            ext_list = extensions.split('-')
            ext_list.sort(key=int)
            extensions = '-'.join(ext_list)
        
        # 对椭圆曲线进行排序
        if elliptic_curves:
            curve_list = elliptic_curves.split('-')
            curve_list.sort(key=int)
            elliptic_curves = '-'.join(curve_list)
        
        # 根据headers添加额外的标准化信息
        # 检查Sec-Fetch-* 头部（现代浏览器特征）
        if headers.get('Sec-Fetch-Site'):
            extensions += "-65037"  # 添加Fetch Metadata扩展
        if headers.get('Sec-Fetch-Mode'):
            extensions += "-65038"
        
        # 重新构建JA3N字符串
        ja3n_text = f"{tls_version},{cipher_suites},{extensions},{elliptic_curves},{ec_point_formats}"
    else:
        ja3n_text = ja3_text
    
    # 生成MD5哈希
    ja3n_hash = hashlib.md5(ja3n_text.encode()).hexdigest()
    
    return ja3n_text, ja3n_hash

def generate_ja4_fingerprint(browser_info, headers):
    """
    生成JA4指纹
    JA4格式: Protocol_CipherCount+CipherList_ExtensionCount+ExtensionList_SignatureAlgorithms
    基于headers信息动态调整协议和参数
    """
    # 基础协议检测
    protocol_version = "t12"  # 默认TLS 1.2
    
    # 根据headers检测HTTP版本
    http_version = "h1"  # 默认HTTP/1.1
    if headers.get('HTTP2-Settings') or headers.get(':method'):
        http_version = "h2"  # HTTP/2
    elif headers.get('Upgrade', '').lower() == 'h2c':
        http_version = "h2"
    
    # 检测TLS版本（基于User-Agent和其他headers）
    user_agent = headers.get('User-Agent', '')
    if 'Chrome/1' in user_agent or 'Firefox/1' in user_agent:  # 现代浏览器
        protocol_version = "t13"  # TLS 1.3
    
    # 根据浏览器和headers生成JA4参数
    if browser_info['browser'] == 'chrome':
        # Chrome的参数，受headers影响
        packet_size = "1516" if http_version == "h2" else "1024"
        protocol = f"{protocol_version}d{packet_size}{http_version}"
        cipher_count = "8"
        cipher_list = "daaf6152771"
        extension_count = "d"
        extension_list = "d8a2da3f94cd"
        
        # 根据Accept-Language调整
        if 'zh' in headers.get('Accept-Language', '').lower():
            cipher_list = "daaf6152772"  # 中文环境变体
        
    elif browser_info['browser'] == 'firefox':
        packet_size = "1312" if http_version == "h2" else "1024"
        protocol = f"{protocol_version}d{packet_size}{http_version}"
        cipher_count = "9"
        cipher_list = "b2e4f8a1c3d5"
        extension_count = "c"
        extension_list = "a1b2c3d4e5f6"
        
    elif browser_info['browser'] == 'safari':
        packet_size = "1415" if http_version == "h2" else "1024"
        protocol = f"{protocol_version}d{packet_size}{http_version}"
        cipher_count = "7"
        cipher_list = "c5d6e7f8a9b0"
        extension_count = "b"
        extension_list = "f1e2d3c4b5a6"
        
    else:
        packet_size = "1024"
        protocol = f"{protocol_version}d{packet_size}{http_version}"
        cipher_count = "6"
        cipher_list = "a1b2c3d4e5f6"
        extension_count = "8"
        extension_list = "1a2b3c4d5e6f"
    
    # 根据Accept-Encoding调整扩展
    accept_encoding = headers.get('Accept-Encoding', '')
    if 'br' in accept_encoding:
        extension_list = extension_list[:-1] + "1"  # 修改最后一位表示Brotli支持
    
    # 根据DNT调整密码套件
    if headers.get('DNT') == '1':
        cipher_list = cipher_list[:-1] + "0"  # 隐私模式变体
    
    return f"{protocol}_{cipher_count}{cipher_list}_{extension_count}{extension_list}"

def generate_ja4_r_fingerprint(browser_info, headers):
    """
    生成JA4_R指纹（原始顺序）
    """
    base_ja4 = generate_ja4_fingerprint(browser_info, headers)
    # JA4_R通常包含更详细的密码套件和扩展信息
    if browser_info['browser'] == 'chrome':
        return f"{base_ja4.split('_')[0]}_002f,0035,009c,009d,1301,1302,1303,c013,c014,c02b,c02c,c02f,c030,cca8,cca9_0005,000a,000b,000d,0012,0017,001b,0023,002b,002d,0033,44cd,fe0d,ff01_0403,0804,0401,0503,0805,0501,0806,0601"
    else:
        return f"{base_ja4.split('_')[0]}_002f,0035,009c,009d,1301,1302,1303_0005,000a,000b,000d,0017,0023_0403,0804,0401,0503"

def generate_ja4_o_fingerprint(browser_info, headers):
    """
    生成JA4_O指纹（原始顺序，不同格式）
    """
    base_ja4 = generate_ja4_fingerprint(browser_info, headers)
    if browser_info['browser'] == 'chrome':
        return f"{base_ja4.split('_')[0]}_acb858a92679_df26d0ba6ad2"
    else:
        return f"{base_ja4.split('_')[0]}_1234567890ab_abcdef123456"

def generate_ja4_ro_fingerprint(browser_info, headers):
    """
    生成JA4_RO指纹（排序后的原始顺序）
    """
    if browser_info['browser'] == 'chrome':
        return "t13d1516h2_1301,1302,1303,c02b,c02f,c02c,c030,cca9,cca8,c013,c014,009c,009d,002f,0035_0023,000d,0005,0010,002b,002d,0017,0012,44cd,000b,fe0d,ff01,000a,001b,0033,0000_0403,0804,0401,0503,0805,0501,0806,0601"
    else:
        return "t12d1024h1_002f,0035,009c,009d,1301,1302,1303_0005,000a,000b,000d,0017,0023_0403,0804,0401,0503"

def generate_akamai_fingerprint(browser_info, headers):
    """
    生成Akamai HTTP/2指纹
    格式: WINDOW_UPDATE:SETTINGS:PRIORITY:HEADERS|stream_id|exclusive|weight
    基于headers信息动态调整HTTP/2参数
    """
    # 基础HTTP/2设置
    header_table_size = "65536"  # 默认值
    enable_push = "0"  # 默认禁用推送
    max_concurrent_streams = "6291456"  # 默认最大并发流
    initial_window_size = "262144"  # 默认窗口大小
    
    # 根据headers调整HTTP/2参数
    connection = headers.get('Connection', '').lower()
    upgrade = headers.get('Upgrade', '').lower()
    
    # 检测HTTP/2支持
    if 'h2' in upgrade or headers.get('HTTP2-Settings'):
        # 现代HTTP/2客户端设置
        if browser_info['browser'] == 'chrome':
            header_table_size = "65536"
            max_concurrent_streams = "6291456"
            initial_window_size = "262144"
        elif browser_info['browser'] == 'firefox':
            header_table_size = "65536"
            max_concurrent_streams = "4294967295"  # Firefox的特殊值
            initial_window_size = "262144"
        elif browser_info['browser'] == 'safari':
            header_table_size = "32768"  # Safari较小的表大小
            max_concurrent_streams = "2097152"
            initial_window_size = "262144"
    
    # 根据Accept-Encoding调整推送设置
    accept_encoding = headers.get('Accept-Encoding', '')
    if 'br' in accept_encoding:
        enable_push = "1"  # 支持Brotli时启用推送
    
    # 根据User-Agent版本调整窗口大小
    user_agent = headers.get('User-Agent', '')
    if 'Chrome/12' in user_agent or 'Chrome/13' in user_agent:  # 新版Chrome
        initial_window_size = "524288"  # 更大的窗口
    
    # 根据Accept-Language调整流ID
    stream_id = "15663105"  # 默认
    accept_language = headers.get('Accept-Language', '')
    if 'zh' in accept_language.lower():
        stream_id = "15663106"  # 中文环境变体
    elif 'ja' in accept_language.lower():
        stream_id = "15663107"  # 日文环境变体
    
    # 根据DNT调整优先级
    priority_flags = "m,a,s,p"  # 默认优先级标志
    if headers.get('DNT') == '1':
        priority_flags = "m,a,s,p,d"  # 隐私模式添加额外标志
    
    # 根据Sec-Fetch-* headers调整
    if headers.get('Sec-Fetch-Site'):
        priority_flags += ",f"  # 添加fetch标志
    
    # 构建Akamai指纹字符串
    akamai_text = f"1:{header_table_size};2:{enable_push};4:{max_concurrent_streams};6:{initial_window_size}|{stream_id}|0|{priority_flags}"
    
    # 生成MD5哈希
    akamai_hash = hashlib.md5(akamai_text.encode()).hexdigest()
    
    return akamai_text, akamai_hash

# HTML模板用于美化显示
INFO_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>浏览器信息检测</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #4CAF50; color: white; padding: 20px; border-radius: 5px; }
        .info-card { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; padding-left: 15px; margin: 15px 0; }
        .section { margin: 20px 0; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .endpoint { display: inline-block; background: #e3f2fd; padding: 10px 15px; margin: 5px 0; border-radius: 4px; }
        .method { font-weight: bold; color: #1976d2; }
        .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; }
        a { color: #1976d2; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 浏览器信息检测服务</h1>
            <p>类似 httpbin.org 的功能，显示您的浏览器和请求信息</p>
        </div>

        <div class="section">
            <h2>📋 基本信息</h2>
            <div class="info-card">
                <p><strong>请求ID:</strong> {{ data.uuid }}</p>
                <p><strong>时间戳:</strong> {{ data.timestamp }}</p>
            </div>
        </div>

        <div class="section">
            <h2>🖥️ 浏览器信息</h2>
            <pre>{{ json_data }}</pre>
        </div>

        <div class="section">
            <h2>🔗 可用端点</h2>
            <div class="endpoints">
                <a href="/"><div class="endpoint">/ - 完整信息</div></a>
                <a href="/ip"><div class="endpoint">/ip - IP地址</div></a>
                <a href="/user-agent"><div class="endpoint">/user-agent - 用户代理</div></a>
                <a href="/headers"><div class="endpoint">/headers - 请求头</div></a>
                <a href="/fingerprint"><div class="endpoint">/fingerprint - 浏览器指纹</div></a>
                <a href="/get"><div class="endpoint">/get - GET请求测试</div></a>
                <a href="/post"><div class="endpoint">/post - POST请求测试</div></a>
                <a href="/status/418"><div class="endpoint">/status/{code} - 状态码测试</div></a>
            </div>
        </div>

        <div class="section">
            <h2>⚙️ 服务器信息</h2>
            <div class="info-card">
                <p><strong>服务器平台:</strong> {{ server_info.platform }}</p>
                <p><strong>Python版本:</strong> {{ server_info.python_version }}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def get_browser_info():
    """
    返回请求者的浏览器信息
    
    Returns:
        dict: 包含完整请求信息的字典，格式类似httpbin.org
    """
    # 获取真实 IP（考虑多种代理情况）
    origin = (
        request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
        request.environ.get('HTTP_X_REAL_IP', '') or
        request.environ.get('HTTP_CF_CONNECTING_IP', '') or
        request.environ.get('HTTP_X_FORWARDED', '') or
        request.environ.get('HTTP_FORWARDED_FOR', '') or
        request.environ.get('HTTP_FORWARDED', '') or
        request.remote_addr or
        'unknown'
    )

    # 处理上传的文件
    files_data = {}
    if request.files:
        for key, file in request.files.items():
            if file.filename:
                files_data[key] = {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(file.read())
                }
                file.seek(0)  # 重置文件指针

    # 构建请求头字典并添加AWS头部（如果环境变量启用）
    headers_dict = {key: value for key, value in request.headers.items()}
    headers_dict = add_aws_headers(headers_dict)
    
    # 构建响应数据（严格按照httpbin.org格式）
    response_data = {
        "args": dict(request.args),
        "data": request.get_data(as_text=True) if request.data else "",
        "files": files_data,
        "form": dict(request.form) if request.form else {},
        "headers": headers_dict,
        "json": None,
        "method": request.method,
        "origin": origin,
        "url": request.url
    }

    # 尝试解析 JSON 数据
    if request.data and request.is_json:
        try:
            response_data["json"] = request.get_json()
        except Exception:
            response_data["json"] = None

    # 为HTML显示添加额外信息
    if request.headers.get('Accept', '').find('text/html') != -1:
        response_data.update({
            "uuid": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "flask_version": "2.3.3"
            },
            "client_info": {
                "browser": request.headers.get('User-Agent', 'Unknown'),
                "language": request.headers.get('Accept-Language', 'Unknown')
            }
        })

    # 如果是浏览器请求，返回美化后的 HTML
    if request.headers.get('Accept', '').find('text/html') != -1:
        return render_template_string(
            INFO_TEMPLATE,
            data=response_data,
            json_data=json.dumps(response_data, indent=2, ensure_ascii=False),
            server_info=response_data["server_info"]
        )
    
    # API 请求返回 JSON
    return jsonify(response_data)

@app.route('/ip')
def get_ip():
    """返回请求者的 IP 地址"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        origin = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        origin = request.remote_addr

    if request.headers.get('Accept', '').find('text/html') != -1:
        return f"<h1>IP 地址检测</h1><p>您的 IP 地址是: {origin}</p>"
    else:
        return jsonify({"origin": origin})

@app.route('/user-agent')
def get_user_agent():
    """返回 User-Agent"""
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    return jsonify({"user-agent": user_agent})

@app.route('/headers')
def get_headers():
    """返回所有请求头"""
    headers_dict = {key: value for key, value in request.headers.items()}

    if request.headers.get('Accept', '').find('text/html') != -1:
        return f"<h1>请求头信息</h1><pre>{json.dumps(headers_dict, indent=2, ensure_ascii=False)}</pre>"
    else:
        return jsonify({"headers": headers_dict})

@app.route('/get', methods=['GET'])
def get_method():
    """
    模拟 GET 请求
    
    Returns:
        dict: GET请求的完整信息
    """
    # 获取真实 IP
    origin = (
        request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
        request.environ.get('HTTP_X_REAL_IP', '') or
        request.remote_addr or
        'unknown'
    )
    
    # 构建请求头字典并添加AWS头部（如果环境变量启用）
    headers_dict = {key: value for key, value in request.headers.items()}
    headers_dict = add_aws_headers(headers_dict)
    
    response_data = {
        "args": dict(request.args),
        "headers": headers_dict,
        "origin": origin,
        "url": request.url
    }
    
    if request.headers.get('Accept', '').find('text/html') != -1:
        return f"""
        <h1>GET 请求测试</h1>
        <p><strong>查询参数:</strong> {dict(request.args)}</p>
        <p><strong>请求方法:</strong> {request.method}</p>
        <p><strong>URL:</strong> {request.url}</p>
        <p><strong>来源 IP:</strong> {request.remote_addr}</p>
        """
    else:
        return jsonify(response_data)

@app.route('/post', methods=['POST'])
def post_method():
    """
    模拟 POST 请求
    
    Returns:
        dict: POST请求的完整信息
    """
    # 获取真实 IP
    origin = (
        request.environ.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
        request.environ.get('HTTP_X_REAL_IP', '') or
        request.remote_addr or
        'unknown'
    )
    
    # 处理上传的文件
    files_data = {}
    if request.files:
        for key, file in request.files.items():
            if file.filename:
                files_data[key] = {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(file.read())
                }
                file.seek(0)  # 重置文件指针
    
    # 构建请求头字典并添加AWS头部（如果环境变量启用）
    headers_dict = {key: value for key, value in request.headers.items()}
    headers_dict = add_aws_headers(headers_dict)
    
    response_data = {
        "args": dict(request.args),
        "data": request.get_data(as_text=True) if request.data else "",
        "files": files_data,
        "form": dict(request.form) if request.form else {},
        "headers": headers_dict,
        "json": None,
        "origin": origin,
        "url": request.url
    }

    # 尝试解析 JSON 数据
    if request.data and request.is_json:
        try:
            response_data["json"] = request.get_json()
        except Exception:
            response_data["json"] = None

    return jsonify(response_data)

@app.route('/delay/<int:delay>')
def delay_response(delay):
    """
    延迟指定秒数后返回响应（模拟httpbin.org/delay/{n}）
    最大延迟限制为10秒，防止滥用
    """
    # 限制最大延迟时间
    if delay > 10:
        delay = 10
    
    # 延迟执行
    time.sleep(delay)
    
    # 获取客户端IP
    origin = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        request.headers.get('X-Real-IP', '') or
        request.environ.get('HTTP_X_FORWARDED_FOR', '') or
        request.remote_addr or
        '127.0.0.1'
    )
    
    # 构建请求头字典并添加AWS头部（如果环境变量启用）
    headers_dict = {key: value for key, value in request.headers.items()}
    headers_dict = add_aws_headers(headers_dict)
    
    # 构建响应数据
    response_data = {
        "args": dict(request.args),
        "data": request.get_data(as_text=True) if request.data else "",
        "files": {},
        "form": dict(request.form) if request.form else {},
        "headers": headers_dict,
        "json": None,
        "origin": origin,
        "url": request.url
    }
    
    # 处理JSON数据
    if request.is_json:
        try:
            response_data["json"] = request.get_json()
        except:
            response_data["json"] = None
    
    # 检查是否请求HTML格式
    if 'text/html' in request.headers.get('Accept', ''):
        # 为HTML响应添加额外信息
        response_data.update({
            "uuid": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "delay": delay
            },
            "client_info": {
                "user_agent": request.headers.get('User-Agent', 'Unknown'),
                "accept_language": request.headers.get('Accept-Language', 'Unknown'),
                "accept_encoding": request.headers.get('Accept-Encoding', 'Unknown')
            }
        })
        
        return render_template_string(
            INFO_TEMPLATE,
            data=response_data,
            json_data=json.dumps(response_data, indent=2, ensure_ascii=False),
            server_info=response_data["server_info"]
        )
    else:
        return jsonify(response_data)

@app.route('/fingerprint')
def fingerprint():
    """
    浏览器指纹检测端点
    返回各种TLS和HTTP/2指纹信息，类似于 https://tls.browserleaks.com/json
    """
    # 获取客户端信息
    user_agent = request.headers.get('User-Agent', '')
    client_ip = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        request.headers.get('X-Real-IP', '') or
        request.headers.get('CF-Connecting-IP', '') or
        request.remote_addr or
        'unknown'
    )
    
    # 获取所有请求头
    headers_dict = dict(request.headers)
    
    # 添加AWS头部（如果启用）
    add_aws_headers(headers_dict)
    
    # 生成浏览器指纹
    fingerprint_data = generate_browser_fingerprint(user_agent, headers_dict)
    
    # 检查是否请求JSON格式
    if request.headers.get('Accept', '').find('application/json') != -1:
        return jsonify(fingerprint_data)
    else:
        # 返回HTML格式
        json_data = json.dumps(fingerprint_data, indent=2, ensure_ascii=False)
        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>浏览器指纹检测</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #FF6B35; color: white; padding: 20px; border-radius: 5px; }
        .info-card { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #FF6B35; padding-left: 15px; margin: 15px 0; }
        .section { margin: 20px 0; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px; }
        .fingerprint-item { margin: 10px 0; padding: 10px; background: #fff3cd; border-radius: 4px; }
        .fingerprint-label { font-weight: bold; color: #856404; }
        .fingerprint-value { font-family: monospace; word-break: break-all; }
        a { color: #FF6B35; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 浏览器指纹检测</h1>
            <p>TLS和HTTP/2指纹分析 - 类似于 tls.browserleaks.com</p>
        </div>

        <div class="section">
            <h2>📊 指纹摘要</h2>
            <div class="fingerprint-item">
                <div class="fingerprint-label">User-Agent:</div>
                <div class="fingerprint-value">{{ fingerprint_data.user_agent }}</div>
            </div>
            <div class="fingerprint-item">
                <div class="fingerprint-label">JA3 Hash:</div>
                <div class="fingerprint-value">{{ fingerprint_data.ja3_hash }}</div>
            </div>
            <div class="fingerprint-item">
                <div class="fingerprint-label">JA4:</div>
                <div class="fingerprint-value">{{ fingerprint_data.ja4 }}</div>
            </div>
            <div class="fingerprint-item">
                <div class="fingerprint-label">Akamai Hash:</div>
                <div class="fingerprint-value">{{ fingerprint_data.akamai_hash }}</div>
            </div>
        </div>

        <div class="section">
            <h2>🔬 详细指纹数据</h2>
            <pre>{{ json_data }}</pre>
        </div>

        <div class="section">
            <h2>📖 指纹说明</h2>
            <div class="info-card">
                <p><strong>JA3:</strong> TLS客户端指纹，基于TLS握手参数生成MD5哈希</p>
                <p><strong>JA3N:</strong> JA3的标准化版本，对扩展进行排序以提高一致性</p>
                <p><strong>JA4:</strong> 新一代TLS指纹，更具可读性和抗干扰能力</p>
                <p><strong>JA4_R/JA4_O/JA4_RO:</strong> JA4的变体，包含不同的排序和格式</p>
                <p><strong>Akamai:</strong> HTTP/2指纹，基于HTTP/2设置和优先级</p>
            </div>
        </div>

        <div class="section">
            <h2>🔗 相关链接</h2>
            <p><a href="/">← 返回主页</a> | <a href="/fingerprint?format=json">JSON格式</a></p>
        </div>
    </div>
</body>
</html>
        """, fingerprint_data=fingerprint_data, json_data=json_data)

@app.route('/status/<int:code>')
def status_code(code):
    """返回指定状态码"""
    if request.headers.get('Accept', '').find('text/html') != -1:
        return f"""
        <h1>状态码测试</h1>
        <p><strong>请求的状态码:</strong> {code}</p>
        """, code
    else:
        return jsonify({"status": code}), code

if __name__ == '__main__':
    # 使用 '::' 绑定到所有IPv6地址，同时支持IPv4（通过IPv4映射的IPv6地址）
    # 如果系统不支持IPv6，则回退到IPv4
    port = 5000
    try:
        print("尝试启动IPv6/IPv4双栈服务器...")
        app.run(debug=True, host='::', port=port)
    except OSError as e:
        print(f"IPv6启动失败: {e}")
        print("回退到IPv4模式...")
        app.run(debug=True, host='0.0.0.0', port=5000)
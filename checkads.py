import requests

def convert_string_to_json_cookies(cookies):
    cookies = cookies.replace(" ","")
    list_cookies = cookies.split(";")
    json_cookies = {}
    for cookie in list_cookies:
        if cookie:
            cut_cookie = cookie.split("=")
            if len(cut_cookie) >= 2:
                key, value = cut_cookie[0], cut_cookie[1]
                json_cookies[key] = value
    return json_cookies

cookies = convert_string_to_json_cookies("YOUR-COOKIE-FACEBOOK-HERE")

def cut_string(key, data, option):
    index = data.find(key)
    if index == -1:
        return None
    if option:
        return data[index + len(key):]
    else:
        return data[:index]

def getFullNameFromCookies(cookies, uid):
    url = f"https://mbasic.facebook.com/{uid}"
    p = requests.get(url, cookies=cookies)
    resp = p.text
    start = resp.find("<head><title>") + len("<head><title>")
    end = resp.find("</title>", start)
    if start != -1 and end != -1:
        full_name = resp[start:end]
        return full_name.strip()
    return None

def get_fb_dtsg(cookies):
    url = "https://facebook.com"
    p = requests.get(url, cookies=cookies)
    data = p.text
    key = '["DTSGInitialData",[],{"token":"'
    data = cut_string(key, data, True)
    return cut_string('"', data, False) if data else None

def getUrlCamp(cookies):
    url = "https://adsmanager.facebook.com/adsmanager/manage/campaigns"
    p = requests.get(url, cookies=cookies)
    html = p.text
    textcut = 'https:\\/\\/adsmanager.facebook.com\\/adsmanager\\/manage\\/campaigns?act='
    redirect_url = cut_string(textcut, html, True)
    if redirect_url:
        redirect_url = cut_string('"', redirect_url, False)
        return (textcut + redirect_url).replace("\\/", "/")
    return None

def getAccessTokenNoFullAccess(cookies):
    try:
        url = getUrlCamp(cookies)
        if url:
            p = requests.get(url, cookies=cookies)
            html = p.text
            resp = cut_string('__accessToken="', html, True)
            return cut_string('"', resp, False) if resp else None
        return None
    except Exception as e:
        raise e

def getAccountId(cookies):
    url = "https://adsmanager.facebook.com/adsmanager/manage/campaigns"
    p = requests.get(url, cookies=cookies)
    html = p.text
    textcut = 'https:\\/\\/adsmanager.facebook.com\\/adsmanager\\/manage\\/campaigns?act='
    id_acc = cut_string(textcut, html, True)
    return cut_string('&', id_acc, False) if id_acc else None

def getInfoAdsApi(cookies):
    accessToken = getAccessTokenNoFullAccess(cookies)
    id_acc = getAccountId(cookies)
    if accessToken and id_acc:
        url = f"https://graph.facebook.com/v15.0/act_{id_acc}?fields=account_id%2Cname%2Caccount_status%2Ccurrency%2Cadtrust_dsl%2Cbusiness_country_code%2Cadspaymentcycle%7Bthreshold_amount%7D%2Cbalance%2Cinsights.date_preset(maximum)%7Bspend%7D&access_token={accessToken}"
        p = requests.get(url, cookies=cookies)
        data = p.json()
        info_ads = {
            'ads_id': data.get('account_id'),
            'ads_name': data.get('name'),
            'account_status': data.get('account_status'),
            'country': data.get('business_country_code'),
            'currency': data.get('currency'),
            'balance': data.get('balance'),
            'spending_limit': data.get('adtrust_dsl'),
            'threshold_amount': None,
            'total_spending': None
        }

        if 'adspaymentcycle' in data and data['adspaymentcycle']:
            info_ads['threshold_amount'] = data['adspaymentcycle'][0].get('threshold_amount')

        if 'insights' in data and data['insights']:
            info_ads['total_spending'] = data['insights']['data'][0].get('spend')
            
        return info_ads
    return None

print(getInfoAdsApi(cookies))

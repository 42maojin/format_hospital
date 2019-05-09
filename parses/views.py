import datetime, re
import pandas as pd
from django_pandas.io import read_frame
from django.shortcuts import render,redirect
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from parses import models
from .forms import UploadFileForm
from .models import KWD, PKT, CONSUMPTION_GC,CONSUMPTION_WC, File_Name
import json
from django.core.paginator import Paginator
# Create your views here.
def readFile(filename, chunk_size=512):
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def talk_type(var):
    if var == '客人无讯息':
        var = 0
        return var
    else:
        var = 1
        return var


def formats(var):
    var['dia_type'] = var['dia_type'].apply(talk_type)
    var['毛咨询'] = 1
    var["五句"] = var.apply(lambda x: fives(int(x.guest_num), int(x.service_num)), axis=1)
    del var['guest_num']
    del var['service_num']
    var.rename(columns={'dia_type': '有效对话'}, inplace=True)
    return var


def sort_consum(data):
    data = data.sort_values(by='consumption', ascending=False)
    return data


def fives(a, b):
    if a >= 5 and b >= 5:
        return 1
    else:
        return 0


# 初次清理着陆页 = 肛肠
def regex(urls):
    url = str(urls)
    if '//ada.baidu' and 'imid=' and 'utm_source=' and "&utm_source" and "&bd_vid" in url:
        if len(re.findall(
                "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+&utm_source=[0-9a-z]+&\d+).*?",
                url)) >= 1:
            data = re.findall(
                "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&utm_source=[0-9a-z]+&\d+.*?",
                url)
            return data[0]
        else:
            return None
    else:
        return None


# 初次清理着陆页 = 胃肠
def regex_wc(urls):
    url = str(urls)
    if '//ada.baidu' and 'imid=' and 'utm_source=' and "&utm_source" and "&bd_vid" in url:
        if len(re.findall(
                "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+&utm_source=[0-9a-z]+&\d+).*?",
                url)) >= 1:
            data = re.findall(
                "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&utm_source=[0-9a-z]+&\d+.*?",
                url)
            # "https://ada.baidu.com/site/0755gck.com/xyl?imid=a63e433f1df3b3ae98a59adefb7a4281&source=bdm14&120012387616"
            return data[0]

        else:
            return None

    else:
        return None


def regex_url(url):
    if len(re.findall(
            "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&utm_source=[0-9a-z]+&\d+",
            url)) >= 1:
        data = re.findall(
            "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&utm_source=[0-9a-z]+&\d+",
            url)
        return data[0]


def regex_url_wc(urls):
    if len(re.findall(
            "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&[a-z_]+=[0-9a-z]+&\d+",
            urls)) >= 1:
        data = re.findall(
            "(https://ada\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&[a-z_]+=[0-9a-z]+&\d+", urls)
        return data[0]


def regex_id(id):
    # data = re.findall("(https://ada\.baidu\.com/site/ydgcyy\.net/xyl\?imid=[a-z0-9]+&utm_source=[0-9a-z]+&\d+).*?", id)
    id = str(id)
    if len(re.findall("https://ada\.baidu\.com/site/[a-z0-9]+\.[net|com]+/xyl\?imid=[a-z0-9]+&utm_source=[0-9a-z]+&(\d+)",id)) >= 1:
        result = re.findall("https://ada\.baidu\.com/site/[a-z0-9]+\.[net|com]+/xyl\?imid=[a-z0-9]+&utm_source=[0-9a-z]+&(\d+)",id)
        return result[0]
    else:
        return None


def regex_id_wc(id):
    id = str(id)
    if len(re.findall("https://ada\.baidu\.com/site/[a-z0-9]+\.[net|com]+/xyl\?imid=[a-z0-9]+&[a-z_]+=[0-9a-z]+&(\d+)",id)) >= 1:
        result = re.findall("https://ada\.baidu\.com/site/[a-z0-9]+\.[net|com]+/xyl\?imid=[a-z0-9]+&[a-z_]+=[0-9a-z]+&(\d+)", id)
        return result[0]
    else:
        return None


def statistics(var):
    var['毛/点'] = var['毛咨询'] / var['click_num']
    var['毛/点'] = var['毛/点'].apply(lambda x: str(round(x * 100, 2)) + "%")
    var['有效点击比'] = var['有效对话'] / var['click_num']
    var['有效点击比'] = var['有效点击比'].apply(lambda x: str(round(x * 100, 2)) + "%")
    var['对话成本'] = round(var['consumption'] / var['有效对话'], 1)
    # var['对话成本']=var['对话成本'].apply(lambda x:)
    return var


# 额外的

def regex_extra(urls):
    url = str(urls)
    if 'baidu' and 'imid=' and "source" and "&bd_vid" in url:
        if len(re.findall(
                "(https://[a-z]+\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+&[a-z_]+=[0-9a-z]+&\d+).*?",
                url)) >= 1:
            # data = re.findall("(https://[a-z]+\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&[a-z_]+=[0-9a-z]+&\d+.*?",url)
            return None
        else:
            return 1
    else:
        if "baidu" in url:
            return 1
        else:
            return None


def regex_extra_wc(urls):
    url = str(urls)
    if 'baidu' and 'imid=' and "source" and "&bd_vid" in url:
        if len(re.findall(
                "(https://[a-z]+\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+&[a-z_]+=[0-9a-z]+&\d+).*?",
                url)) >= 1:
            # data = re.findall("(https://[a-z]+\.baidu\.com/site/[0-9a-z]+\.[net|com]+/xyl\?imid=[a-z0-9]+)&[a-z_]+=[0-9a-z]+&\d+.*?",url)
            return None
        else:
            return 1
    else:
        if "baidu" in url:
            return 1
        else:
            return None


def regex_customer(var):
    if "推广账户ID" in str(var):
        data = re.findall("(\d{6,10})", str(var))
        if len(data) >= 0:
            return data[0]
        else:
            return 0
    else:
        return 0


def extra(var):
    for x in number_account.items():
        if var == x[0]:
            # print(x[0])
            return x[1]


def customer(var, var1):
    if regex_extra(var) is not None and regex_customer(var1) is not 0:
        return regex_customer(var1)
    else:
        return 0


date_name = "0"  # 全局变量
number_account = {"7678624": "深圳远大肛肠医院03", "1376286": "ydgcyy", "3828965": "szydgc", "10375830": "远大肛肠医院13",
                  "10375815": "远大肛肠医院12", "7278015": "远大肛肠医院03", "10375827": "远大肛肠医院10", "10375851": "远大肛肠医院15",
                  "10375846": "远大肛肠医院14", "10375804": "远大肛肠医院08", "10375788": "远大肛肠医院07", "3803609": "湛江东大肛肠",
                  "7507249": "湛江东大肛肠医院", "7508391": "湛江东大肛肠医院01"}


def index(request):
    t = datetime.datetime.now()
    # 文件上传
    print("====", request.method)

    if request.is_ajax():
        try:
            print("进来了")
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                return render(request, '404.html')
            else:

                files = request.FILES.getlist('file')
                print(files[0].name)
                print(type(files))
                for f in files:
                    result = models.File_Name.objects.filter(files_name=f.name).exists()
                    if result:
                        b = {'name': 'nick', 'age': 12}
                        return JsonResponse(b)
                    else:
                        if "xls" in str(f):
                            if "KWD" in str(f):
                                data = pd.DataFrame(pd.read_excel(f))
                                # print(data)

                                df = data.drop(0).drop(1)  # 加上head() 取前五行
                                columns = ['编号', '开始访问时间', '开始对话时间', '对话时长', '对话类型', '开始方式', '结束方式',
                                           '客人讯息数', '客服讯息数', '名称', '参与接待客服', '客人类别', '操作系统', '永久身份',
                                           '对话来源', '访问来源', '初次访问网址', '客人说明', '关键词', 'IP定位', '初始接待客服',
                                           '分辨率', '参与邀请客服', '本次访问页数']
                                df.columns = columns
                                # df.to_excel("df.xlsx", index=False)
                                # df["客人说明"]="0"
                                # df["关键词"]="0"
                                df["file_name_kwd"] = f.name
                                file_name_kwd = list(df["file_name_kwd"])
                                u_number = list(df["编号"])
                                start_visit_time = list(df["开始访问时间"])
                                start_dia_time = list(df["开始对话时间"])
                                dia_time = list(df["对话时长"])
                                dia_type = list(df["对话类型"])
                                start_func = list(df["开始方式"])
                                end_func = list(df["结束方式"])
                                guest_num = list(df["客人讯息数"])
                                service_num = list(df["客服讯息数"])
                                name = list(df["名称"])
                                join_service = list(df["参与接待客服"])
                                guest_type = list(df["客人类别"])

                                operating_system = list(df["操作系统"])
                                u_id = list(df["永久身份"])
                                dia_source = list(df["对话来源"])
                                visit_source_url = list(df["访问来源"])
                                first_visit_url = list(df["初次访问网址"])
                                guest_desc = list(df["客人说明"])
                                print("number : ", len(guest_desc))
                                print("number:", len(start_visit_time))
                                key_word = list(df["关键词"])
                                ip_location = list(df['IP定位'])
                                first_service_guest = list(df['初始接待客服'])
                                resolution = list(df['分辨率'])
                                join_invite = list(df["参与邀请客服"])
                                visit_page = list(df["本次访问页数"])
                                a = pd.DataFrame({"A": guest_desc})

                                kwd_list = []
                                for i in range(len(start_visit_time)):
                                    # print("---", i)
                                    file_name_kwds = file_name_kwd[i]
                                    u_numbers = int(u_number[i])
                                    start_visit_times = datetime.datetime.strptime(start_visit_time[i],
                                                                                   '%Y-%m-%d %H:%M:%S')
                                    start_dia_times = datetime.datetime.strptime(start_dia_time[i], '%Y-%m-%d %H:%M:%S')
                                    dia_times = dia_time[i]
                                    dia_types = dia_type[i]
                                    start_funcs = start_func[i]
                                    end_funcs = end_func[i]
                                    guest_nums = int(guest_num[i])
                                    service_nums = int(service_num[i])
                                    names = name[i]
                                    join_services = join_service[i]
                                    guest_types = guest_type[i]
                                    operating_systems = operating_system[i]
                                    u_ids = u_id[i]
                                    dia_sources = dia_source[i]
                                    visit_source_urls = visit_source_url[i]
                                    first_visit_urls = first_visit_url[i]
                                    guest_descs = guest_desc[i]
                                    key_words = key_word[i]
                                    ip_locations = ip_location[i]
                                    first_service_guests = first_service_guest[i]
                                    resolutions = resolution[i]
                                    join_invites = join_invite[i]
                                    visit_pages = visit_page[i]

                                    kwd_list.append(
                                        KWD(file_name_kwd=file_name_kwds, u_number=u_numbers,
                                            start_visit_time=start_visit_times,
                                            start_dia_time=start_dia_times,
                                            dia_time=dia_times, dia_type=dia_types, start_func=start_funcs,
                                            end_func=end_funcs,
                                            guest_num=guest_nums, service_num=service_nums, name=names,
                                            join_service=join_services,
                                            guest_type=guest_types, operating_system=operating_systems, u_id=u_ids,
                                            dia_source=dia_sources, visit_source_url=visit_source_urls,
                                            first_visit_url=first_visit_urls, guest_desc=guest_descs,
                                            key_word=key_words,
                                            ip_location=ip_locations, first_service_guest=first_service_guests,
                                            resolution=resolutions, join_invite=join_invites, visit_page=visit_pages, ))

                                KWD.objects.bulk_create(kwd_list)  # 商务通数据入库
                                now = datetime.datetime.now()

                                models.File_Name.objects.create(files_name=f.name, create_time=now)
                                print("商务通上传数据成功")
                                print("ok")
                                print("花费时间:", datetime.datetime.now() - t)
                                b = {'name': 'nick', 'age': 12}
                                return JsonResponse(b)
                            if "PKT" in str(f):
                                data = pd.DataFrame(pd.read_excel(f))
                                # print(data)
                                df = data.drop(0).drop(1)  # 加上head() 取前五行
                                columns = ['编号', '开始访问时间', '开始对话时间', '对话时长', '对话类型', '开始方式', '结束方式',
                                           '客人讯息数', '客服讯息数', '名称', '参与接待客服', '客人类别', '操作系统', '永久身份',
                                           '对话来源', '访问来源', '初次访问网址', '客人说明', '关键词', 'IP定位', '初始接待客服',
                                           '分辨率', '参与邀请客服', '本次访问页数']
                                df.columns = columns
                                # df.to_excel("df.xlsx", index=False)
                                # df["客人说明"]="0"
                                # df["关键词"]="0"
                                df["file_name_pkt"] = f.name
                                file_name_pkt = list(df["file_name_pkt"])
                                u_number = list(df["编号"])
                                start_visit_time = list(df["开始访问时间"])
                                start_dia_time = list(df["开始对话时间"])
                                dia_time = list(df["对话时长"])
                                dia_type = list(df["对话类型"])
                                start_func = list(df["开始方式"])
                                end_func = list(df["结束方式"])
                                guest_num = list(df["客人讯息数"])
                                service_num = list(df["客服讯息数"])
                                name = list(df["名称"])
                                join_service = list(df["参与接待客服"])
                                guest_type = list(df["客人类别"])

                                operating_system = list(df["操作系统"])
                                u_id = list(df["永久身份"])
                                dia_source = list(df["对话来源"])
                                visit_source_url = list(df["访问来源"])
                                first_visit_url = list(df["初次访问网址"])
                                guest_desc = list(df["客人说明"])
                                print("number : ", len(guest_desc))
                                print("number:", len(start_visit_time))
                                key_word = list(df["关键词"])
                                ip_location = list(df['IP定位'])
                                first_service_guest = list(df['初始接待客服'])
                                resolution = list(df['分辨率'])
                                join_invite = list(df["参与邀请客服"])
                                visit_page = list(df["本次访问页数"])
                                a = pd.DataFrame({"A": guest_desc})

                                kwd_list = []
                                for i in range(len(start_visit_time)):
                                    # print("---", i)
                                    file_name_pkts = file_name_pkt[i]
                                    u_numbers = int(u_number[i])
                                    start_visit_times = datetime.datetime.strptime(start_visit_time[i],
                                                                                   '%Y-%m-%d %H:%M:%S')
                                    start_dia_times = datetime.datetime.strptime(start_dia_time[i], '%Y-%m-%d %H:%M:%S')
                                    dia_times = dia_time[i]
                                    dia_types = dia_type[i]
                                    start_funcs = start_func[i]
                                    end_funcs = end_func[i]
                                    guest_nums = int(guest_num[i])
                                    service_nums = int(service_num[i])
                                    names = name[i]
                                    join_services = join_service[i]
                                    guest_types = guest_type[i]
                                    operating_systems = operating_system[i]
                                    u_ids = u_id[i]
                                    dia_sources = dia_source[i]
                                    visit_source_urls = visit_source_url[i]
                                    first_visit_urls = first_visit_url[i]
                                    guest_descs = guest_desc[i]
                                    key_words = key_word[i]
                                    ip_locations = ip_location[i]
                                    first_service_guests = first_service_guest[i]
                                    resolutions = resolution[i]
                                    join_invites = join_invite[i]
                                    visit_pages = visit_page[i]

                                    kwd_list.append(
                                        PKT(file_name_pkt=file_name_pkts, u_number=u_numbers,
                                            start_visit_time=start_visit_times,
                                            start_dia_time=start_dia_times,
                                            dia_time=dia_times, dia_type=dia_types, start_func=start_funcs,
                                            end_func=end_funcs,
                                            guest_num=guest_nums, service_num=service_nums, name=names,
                                            join_service=join_services,
                                            guest_type=guest_types, operating_system=operating_systems, u_id=u_ids,
                                            dia_source=dia_sources, visit_source_url=visit_source_urls,
                                            first_visit_url=first_visit_urls, guest_desc=guest_descs,
                                            key_word=key_words,
                                            ip_location=ip_locations, first_service_guest=first_service_guests,
                                            resolution=resolutions, join_invite=join_invites, visit_page=visit_pages))

                                PKT.objects.bulk_create(kwd_list)  # 商务通数据入库
                                now = datetime.datetime.now()
                                models.File_Name.objects.create(files_name=f.name, create_time=now)
                                print("商务通上传数据成功")
                                print("ok")
                                print("花费时间:", datetime.datetime.now() - t)
                                b = {'name': 'nick', 'age': 12}
                                return JsonResponse(b)

                        if "csv" in str(f):

                            file_name = f.name
                            gc=models.ACCOUNT_GC.objects.filter(account_name=file_name.split("_")[0]).exists()
                            wc=models.ACCOUNT_WC.objects.filter(account_name=file_name.split("_")[0]).exists()
                            if gc:
                                print("file_name:", file_name)
                                try:
                                    if "_" in file_name:
                                        files = file_name.split("_")
                                        account = files[0]
                                        if files[-1].split(".")[0]:
                                            date = datetime.datetime.strptime(files[-1].split(".")[0],
                                                                              "%Y-%m-%d") + datetime.timedelta(days=-1)
                                    else:
                                        account = "admin"
                                        date = "2019-01-01"
                                except ImportError as e:
                                    print(e)
                                    return render(request, '404.html')
                                # print("account:",account)
                                data1 = pd.DataFrame(
                                    pd.read_csv(f, delimiter="\t", encoding='utf-16'))  # 以分隔符读取，用utf-16解码
                                # print(data1.columns)
                                data1["日期"] = date
                                data1["账户"] = account
                                data1["file_name_con"] = f.name
                                file_name_con = list(data1["file_name_con"])
                                file_date = list(data1["日期"])
                                file_account = list(data1["账户"])
                                plan_name = list(data1["推广计划名称"])  # 推广计划名称
                                unit_name = list(data1["推广单元名称"])  # 推广单元名称
                                key_word = list(data1["关键词名称"])  # 关键词名称
                                match_model = list(data1["匹配模式"])  # 匹配模式
                                bid = list(data1["出价"])  # 出价
                                visit_url = list(data1["访问URL"])  # 访问URL
                                mobile_visit_url = list(data1["移动访问URL"])  # 移动访问URL
                                start_or_stop = list(data1["启用/暂停"])  # 启用/暂停
                                label = list(data1["标签"])  # 标签
                                applet = list(data1["小程序URL"])  # 小程序URL
                                key_word_status = list(data1["关键词状态"])  # 关键词状态
                                computer_price = list(data1["计算机指导价"])  # 计算机指导价
                                computer_quality = list(data1["计算机质量度"])  # 计算机质量度
                                mobile_quality = list(data1["移动质量度"])  # 移动质量度
                                consumption = list(data1["消费"])  # 消费
                                avg_click_price = list(data1["平均点击价格"])  # 平均点击价格
                                click_num = list(data1["点击"])  # 点击
                                show = list(data1["展现"])  # 展现
                                click_rate = list(data1["点击率"])  # 点击率
                                page_conversion = list(data1["网页转化"])  # 网页转化
                                k_show_consumption = list(data1["千次展现消费"])  # 千次展现消费
                                avg_conversion_price = list(data1["平均转化价格"])  # 平均转化价格
                                conversion_word = list(data1["转化搜索词"])  # 转化搜索词

                                consumer_keyword_list = []
                                for j in range(len(plan_name)):
                                    file_name_cons = file_name_con[j]
                                    accounts = file_account[j]
                                    # datetime.datetime.strptime(start_time[i], '%Y-%m-%d %H:%M:%S')
                                    dates = file_date[j]
                                    # dates = datetime.datetime.strptime(file_date[j], '%Y-%m-%d')
                                    plan_names = plan_name[j]
                                    unit_names = unit_name[j]
                                    key_words = key_word[j]
                                    match_models = match_model[j]
                                    bids = float(bid[j])
                                    visit_urls = visit_url[j]
                                    mobile_visit_urls = mobile_visit_url[j]
                                    start_or_stops = start_or_stop[j]
                                    labels = label[j]
                                    applets = applet[j]
                                    key_word_statuss = key_word_status[j]
                                    computer_prices = computer_price[j]
                                    computer_qualitys = computer_quality[j]
                                    mobile_qualitys = mobile_quality[j]
                                    consumptions = float(consumption[j])
                                    avg_click_prices = float(avg_click_price[j])
                                    click_nums = int(click_num[j])
                                    shows = int(show[j])
                                    click_rates = click_rate[j]
                                    page_conversions = page_conversion[j]
                                    k_show_consumptions = k_show_consumption[j]
                                    avg_conversion_prices = avg_conversion_price[j]
                                    conversion_words = conversion_word[j]

                                    consumer_keyword_list.append(
                                        CONSUMPTION_GC(file_name_con=file_name_cons, account=accounts, date=dates,
                                                    plan_name=plan_names,
                                                    unit_name=unit_names,
                                                    key_word=key_words,
                                                    match_model=match_models, bid=bids, visit_url=visit_urls,
                                                    mobile_visit_url=mobile_visit_urls, start_or_stop=start_or_stops,
                                                    label=labels,
                                                    applet=applets, key_word_status=key_word_statuss,
                                                    computer_price=computer_prices, computer_quality=computer_qualitys,
                                                    mobile_quality=mobile_qualitys, consumption=consumptions,
                                                    avg_click_price=avg_click_prices, click_num=click_nums, show=shows,
                                                    click_rate=click_rates, page_conversion=page_conversions,
                                                    k_show_consumption=k_show_consumptions,
                                                    avg_conversion_price=avg_conversion_prices,
                                                    conversion_word=conversion_words
                                                    ))
                                CONSUMPTION_GC.objects.bulk_create(consumer_keyword_list)  # 消费表数据入库
                                now = datetime.datetime.now()
                                models.File_Name.objects.create(files_name=f.name, create_time=now)
                                print("消费表上传数据成功")
                                print("ok")
                                print("花费时间:", datetime.datetime.now() - t)
                                b = {'name': 'nick', 'age': 12}
                                return JsonResponse(b)
                            else:
                                render(request,'404.html')
                            if wc:
                                print("file_name:", file_name)
                                try:
                                    if "_" in file_name:
                                        files = file_name.split("_")
                                        account = files[0]
                                        if files[-1].split(".")[0]:
                                            date = datetime.datetime.strptime(files[-1].split(".")[0],
                                                                              "%Y-%m-%d") + datetime.timedelta(days=-1)
                                    else:
                                        account = "admin"
                                        date = "2019-01-01"
                                except ImportError as e:
                                    print(e)
                                    return render(request, '404.html')
                                # print("account:",account)
                                data1 = pd.DataFrame(
                                    pd.read_csv(f, delimiter="\t", encoding='utf-16'))  # 以分隔符读取，用utf-16解码
                                # print(data1.columns)
                                data1["日期"] = date
                                data1["账户"] = account
                                data1["file_name_con"] = f.name
                                file_name_con = list(data1["file_name_con"])
                                file_date = list(data1["日期"])
                                file_account = list(data1["账户"])
                                plan_name = list(data1["推广计划名称"])  # 推广计划名称
                                unit_name = list(data1["推广单元名称"])  # 推广单元名称
                                key_word = list(data1["关键词名称"])  # 关键词名称
                                match_model = list(data1["匹配模式"])  # 匹配模式
                                bid = list(data1["出价"])  # 出价
                                visit_url = list(data1["访问URL"])  # 访问URL
                                mobile_visit_url = list(data1["移动访问URL"])  # 移动访问URL
                                start_or_stop = list(data1["启用/暂停"])  # 启用/暂停
                                label = list(data1["标签"])  # 标签
                                applet = list(data1["小程序URL"])  # 小程序URL
                                key_word_status = list(data1["关键词状态"])  # 关键词状态
                                computer_price = list(data1["计算机指导价"])  # 计算机指导价
                                computer_quality = list(data1["计算机质量度"])  # 计算机质量度
                                mobile_quality = list(data1["移动质量度"])  # 移动质量度
                                consumption = list(data1["消费"])  # 消费
                                avg_click_price = list(data1["平均点击价格"])  # 平均点击价格
                                click_num = list(data1["点击"])  # 点击
                                show = list(data1["展现"])  # 展现
                                click_rate = list(data1["点击率"])  # 点击率
                                page_conversion = list(data1["网页转化"])  # 网页转化
                                k_show_consumption = list(data1["千次展现消费"])  # 千次展现消费
                                avg_conversion_price = list(data1["平均转化价格"])  # 平均转化价格
                                conversion_word = list(data1["转化搜索词"])  # 转化搜索词

                                consumer_keyword_list = []
                                for j in range(len(plan_name)):
                                    file_name_cons = file_name_con[j]
                                    accounts = file_account[j]
                                    # datetime.datetime.strptime(start_time[i], '%Y-%m-%d %H:%M:%S')
                                    dates = file_date[j]
                                    # dates = datetime.datetime.strptime(file_date[j], '%Y-%m-%d')
                                    plan_names = plan_name[j]
                                    unit_names = unit_name[j]
                                    key_words = key_word[j]
                                    match_models = match_model[j]
                                    bids = float(bid[j])
                                    visit_urls = visit_url[j]
                                    mobile_visit_urls = mobile_visit_url[j]
                                    start_or_stops = start_or_stop[j]
                                    labels = label[j]
                                    applets = applet[j]
                                    key_word_statuss = key_word_status[j]
                                    computer_prices = computer_price[j]
                                    computer_qualitys = computer_quality[j]
                                    mobile_qualitys = mobile_quality[j]
                                    consumptions = float(consumption[j])
                                    avg_click_prices = float(avg_click_price[j])
                                    click_nums = int(click_num[j])
                                    shows = int(show[j])
                                    click_rates = click_rate[j]
                                    page_conversions = page_conversion[j]
                                    k_show_consumptions = k_show_consumption[j]
                                    avg_conversion_prices = avg_conversion_price[j]
                                    conversion_words = conversion_word[j]

                                    consumer_keyword_list.append(
                                        CONSUMPTION_WC(file_name_con=file_name_cons, account=accounts, date=dates,
                                                    plan_name=plan_names,
                                                    unit_name=unit_names,
                                                    key_word=key_words,
                                                    match_model=match_models, bid=bids, visit_url=visit_urls,
                                                    mobile_visit_url=mobile_visit_urls, start_or_stop=start_or_stops,
                                                    label=labels,
                                                    applet=applets, key_word_status=key_word_statuss,
                                                    computer_price=computer_prices, computer_quality=computer_qualitys,
                                                    mobile_quality=mobile_qualitys, consumption=consumptions,
                                                    avg_click_price=avg_click_prices, click_num=click_nums, show=shows,
                                                    click_rate=click_rates, page_conversion=page_conversions,
                                                    k_show_consumption=k_show_consumptions,
                                                    avg_conversion_price=avg_conversion_prices,
                                                    conversion_word=conversion_words
                                                    ))
                                CONSUMPTION_WC.objects.bulk_create(consumer_keyword_list)  # 消费表数据入库
                                now = datetime.datetime.now()
                                models.File_Name.objects.create(files_name=f.name, create_time=now)
                                print("消费表上传数据成功")
                                print("ok")
                                print("花费时间:", datetime.datetime.now() - t)
                                b = {'name': 'nick', 'age': 12}
                                return JsonResponse(b)
                            else:
                                render(request, '404.html')
        except ImportError as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return render(request, '404.html')
    # 查询
    elif 'inquire' in request.POST:
        try:
            print("进来了1")
            date = request.POST.get('Date')  # 输入的查询日期
            global date_name
            date_name = date.replace(' ', '')
            print(date_name)
            # with open('file_name.txt', 'w') as f:
            #     f.write(date_name)
            date1 = date.split(" - ")[0]
            date2 = date.split(" - ")[1]
            k = models.KWD.objects.filter(start_visit_time__range=(date1 + " 00:00:00", date2 + " 23:59:59"))
            p = models.PKT.objects.filter(start_visit_time__range=(date1 + " 00:00:00", date2 + " 23:59:59"))

            # k = models.KWD.objects.filter(start_visit_time__range=(date1, date2))

            # ====================处理==================================================
            df_kwd = read_frame(k)
            # KWD-着陆页
            df1 = df_kwd[["dia_type", "guest_num", "service_num", "first_visit_url"]].copy()
            df1['first_visit_url'] = df1['first_visit_url'].apply(regex)
            # df1.to_excel("df1.xlsx")
            df_url = formats(df1).groupby(['first_visit_url'], as_index=False).sum()
            # df_url.to_excel("df_url.xlsx")
            df_url_k = df_url.rename(columns={"first_visit_url": "mobile_visit_url"})

            # CONSUMPTION - 着陆页
            gc = models.CONSUMPTION_GC.objects.filter(date__range=(date1, date2))


            df_consumption = read_frame(gc)
            df_url_c = df_consumption[["account", 'mobile_visit_url', 'consumption', 'click_num', 'show']].copy()
            df_url_c["mobile_visit_url"] = df_url_c["mobile_visit_url"].apply(regex_url)
            df_url_c1 = df_url_c.groupby(by=["account", "mobile_visit_url"], as_index=False).sum()
            # 着陆页合并
            url_columns = ["总计", "account", "mobile_visit_url", "consumption", "show", "click_num", "毛咨询", "有效对话", "五句",
                           "毛/点", "有效点击比", "对话成本"]
            data = pd.merge(df_url_k, df_url_c1, on="mobile_visit_url")
            # data.to_excel("data.xlsx")
            # ---------------------------------------------------
            df_extra = df_kwd[["dia_type", "first_visit_url", "guest_desc", "guest_num", "service_num"]].copy()
            df_extra["account"] = df_extra.apply(lambda x: customer(x.first_visit_url, x.guest_desc), axis=1)
            df_extra["guest_desc"] = df_extra["guest_desc"].apply(regex_customer)
            # df['初次访问网址'] = df['初次访问网址'].apply(regex_extra)
            df_extra_url = formats(df_extra).groupby(by="account", as_index=False).sum()
            df_extra_url["account"] = df_extra_url["account"].apply(extra)
            df_extra_url["consumption"] = 0
            df_extra_url["mobile_visit_url"] = "空白"
            df_extra_url["click_num"] = 0
            df_extra_url["show"] = 0

            extras = pd.concat([data, df_extra_url], sort=True)
            # extras.to_excel("extras.xlsx")
            # -----------------------------------------------------------------

            df_pro_url = extras.groupby(by=["account"], as_index=False).sum()
            df_pro_url["总计"] = "总计"
            url_data = pd.concat([extras, df_pro_url], sort=True)
            f_url = statistics(url_data).reindex(columns=url_columns).sort_values(by=["account", "consumption"],
                                                                                  ascending=False)
            # f_url.to_excel("f_url.xlsx")
            # ===================================================================================================================完成的着陆页
            df_P = read_frame(p)

            df1_wc = df_P[["dia_type", "guest_num", "service_num", "first_visit_url"]].copy()
            df1_wc['first_visit_url'] = df1_wc['first_visit_url'].apply(regex_wc)
            df_url_wc = formats(df1_wc).groupby(['first_visit_url'], as_index=False).sum()
            df_url_k_wc = df_url_wc.rename(columns={"first_visit_url": "mobile_visit_url"})

            # CONSUMPTION - 着陆页
            wc = models.CONSUMPTION_WC.objects.filter(date__range=(date1, date2))
            df_consumption_wc = read_frame(wc)
            df_url_c_wc = df_consumption_wc[["account", 'mobile_visit_url', 'consumption', 'click_num', 'show']].copy()
            df_url_c_wc["mobile_visit_url"] = df_url_c_wc["mobile_visit_url"].apply(regex_url_wc)
            df_url_c1_wc = df_url_c_wc.groupby(by=["account", "mobile_visit_url"], as_index=False).sum()
            # 着陆页合并
            url_columns = ["总计", "account", "mobile_visit_url", "consumption", "show", "click_num", "毛咨询", "有效对话", "五句",
                           "毛/点", "有效点击比", "对话成本"]
            data_wc = pd.merge(df_url_k_wc, df_url_c1_wc, on="mobile_visit_url")
            # 额外的--------------------------------------------------------------------------------
            df_extra_wc = df_P[["dia_type", "first_visit_url", "guest_desc", "guest_num", "service_num"]].copy()
            df_extra_wc["account"] = df_extra_wc.apply(lambda x: customer(x.first_visit_url, x.guest_desc), axis=1)
            df_extra_wc["guest_desc"] = df_extra_wc["guest_desc"].apply(regex_customer)
            # df['初次访问网址'] = df['初次访问网址'].apply(regex_extra)
            df_extra_wc_url = formats(df_extra_wc).groupby(by="account", as_index=False).sum()
            df_extra_wc_url["account"] = df_extra_wc_url["account"].apply(extra)
            df_extra_wc_url["consumption"] = 0
            df_extra_wc_url["mobile_visit_url"] = "空白"
            df_extra_wc_url["click_num"] = 0
            df_extra_wc_url["show"] = 0
            # df_extra_wc_url.to_excel("df_extra_wc_url.xlsx")
            extras_wc = pd.concat([data_wc, df_extra_wc_url], sort=True)
            # extras_wc.to_excel("extras_wc.xlsx")
            # 额外的--------------------------------------------------------------------------------

            df_pro_url_wc = extras_wc.groupby(by=["account"], as_index=False).sum()
            df_pro_url_wc["总计"] = "总计"
            url_data_wc = pd.concat([extras_wc, df_pro_url_wc], sort=True)
            f_url_wc = statistics(url_data_wc).reindex(columns=url_columns).sort_values(by=["account", "consumption"],
                                                                                        ascending=False)
            # f_url_wc.to_excel("f_url_wc.xlsx")
            finsh_url = pd.concat([f_url, f_url_wc])
            finsh_url.rename(columns={"account": "远大项目", "mobile_visit_url": "着陆页", "consumption": "消费", "show": "展现",
                                      "click_num": "点击量"}, inplace=True)
            # ok
            # KWD - 关键词
            df_word = df_kwd[["dia_type", "guest_num", "service_num", "first_visit_url"]].copy()
            df_word["first_visit_url"] = df_word["first_visit_url"].apply(regex_id)
            # df_word.to_excel("df_word.xlsx")
            df_word.rename(columns={"first_visit_url": "mobile_visit_url"}, inplace=True)
            df_kwd_key = formats(df_word).groupby(['mobile_visit_url'], as_index=False).sum()
            # df_kwd_key.to_excel("df_kwd_key.xlsx")
            # CONSUMPTION - 关键词
            df_key1 = df_consumption[
                ["account", 'key_word', 'mobile_visit_url', 'consumption', 'click_num', 'show']].copy()
            df_key1["mobile_visit_url"] = df_key1["mobile_visit_url"].apply(regex_id)
            new_df1_key = df_key1.groupby(by=["mobile_visit_url", "account", "key_word"], as_index=False).sum()

            # 关键词合并
            key_columns = ["总计", "account", "key_word", "consumption", "show", "click_num", "毛咨询", "有效对话", "五句", "毛/点",
                           "有效点击比", "对话成本"]
            key_word = pd.merge(df_kwd_key, new_df1_key, how="right", on="mobile_visit_url")  # 数据全都要
            # key_word.to_excel("key_word.xlsx")
            key_w = key_word.groupby(by=["account", "key_word"], as_index=False).sum()
            df_pro = key_w.groupby(by=["account"], as_index=False).sum()  # 组合用的
            df_pro["总计"] = "总计"
            f_key_word = statistics(pd.concat([key_w, df_pro], ignore_index=True, sort=True)).groupby(by=["account"],as_index=False).apply(sort_consum).reindex(columns=key_columns)
            # f_key_word.to_excel("f_key_word.xlsx",index=File_Name)
            # =======================================================================================================================完成的关键字
            df_word_wc = df_P[["dia_type", "guest_num", "service_num", "first_visit_url"]].copy()
            df_word_wc["first_visit_url"] = df_word_wc["first_visit_url"].apply(regex_id_wc)
            df_word_wc.rename(columns={"first_visit_url": "mobile_visit_url"}, inplace=True)
            df_kwd_key_wc = formats(df_word_wc).groupby(['mobile_visit_url'], as_index=False).sum()
            # CONSUMPTION - 关键词
            wc = models.CONSUMPTION_WC.objects.filter(date__range=(date1, date2))  #获取对应的胃肠消费表
            df_con_wc = read_frame(wc)
            df_key1_wc = df_con_wc[
                ["account", 'key_word', 'mobile_visit_url', 'consumption', 'click_num', 'show']].copy()
            df_key1_wc["mobile_visit_url"] = df_key1_wc["mobile_visit_url"].apply(regex_id_wc)
            new_df1_key_wc = df_key1_wc.groupby(by=["mobile_visit_url", "account", "key_word"], as_index=False).sum()
            # 关键词合并
            key_columns = ["总计", "account", "key_word", "consumption", "show", "click_num", "毛咨询", "有效对话", "五句", "毛/点",
                           "有效点击比", "对话成本"]
            key_word_wc = pd.merge(df_kwd_key_wc, new_df1_key_wc, how="right", on="mobile_visit_url")  # 数据全都要
            key_wc = key_word_wc.groupby(by=["account", "key_word"], as_index=False).sum()
            df_pro_wc = key_wc.groupby(by=["account"], as_index=False).sum()  # 组合用的
            df_pro_wc["总计"] = "总计"
            f_key_word_wc = statistics(pd.concat([key_wc, df_pro_wc], ignore_index=True, sort=True)).groupby(by=["account"], as_index=False).apply(sort_consum).reindex(columns=key_columns)
            # f_key_word_wc.to_excel("f_key_word_wc.xlsx",index=File_Name)
            finsh_key_word = pd.concat([f_key_word, f_key_word_wc])
            finsh_key_word.rename(columns={"account": "远大项目", "key_word": "关键字", "consumption": "消费", "show": "展现", "click_num": "点击量"},inplace=True)
            # ok1

            # CONSUMPTION - 计划
            plan = df_consumption[
                ["account", 'plan_name', 'mobile_visit_url', 'consumption', 'click_num', 'show']].copy()
            plan["mobile_visit_url"] = plan["mobile_visit_url"].apply(regex_id)
            plans = plan.groupby(by=["mobile_visit_url", "account", "plan_name"], as_index=False).sum()
            df_plans = pd.merge(df_kwd_key, plans, how="right", on="mobile_visit_url").groupby(
                by=["account", "plan_name"], as_index=False).sum()
            plan_pro = df_plans.groupby(by=["account"], as_index=False).sum()
            plan_pro["总计"] = "总计"
            plan_columns = ["总计", "account", "plan_name", "consumption", "show", "click_num", "毛咨询", "有效对话", "五句",
                            "毛/点", "有效点击比", "对话成本"]
            f_plan = statistics(pd.concat([df_plans, plan_pro], ignore_index=True, sort=True)).groupby(by=["account"],as_index=False).apply(sort_consum).reindex(columns=plan_columns)
            # =========================================================================================================================完成的计划

            plan_wc = df_con_wc[
                ["account", 'plan_name', 'mobile_visit_url', 'consumption', 'click_num', 'show']].copy()
            plan_wc["mobile_visit_url"] = plan_wc["mobile_visit_url"].apply(regex_id_wc)
            plans_wc = plan_wc.groupby(by=["mobile_visit_url", "account", "plan_name"], as_index=False).sum()

            df_plans_wc = pd.merge(df_kwd_key_wc, plans_wc, how="right", on="mobile_visit_url").groupby(
                by=["account", "plan_name"], as_index=False).sum()
            plan_pro = df_plans_wc.groupby(by=["account"], as_index=False).sum()
            plan_pro["总计"] = "总计"
            plan_columns = ["总计", "account", "plan_name", "consumption", "show", "click_num", "毛咨询", "有效对话", "五句",
                            "毛/点", "有效点击比", "对话成本"]
            f_plan_wc = statistics(pd.concat([df_plans_wc, plan_pro], ignore_index=True, sort=True)).groupby(
                by=["account"], as_index=False).apply(sort_consum).reindex(columns=plan_columns)
            finsh_plan = pd.concat([f_plan, f_plan_wc])
            finsh_plan.rename(
                columns={"account": "远大项目", "plan_name": "计划", "consumption": "消费", "show": "展现", "click_num": "点击量"},
                inplace=True)
            # f_plan.to_excel("f_plan.xlsx")
            # ok1
            parses = pd.ExcelWriter('file_data/' + date_name + '.xlsx')
            finsh_url.to_excel(parses, '着陆页', index=False)
            finsh_key_word.to_excel(parses, '关键词', index=False)
            finsh_plan.to_excel(parses, '计划', index=False)
            parses.save()
            # ======================处理==============================================
            aa = finsh_url['消费'].apply(lambda x: round(x, 2))
            # url_columns= ["总计","account","mobile_visit_url", "consumption", "show", "click_num", "毛咨询", "dia_type", "五句","毛/点","有效点击比","对话成本"]

            info = zip(list(finsh_url['远大项目']), list(finsh_url['着陆页']), list(aa),
                       list(finsh_url['展现']), list(finsh_url['点击量']), list(finsh_url['毛咨询']),
                       list(finsh_url['有效对话']), list(finsh_url['五句']),
                       list(finsh_url['毛/点']), list(finsh_url['有效点击比']), list(finsh_url['对话成本']))
            return render(request, 'index.html', {"info": list(info)})

        except ImportError as e:
            print(e)
            return render(request, '404.html')
    else:
        return render(request, "index.html")


def manages(request):
    bb = models.File_Name.objects.all().order_by("id")
    paginator = Paginator(bb, 5)    # 每页显示5条数据
    page = request.GET.get('page')
    contacts = paginator.get_page(page)

    return render(request, 'manages.html', {'contacts': contacts})

def delete_info(request,id):
    d_name = models.File_Name.objects.filter(id=id).first().files_name
    models.File_Name.objects.filter(id=id).delete()
    models.KWD.objects.filter(file_name_kwd=d_name).delete()
    models.CONSUMPTION_GC.objects.filter(file_name_con=d_name).delete()
    models.CONSUMPTION_WC.objects.filter(file_name_con=d_name).delete()
    models.PKT.objects.filter(file_name_pkt=d_name).delete()

    return redirect('/parses/manages?page=1')

def add_account(request):

    if request.method=="GET":
        account_gc = models.ACCOUNT_GC.objects.all()
        account_wc = models.ACCOUNT_WC.objects.all()
        return render(request,'add_account.html',{"account_gc":account_gc,"account_wc":account_wc})
    elif request.method=="POST":
        if request.POST.get("name1"):
            account_gc = request.POST.get("name1")
            print("account_gc: ",account_gc)
            models.ACCOUNT_GC.objects.create(account_name=account_gc)
            return redirect('/parses/add_account')
        if request.POST.get("name2"):
            account_wc=request.POST.get("name2")
            print("account_wc: ",account_wc)
            models.ACCOUNT_WC.objects.create(account_name=account_wc)
            return redirect('/parses/add_account')
        else:
            return render(request,'404.html')
    else:
        return render(request,'404.html')


def del_account_gc(request,id):
    models.ACCOUNT_GC.objects.filter(id=id).delete()
    return redirect('/parses/add_account')
def del_account_wc(request,id):
    models.ACCOUNT_WC.objects.filter(id=id).delete()
    return redirect('/parses/add_account')

def download_file(request):
    # with open("file_name.txt", 'r') as ff:
    #     date_name = ff.read()
    global date_name
    print(date_name)
    the_file_name = date_name + '.xlsx'
    filename = 'file_data/' + the_file_name
    response = StreamingHttpResponse(readFile(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response


def download_kwd(request):
    file = open('static/商务通文件模板.xls', 'rb')
    the_file_name = file + '.xlsx'
    response = HttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response


def download_consum(request):
    file = open('static/消费表文件模板.csv', 'rb')
    the_file_name = file + '.csv'
    response = HttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
    return response

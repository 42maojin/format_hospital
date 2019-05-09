from django.db import models

# Create your models here.
'''
'编号', '开始访问时间', '开始对话时间', '对话时长', '对话类型', '开始方式', '结束方式', '客人讯息数', '客服讯息数', '名称', '参与接待客服', '客人类别',
'操作系统', '永久身份', '对话来源', '访问来源', '初次访问网址', '客人说明',
        '关键词', 'IP定位', '初始接待客服', '分辨率', '本次访问页数', '参与邀请客服'
'''


# 商务通表== 肛肠
class KWD(models.Model):
    file_name_kwd=models.CharField(max_length=200)  #对应的文件名
    u_number = models.IntegerField()  # 编号
    start_visit_time = models.DateTimeField()  # 开始访问时间
    start_dia_time = models.DateTimeField()  # 开始对话时间
    dia_time = models.CharField(max_length=100)  # 对话时长
    dia_type = models.CharField(max_length=200)  # 对话类型
    start_func = models.CharField(max_length=100)  # 开始方式
    end_func = models.CharField(max_length=100)  # 结束方式
    guest_num = models.IntegerField()  # 客人讯息数
    service_num = models.IntegerField()  # 客服讯息数
    name = models.CharField(max_length=200)  # 名称
    join_service = models.CharField(max_length=200)  # 参与接待客服
    guest_type = models.CharField(max_length=200)  # 客人类型
    operating_system = models.CharField(max_length=200)  # 操作系统
    u_id = models.CharField(max_length=200)  # 永久身份
    dia_source = models.TextField()  # 对话来源
    visit_source_url = models.TextField()  # 访问来源
    first_visit_url = models.TextField(null=True)  # 初次访问网址
    guest_desc = models.TextField(null=True)  # 客人说明
    key_word = models.CharField(max_length=200,null=True)  # 关键词
    ip_location = models.CharField(max_length=200)  # 'IP定位'
    first_service_guest = models.CharField(max_length=50)  # '初始接待客服',
    resolution = models.CharField(max_length=100)  # '分辨率',
    visit_page = models.CharField(max_length=200)  # '本次访问页数',
    join_invite = models.CharField(max_length=250)  # '参与邀请客服'
    # f_id = models.ForeignKey('File_Name', on_delete=models.CASCADE)

# 商务通表== 胃肠
class PKT(models.Model):
    file_name_pkt = models.CharField(max_length=200)  # 对应的文件名
    u_number = models.IntegerField()  # 编号
    start_visit_time = models.DateTimeField()  # 开始访问时间
    start_dia_time = models.DateTimeField()  # 开始对话时间
    dia_time = models.CharField(max_length=100)  # 对话时长
    dia_type = models.CharField(max_length=200)  # 对话类型
    start_func = models.CharField(max_length=100)  # 开始方式
    end_func = models.CharField(max_length=100)  # 结束方式
    guest_num = models.IntegerField()  # 客人讯息数
    service_num = models.IntegerField()  # 客服讯息数
    name = models.CharField(max_length=200)  # 名称
    join_service = models.CharField(max_length=200)  # 参与接待客服
    guest_type = models.CharField(max_length=200)  # 客人类型
    operating_system = models.CharField(max_length=200)  # 操作系统
    u_id = models.CharField(max_length=200)  # 永久身份
    dia_source = models.TextField()  # 对话来源
    visit_source_url = models.TextField()  # 访问来源
    first_visit_url = models.TextField(null=True)  # 初次访问网址
    guest_desc = models.TextField(null=True)  # 客人说明
    key_word = models.CharField(max_length=200,null=True)  # 关键词
    ip_location = models.CharField(max_length=200)  # 'IP定位'
    first_service_guest = models.CharField(max_length=50)  # '初始接待客服',
    resolution = models.CharField(max_length=100)  # '分辨率',
    visit_page = models.CharField(max_length=200)  # '本次访问页数',
    join_invite = models.CharField(max_length=250)  # '参与邀请客服'
    # f_id = models.ForeignKey('File_Name',on_delete=models.CASCADE)

# 各个账号的消费表
class CONSUMPTION_GC(models.Model):
    file_name_con = models.CharField(max_length=200)  # 对应的文件名
    account = models.CharField(max_length=200)  # 账号
    date = models.DateField()  # 文件对应时间
    plan_name = models.CharField(max_length=200)  # 推广计划名称
    unit_name = models.CharField(max_length=200)  # 推广单元名称
    key_word = models.CharField(max_length=200)  # 关键词名称
    match_model = models.CharField(max_length=200)  # 匹配模式
    bid = models.FloatField()  # 出价
    visit_url = models.TextField()  # 访问URL
    mobile_visit_url = models.TextField()  # 移动访问URL
    start_or_stop = models.CharField(max_length=100)  # 启用/暂停
    label = models.CharField(max_length=200)  # 标签
    applet = models.TextField()  # 小程序URL
    key_word_status = models.CharField(max_length=100)  # 关键词状态
    computer_price = models.CharField(max_length=200)  # 计算机指导价
    computer_quality = models.CharField(max_length=50)  # 计算机质量度
    mobile_quality = models.CharField(max_length=50)  # 移动质量度
    consumption = models.FloatField()  # 消费
    avg_click_price = models.FloatField()  # 平均点击价格
    click_num = models.IntegerField()  # 点击
    show = models.IntegerField()  # 展现
    click_rate = models.CharField(max_length=200)  # 点击率
    page_conversion = models.CharField(max_length=100)  # 网页转化
    k_show_consumption = models.CharField(max_length=100)  # 千次展现消费
    avg_conversion_price = models.CharField(max_length=200)  # 平均转化价格
    conversion_word = models.CharField(max_length=200)  # 转化搜索词
    # f_id=models.ForeignKey('File_Name',on_delete=models.CASCADE)

class CONSUMPTION_WC(models.Model):
    file_name_con = models.CharField(max_length=200)  # 对应的文件名
    account = models.CharField(max_length=200)  # 账号
    date = models.DateField()  # 文件对应时间
    plan_name = models.CharField(max_length=200)  # 推广计划名称
    unit_name = models.CharField(max_length=200)  # 推广单元名称
    key_word = models.CharField(max_length=200)  # 关键词名称
    match_model = models.CharField(max_length=200)  # 匹配模式
    bid = models.FloatField()  # 出价
    visit_url = models.TextField()  # 访问URL
    mobile_visit_url = models.TextField()  # 移动访问URL
    start_or_stop = models.CharField(max_length=100)  # 启用/暂停
    label = models.CharField(max_length=200)  # 标签
    applet = models.TextField()  # 小程序URL
    key_word_status = models.CharField(max_length=100)  # 关键词状态
    computer_price = models.CharField(max_length=200)  # 计算机指导价
    computer_quality = models.CharField(max_length=50)  # 计算机质量度
    mobile_quality = models.CharField(max_length=50)  # 移动质量度
    consumption = models.FloatField()  # 消费
    avg_click_price = models.FloatField()  # 平均点击价格
    click_num = models.IntegerField()  # 点击
    show = models.IntegerField()  # 展现
    click_rate = models.CharField(max_length=200)  # 点击率
    page_conversion = models.CharField(max_length=100)  # 网页转化
    k_show_consumption = models.CharField(max_length=100)  # 千次展现消费
    avg_conversion_price = models.CharField(max_length=200)  # 平均转化价格
    conversion_word = models.CharField(max_length=200)  # 转化搜索词
    # f_id=models.ForeignKey('File_Name',on_delete=models.CASCADE)

#
class File_Name(models.Model):
    # id=models.AutoField(primary_key=True,default=1)
    files_name = models.CharField(max_length=300)  # 文件名
    create_time = models.DateTimeField()  # 文件上传时间


class ACCOUNT_GC(models.Model):
    account_name= models.CharField(max_length=200)

class ACCOUNT_WC(models.Model):
    account_name= models.CharField(max_length=200)
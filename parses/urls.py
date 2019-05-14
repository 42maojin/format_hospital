'''

Create Time  2019/4/10
by xiang

'''

from django.urls import path,re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download_file/', views.download_file, name='download_file'),
    path('download_kwd/',views.download_kwd,name="download_kwd"),
    path('download_consum/',views.download_consum,name="download_consum"),
    path('manages/',views.manages,name="manages"),
    path('add_account/',views.add_account,name="add_account"),
    path('useful/',views.useful,name="useful"),
    re_path('^del_account_gc/(?P<id>[0-9]*)/$',views.del_account_gc,name="del_account_gc"),
    re_path('^del_account_wc/(?P<id>[0-9]*)/$',views.del_account_wc,name="del_account_wc"),

    re_path(r'^delete_info/(?P<id>[0-9]*)/$',views.delete_info,name="delete_info"),
]
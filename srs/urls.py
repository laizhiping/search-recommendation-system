from django.urls import path, re_path
from . import views
from django.conf.urls import url

urlpatterns = [
	# path('',views.index, name='index'),
	# path('search', views.search),
	# path('runoob/', views.runoob),
	re_path(r'search',views.search_p)
	# path(r'search',views.search_p)

]

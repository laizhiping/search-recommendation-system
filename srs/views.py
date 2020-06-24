from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators import csrf

# Create your views here.

# def search(request):
#     request.encoding = 'utf-8'
#     if 'q' in request.GET and request.GET['q']:
#         message = '你搜索的内容为' + request.GET['q']
#     else:
#         message = "你提交了空表单"
#     print(message)
#     return HttpResponse(message)


def search_p(request):
    res = {}
    if request.POST:
        print(request.POST['q'])
        res['precise'] = 0.12
        res['emotion'] = 1.2
        res['Ids_his'] = ['123','35456','3557']
        res['Ids_re'] = ['post','resafaf','tesad']
    elif request.GET:
        res['precise'] = 0.12
        res['emotion'] = 1.2
        res['Ids_his'] = ['123', '35456', '3557']
        res['Ids_re'] = ['get', 'get', 'get']
    return render(request, "search_post.html", res)

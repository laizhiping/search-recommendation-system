from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators import csrf
import sys
sys.path.append("..")
import FeatureExtractor
import sentiment_analysis
# Create your views here.

# def search(request):
#     request.encoding = 'utf-8'
#     if 'q' in request.GET and request.GET['q']:
#         message = '你搜索的内容为' + request.GET['q']
#     else:
#         message = "你提交了空表单"
#     print(message)
#     return HttpResponse(message)

res = {}
res['history'] = []
def search(request):
    if request.POST:
        # print(request.POST['q'])
        query = request.POST['q']
        # print(query)

        # 查询词加入搜索历史列表
        res['history'].append(query)

        # 进行查询推荐
        result = FeatureExtractor.do_query(query)
        
        # 获取推荐词和其对应的相似度
        similarity, recommend = zip(*result)
        # 取第TOP_K个推荐词的精度，若数量不足TOP_K个则取最后一个
        if len(similarity) >= FeatureExtractor.TOP_K:
            res['precise'] = similarity[FeatureExtractor.TOP_K - 1]
        else:
            res['precise'] = similarity[-1]
        res['sentiment'] = sentiment_analysis.getscore_recommend(recommend)
        res['recommend'] = recommend
    elif request.GET:
        pass
    return render(request, "search_post.html", res)

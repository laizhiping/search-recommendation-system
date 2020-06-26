import jieba
import json
import os
import pre_deal

SAdic={}
with open('SA.model','r') as f:
    SAdic = json.loads(f.read())
def getscore(sstring):
    score = 0
    words = pre_deal.deal_str(sstring)
    for word in words:
        if word in SAdic.keys():
            score += SAdic[word]
    return score

def getscore_recommend(sstrings):
    return sum([getscore(item) for item in sstrings])
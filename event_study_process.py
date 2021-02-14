# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 16:14:58 2021

@author: Jewon Shin
"""

import pandas as pd
import numpy as np
import math
import statsmodels.formula.api as smf
from sklearn import linear_model
import scipy.stats as st
import statsmodels.formula.api as smf
from sklearn import linear_model
import scipy.stats as st

from __future__ import print_function

import numpy as np
from scipy.stats import ttest_ind, ttest_ind_from_stats
from scipy.special import stdtr

#######
# 1. Sorting stocks based on the size of its asset
#######

fn_data = pd.read_csv('fnguide_utf.csv')
ts_data = pd.read_csv('ts2000_utf.csv')


asset = fn_data[['Symbol', 'conm', 'regist_num', '회계년', 'asset']]
asset = asset.rename(columns={'Symbol':'code'})
asset = asset.rename(columns={'회계년':'year'})
asset['asset'] =asset['asset'].fillna(method='ffill') ## 2020년의 자료는 아직 없지만, 2019년에 넘었으면 잠정적으로 넘었다고 가정. 
asset['asset_above']= (asset['asset']>=2000000000000/1000)*1

asset_above = asset[asset['asset_above']==1]

merge = pd.merge(ts_data, asset_above, on=['year','conm','regist_num'], how='left')
merge = merge[merge['asset_above']==1] # 자산총액 2조 이상 기업의 사회이사 리스트
merge.to_csv('ts_name_list_utf.csv')


#######
# 2. Calculating abnormal return based on market model
#######

data = pd.read_csv('total_market_ret.csv', parse_dates=['date']) ## FnGuide의 KOSPI+KSE 수익률
data2 = pd.melt(data, id_vars=['date'], var_name='code', value_name='ret') ## Time-series data -> Panel data
data2['ret'] = data2['ret']/100

kospi = pd.read_csv('kospi_ret.csv', parse_dates=['date'])
conm = pd.read_csv('code_list_utf.csv')

data3 = pd.merge(data2, kospi, how='left', on=['date'])
data3 = pd.merge(data3, conm, how='left', on=['code'])

## Delete holiday
data4 = data3.dropna(axis=0)

# Abnormal Returns
def ols_coef(x,formula):
    return smf.ols(formula,data=x).fit().params

FF1_process = (data4.groupby(['date','code'])
                .apply(ols_coef,'ret ~ kospi_ret'))

FF1_process.to_csv("FF1_result.csv")



#######
# 3. Merging TS-2000 and sex information in DART
#######

ts_name_list = pd.read_csv('ts_name_list_utf.csv')
# 자산총액 2조 이상 기업의 사회이사 리스트

dart_name_list = pd.read_csv('dart_name_list_utf.csv') 
# TS-2000의 자산총액 2조 이상인 기업을 대상으로, DART에서 임원자료를 수집한 파일
# 본 파일에는 미등기임원, 등기임원이 섞여있음.
# 한편, TS-2000에는 존재하는 회사이고 자산총액 2조를 넘지만, DART에 공시 자체가 되어있지 않거나, 
# DART에 회사는 존재해도 해당년 사업보고서가 존재하지 않는 경우가 있음.


## 일단 회계연도 상관없이 이름, 성별 정보만 분리해서 목록으로 만듦.

dart_name_list2 = dart_name_list[['conm','name','sex']].drop_duplicates()
ts_name_list2 = ts_name_list[['conm','regist_num','name']]

merge1 = pd.merge(ts_name_list2, dart_name_list2, on=['conm','name'], how='left', indicator=True)

left_only = merge1[merge1['_merge']=='left_only']


dart_name_list3 = dart_name_list[['conm','name','sex', 'birthdate', 'foreign']].drop_duplicates()
ts_name_list3 = ts_name_list[['conm','regist_num','name', 'name_ts', 'birthdate']].drop_duplicates()

merge2 = pd.merge(ts_name_list3, dart_name_list3, on=['conm','name', 'birthdate'], how='left', indicator=True)

left_only2 = merge2[merge2['_merge']=='left_only']  # 345명 사외이사 
# merge가 되지 않은 경우는 다음 경우로 추정된다.
#1. 외국인 이사 이름의 기재방법이 DART와 달라서 붙지 않음
#2. 생년월일이 맞지 않음. (보통 TS-2000의 생년월일이 틀린 경우가 대부분)
#3. TS-2000에는 존재하는 회사이고 자산총액 2조를 넘지만, DART에 공시 자체가 되어있지 않거나, 
#   DART에 회사는 존재해도 해당년 사업보고서가 존재하지 않는 경우가 있음.

merge2.to_csv("merge_utf.csv")

### 다시 정리 <- 상기에서 left_only로 되어있는 경우는 수작업으로 정리
ts_name_list = pd.read_csv('ts_name_list_utf.csv')
director = pd.read_csv('outside_director_utf.csv')

merge = pd.merge(ts_name_list, director, on=['conm','regist_num','name','birthdate'], how='left')
merge.to_csv('outside_director_sorting_utf.csv')


########
# 4. Sorting firms based on the existence of female outside borders
########

## 해당년도에 여성사외이사가 있는 기업 골라내기 ###

list_2018 = merge[merge['year']==2018]
female_2018 = list_2018[list_2018['sex']=='여']
female_2018_2 = female_2018.groupby(['regist_num']).size().reset_index(name='female_count') ## 여성 사외이사가 존재하는 경우, 그 수 ##
female_2018_3 = pd.merge(female_2018, female_2018_2, on='regist_num', how='left')

list_2018_2 = list_2018[['conm','regist_num','code','year','asset','asset_above']].drop_duplicates()
female_2018_3 = female_2018_3[['conm','regist_num','year','asset','asset_above','female_count']].drop_duplicates()

list_2018_total = pd.merge(list_2018_2, female_2018_3, on=['conm','regist_num','year','asset','asset_above'], how='left')
list_2018_total = list_2018_total.fillna(0) ## female_count = 0 ; 남자만 존재 / female_count > 1; 여성이사존재
list_2018_total_female = list_2018_total[list_2018_total['female_count']>=1]
list_2018_total_male = list_2018_total[list_2018_total['female_count']==0]

list_2019 = merge[merge['year']==2019]
list_2019 = merge[merge['year']==2019]
female_2019 = list_2019[list_2019['sex']=='여']
female_2019_2 = female_2019.groupby(['regist_num']).size().reset_index(name='female_count') ## 여성 사외이사가 존재하는 경우, 그 수 ##
female_2019_3 = pd.merge(female_2019, female_2019_2, on='regist_num', how='left')

list_2019_2 = list_2019[['conm','regist_num','code','year','asset','asset_above']].drop_duplicates()
female_2019_3 = female_2019_3[['conm','regist_num','year','asset','asset_above','female_count']].drop_duplicates()

list_2019_total = pd.merge(list_2019_2, female_2019_3, on=['conm','regist_num','year','asset','asset_above'], how='left')
list_2019_total = list_2019_total.fillna(0) ## female_count = 0 ; 남자만 존재 / female_count > 1; 여성이사존재
list_2019_total_female = list_2019_total[list_2019_total['female_count']>=1]
list_2019_total_male = list_2019_total[list_2019_total['female_count']==0]


########
# 5. Event Study
########

# - 정무위 통과: 2019-11-25
# - 법사위 통과: 2019-11-27
# - 본회의 통과: 2020-01-09

data = pd.read_csv('total_market_ret.csv', parse_dates=['date'])
data2 = pd.melt(data, id_vars=['date'], var_name='code', value_name='ret')
data2['ret'] = data2['ret']/100

kospi = pd.read_csv('kospi_ret.csv', parse_dates=['date'])
conm = pd.read_csv('code_list_utf.csv')

data3 = pd.merge(data2, kospi, how='left', on=['date'])
data3 = pd.merge(data3, conm, how='left', on=['code'])

## Delete holiday
data4 = data3.dropna(axis=0)

FF1_process2 = pd.read_csv("FF1_result.csv", parse_dates=['date'])
FF1_process2 = FF1_process2[FF1_process2['date']>='2019-11-01 00:00:00']
FF1_process2 = FF1_process2[FF1_process2['date']<='2020-01-30 00:00:00']

FF1_process2 = FF1_process2.rename(columns={'Intercept':'f1_int'})
FF1_process2 = FF1_process2.rename(columns={'kospi_ret':'f1_mkt'})
FF1_process3 = pd.merge(FF1_process2, data4, on=['date','code'],how='left')
FF1_process3['f1_d1']=FF1_process3['ret']-FF1_process3['kospi_ret']*FF1_process3['f1_mkt']

FF1_process3['dum_aret'] = ( FF1_process3['f1_d1']>0 )*1
FF1_process3['year'] = FF1_process3['date'].dt.year

list_2019_total2 = list_2019_total[['code','female_count','asset_above']]
FF1_process4 = pd.merge(FF1_process3, list_2019_total2, on=['code'], how='left')
FF1_process5 = FF1_process4[FF1_process4['asset_above']==1]  ## 자산 2조 이상만 골라내기 

### CAR (Cumulative Abnormal Return): CAR(0, +2)
FF1_process5['car'] = FF1_process5.groupby('code')['f1_d1'].rolling(3).sum().reset_index(0,drop=True)

stock_female_2019 = FF1_process5[FF1_process5['female_count']>=1]
stock_male_2019 = FF1_process5[FF1_process5['female_count']==0]

## total firm number ##
total_firm_number = stock_female_2019[['date','code']].drop_duplicates()
total_firm_number = stock_female_2019.groupby(['date'])['code'].agg(['count'])
total_firm_number = total_firm_number.rename(columns={'count':'total_firm_number'})

## Number of AR
number = stock_female_2019.groupby(['date'])['dum_aret'].agg(['sum'])
number.rename(columns={'sum':'no_positive_aret'}, inplace=True)
number = pd.merge(number, total_firm_number, on=['date'], how='left')
number['no_negative_aret'] = number['total_firm_number'] - number['no_positive_aret'] #45: total firm number
number.to_csv('number.csv')
number = pd.read_csv("number.csv", parse_dates=['date'])

# AAR(Average Abnormal Return)
aar = stock_female_2019.groupby(['date'])['f1_d1'].agg(['mean','std'])
aar.rename(columns={'mean':'mean_aar', 'std':'std_aar'}, inplace=True)
aar['t_test'] = aar['mean_aar']/aar['std_aar']
aar['p_value'] = st.norm.cdf(aar['t_test'])

aar.to_csv('aar.csv')
aar = pd.read_csv("aar.csv", parse_dates=['date'])

aar = pd.merge(aar, number, on='date', how='left')

event_day = "2019-11-25 00:00:00"
aar = aar.reset_index().rename(columns={"index": "event_index"})
aar['temp_index'] = aar[aar['date'] == event_day]['event_index']
aar['temp_index'] = aar['temp_index'].fillna(method='ffill')
aar['temp_index'] = aar['temp_index'].fillna(method='backfill')
aar['event_index'] = aar['event_index'] - aar['temp_index']
aar = aar.drop('temp_index', axis=1)


### -10 ~ 10
analysis1 = aar[ (aar['event_index']>=-10) & (aar['event_index']<=10)]
analysis1['car'] = analysis1['mean_aar'].cumsum()

stock_female_2019_2 = stock_female_2019[stock_female_2019['date']=='2020-01-13 00:00:00']
stock_male_2019_2 = stock_male_2019[stock_male_2019['date']=='2020-01-13 00:00:00']
stock_female_2019_3 =stock_female_2019_2['car'].agg(['mean','min','max'])
stock_male_2019_2 = stock_male_2019[stock_male_2019['date']=='2020-01-13 00:00:00']
stock_male_2019_3 =stock_male_2019_2['car'].agg(['mean','min','max'])


### t-test: 여성사외이사 존재/비존재 기업 간의 CAR 차이 유의성 검증
t, p = ttest_ind(stock_female_2019_2['car'], stock_male_2019_2['car'], equal_var=False)
print("ttest_ind:            t = %g  p = %g" % (t, p))


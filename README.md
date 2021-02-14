# Event Study


# File
- 파일명 뒤에 "utf"가 붙어있는 것은 Python에서 한국어를 읽을 수 있도록 UTF-8로 인코딩 처리한 것이다. 통상적으로 엑셀에서 한국어를 읽기 위해서는 이 파일을 ANSI 인코딩으로 재변환 필요.

- code_list_utf.csv: FnGuide의 KOSPI+KSE 회사 전체 목록정리 (code: FnGuide 주식부여번호 / conm: 회사명)

- fnguide_utf.csv: FnGuide에서 추출한 KOSPI+KSE 회사의 자산총액 자료 (2017 ~ 2019)
  * asset: 자산총액 (단위: 천)
  * regist_num: 사업자등록번호 (TS-2000 자료와 병합할 때 사용)
  
- ts2000_utf.csv: TS-2000에서 추출한 KOSPI+KSE 회사의 사외이사 목록
  * 사외이사는 총 두 종류가 존재: 직명코드 751 - 사외이사(감사위원), 직명코드 721 - 사외이사
  * name_ts는 TS-2000에 등록된 사외이사 이름, name은 TS-2000에 등록된 이름에서 공백을 제거한 것. 
    name_ts는 향후 TS-2000의 다른 자료를 병합할 때, name은 다른 DB와 병합을 시도할 때를 고려
  * birthdate는 해당 사외이사의 생년월일 (단, TS-2000의 경우 생년월일이 부정확한 경우가 포함되어 있음.)
  
- FF1_result.csv: FnGuide의 KOSPI+KSE 회사 전체 주식수익률(현금배당반영)을 대상으로 market model로 abnormal return을 산출한 데이터 (2018-01-02 ~ 2021-01-27)

- dart_name_list_utf.csv
  * TS-2000의 자산총액 2조 이상인 기업을 대상으로, DART에서 임원자료를 수집한 파일
  * 본 파일에는 미등기임원, 등기임원이 섞여있음. 
  * 한편, TS-2000에는 존재하는 회사이고 자산총액 2조를 넘지만, DART에 공시 자체가 되어있지 않거나, DART에 회사는 존재해도 해당년 사업보고서가 존재하지 않는 경우가 있음.
  

# Female_Director


# File
- code_list_utf.csv: FnGuide의 KOSPI+KSE 회사 전체 목록정리 (code: FnGuide 주식부여번호 / conm: 회사명)

- fnguide_utf.csv: FnGuide에서 추출한 KOSPI+KSE 회사의 자산총액 자료 (2017 ~ 2019)
  * asset: 자산총액 (단위: 천)
  * regist_num: 사업자등록번호 (TS-2000 자료와 병합할 때 사용)
  
- ts2000_utf.csv: TS-2000에서 추출한 KOSPI+KSE 회사의 사외이사 목록
  * 사외이사는 총 두 종류가 존재: 직명코드 751 - 사외이사(감사위원), 직명코드 721 - 사외이사
  * name_ts는 TS-2000에 등록된 사외이사 이름, name은 TS-2000에 등록된 이름에서 공백을 제거한 것. 
    name_ts는 향후 TS-2000의 다른 자료를 병합할 때, name은 다른 DB와 병합을 시도할 때를 고려
  * birthdate는 해당 사외이사의 생년월일 (단, TS-2000의 경우 생년월일이 부정확한 경우가 포함되어 있음.)
  

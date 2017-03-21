from enum import Enum,IntEnum
from functools import reduce
from datetime import datetime
from pyDatalog import pyDatalog

@pyDatalog.predicate()
def p2(X,Y):
    yield (1,2)
    yield (2,3)
    yield ("daniel",3)

def age_as_of(dob,date_as_of):
  return date_as_of.year - dob.year - ((date_as_of.month, date_as_of.day) < (dob.month, dob.day))

class EntitlementReason(IntEnum):
  OASI=0
  DIB=1
  ESRD=2
  DIB_AND_ESRD = 3

class ICDType(IntEnum):
  NINE = 9
  TEN = 0

class Diagnosis(pyDatalog.Mixin):
  def __init__(self,
              beneficiary,
              icdcode,
              codetype=ICDType.NINE):
    super().__init__()
    self.beneficiary = beneficiary
    self.icdcode = icdcode
    self.codetype = codetype

  def __repr__(self): # specifies how to display an Employee
    return str(beneficiary) + str(self.icdcode) + str(self.codetype)


class Beneficiary(pyDatalog.Mixin):
  def __init__(self,
              hicno,sex,dob,
              original_reason_entitlement=EntitlementReason.OASI,
              medicaid=False,
              newenrollee_medicaid=False,):
    super().__init__()
    self.hicno = hicno
    self.sex = sex
    self.dob = datetime.strptime(dob,"%Y%m%d")
    self.age = age_as_of(self.dob,datetime.now())
    self.medicaid = medicaid
    self.newenrollee_medicaid = newenrollee_medicaid
    self.original_reason_entitlement = original_reason_entitlement
    self.diagnoses = []

  def __repr__(self): # specifies how to display an Employee
    return str(self.hicno)

  def add_diagnosis(self,diag):
    self.diagnoses.append(diag)

 

# lines 352 - 361
def load_diagnostic_category_facts():
  diagnostic_categories = [
          ("cancer",["8","9","10","11","12"]),
          ("diabetes",["17","18","19"]),
          ("immune",["47"]),
          ("card_resp_fail",["82","83","84"]),
          ("chf",["85"]),
          ("copd",["110","111"]),
          ("renal",[str(x) for x in range(134,142)]),
          ("compl",["176"]),
          ("pressure_ulcer",["157","158","159","160"]),
          ("sepsis",["2"]) ]
  for dc, ccs in diagnostic_categories:
    for cc in ccs:
      pyDatalog.assert_fact('dc',dc,cc)

def load_cc_facts(f,icdcodetype):
  file = open(f, 'r')                                     
  for line in file:
    vals = line.split()
    if len(vals) == 2:
      icd,cc = vals
    elif len(vals) == 3:
      icd,cc,_ = vals
    pyDatalog.assert_fact('cc',icd,cc,icdcodetype) 

def load_hcc_facts():
  overriders = [
          ("8",["9","10","11","12" ]),
          ("9",["10","11","12" ]),
          ("10",["11","12" ]),
          ("11",["12" ]),
          ("17",["18","19" ]),
          ("18",["19" ]),
          ("27",["28","29","80" ]),
          ("28",["29" ]),
          ("46",["48" ]),
          ("51",["52" ]),
          ("54",["55" ]),
          ("57",["58" ]),
          ("70",["71","72","103","104","169" ]),
          ("71",["72","104","169" ]),
          ("72",["169" ]),
          ("82",["83","84" ]),
          ("83",["84" ]),
          ("86",["87","88" ]),
          ("87",["88" ]),
          ("99",["100" ]),
          ("103",["104" ]),
          ("106",["107","108","161","189" ]),
          ("107",["108" ]),
          ("110",["111","112" ]),
          ("111",["112" ]),
          ("114",["115" ]),
          ("134",["135","136","137","138","139","140","141"]),
          ("135",["136","137","138","139","140","141" ]),
          ("136",["137","138","139","140","141" ]),
          ("137",["138","139","140","141" ]),
          ("138",["139","140","141" ]),
          ("139",["140","141" ]),
          ("140",["141" ]),
          ("157",["158","159","160","161" ]),
          ("158",["159","160","161" ]),
          ("159",["160","161" ]),
          ("160",["161" ]),
          ("166",["80","167" ])
          ]
  for overrider, overridees in overriders:
    for overridee in overridees:
      pyDatalog.assert_fact('overrides',overrider,overridee)

pyDatalog.create_terms('b,dc,overrides,has_cc_that_overrides_this_one,beneficiary_has_hcc,Type,OT,beneficiary_has_cc,cc,CC,CC2,ICD,edit,male,B,Diag,Ben,female,medicaid,age,A,old_age_entitled,new_enrollee,D,ben_hcc')

pyDatalog.create_terms('sepsis_card_resp_fail,cancer_immune,diabetes_chf,chf_copd,chf_renal, copd_card_resp_fail')

pyDatalog.create_terms('sepsis_pressure_ulcer, sepsis_artif_openings, art_openings_pressure_ulcer, diabetes_chf, copd_asp_spec_bact_pneum, asp_spec_bact_pneum_pres_ulc, sepsis_asp_spec_bact_pneum, schizophrenia_copd, schizophrenia_chf, schizophrenia_seizures,sex_age_range,U,L,disabled,originally_disabled,ben_hcc,sex_age,MF,indicator ')

def load_facts():
  load_cc_facts("icd10.txt",0)
  load_cc_facts("icd9.txt",9)
  load_hcc_facts()
  load_diagnostic_category_facts()
  
def community_regression():
  # &COMM_REG
  reg_vars = ["F0_34","F35_44", "F45_54", "F55_59", "F60_64", "F65_69",
  "F70_74", "F75_79", "F80_84", "F85_89", "F90_94", "F95_GT",
  "M0_34","M35_44", "M45_54", "M55_59", "M60_64", "M65_69",
  "M70_74", "M75_79", "M80_84", "M85_89", "M90_94", "M95_GT",
  "MCAID_Female_Aged","MCAID_Female_Disabled",
  "MCAID_Male_Aged","MCAID_Male_Disabled",
  "OriginallyDisabled_Female","OriginallyDisabled_Male",
  "DISABLED_HCC6", "DISABLED_HCC34",
  "DISABLED_HCC46","DISABLED_HCC54",
  "DISABLED_HCC55","DISABLED_HCC110",
  "DISABLED_HCC176", "SEPSIS_CARD_RESP_FAIL",
  "CANCER_IMMUNE", "DIABETES_CHF",
  "CHF_COPD","CHF_RENAL",
  "COPD_CARD_RESP_FAIL",
  "HCC1","HCC2","HCC6","HCC8","HCC9","HCC10", "HCC11", "HCC12", 
  "HCC17", "HCC18", "HCC19", "HCC21", "HCC22", "HCC23", "HCC27", "HCC28",
  "HCC29", "HCC33", "HCC34", "HCC35", "HCC39", "HCC40", "HCC46", "HCC47", 
  "HCC48", "HCC51", "HCC52", "HCC54", "HCC55", "HCC57", "HCC58", "HCC70", 
  "HCC71", "HCC72", "HCC73", "HCC74", "HCC75", "HCC76", "HCC77", "HCC78", 
  "HCC79", "HCC80", "HCC82", "HCC83", "HCC84", "HCC85", "HCC86", "HCC87", 
  "HCC88", "HCC96", "HCC99", "HCC100","HCC103","HCC104","HCC106","HCC107",
  "HCC108","HCC110","HCC111","HCC112","HCC114","HCC115","HCC122","HCC124",
  "HCC134","HCC135","HCC136","HCC137","HCC138","HCC139","HCC140","HCC141",
  "HCC157","HCC158","HCC159","HCC160","HCC161","HCC162","HCC166","HCC167",
  "HCC169","HCC170","HCC173","HCC176","HCC186","HCC188","HCC189" ]
  return reg_vars

def new_enrollee_regression():
  # 
  reg_vars = ["NEF0_34","NEF35_44", "NEF45_54", "NEF55_59", "NEF60_64",
              "NEF65","NEF66","NEF67","NEF68","NEF69",
              "NEF70_74", "NEF75_79", "NEF80_84", "NEF85_89", "NEF90_94", "NEF95_GT",
              "NEM0_34","NEM35_44", "NEM45_54", "NEM55_59", "NEM60_64",
              "NEM65","NEM66","NEM67","NEM68","NEM69",
              "NEM70_74", "NEM75_79", "NEM80_84", "NEM85_89", "NEM90_94", "NEM95_GT",
              "MCAID_FEMALE0_64","MCAID_FEMALE65","MCAID_FEMALE66_69",
              "MCAID_FEMALE70_74", "MCAID_FEMALE75_GT",
              "MCAID_MALE0_64","MCAID_MALE65","MCAID_MALE66_69",
              "MCAID_MALE70_74", "MCAID_MALE75_GT",
              "Origdis_female65", "Origdis_female66_69",
              "Origdis_female70_74","Origdis_female75_GT",
              "Origdis_male65", "Origdis_male66_69",
              "Origdis_male70_74","Origdis_male75_GT"]
  return reg_vars

def institutional_regression():
  # &INST_REG
  reg_vars = ["F0_34","F35_44", "F45_54", "F55_59", "F60_64", "F65_69",
              "F70_74", "F75_79", "F80_84", "F85_89", "F90_94", "F95_GT",
              "M0_34","M35_44", "M45_54", "M55_59", "M60_64", "M65_69",
              "M70_74", "M75_79", "M80_84", "M85_89", "M90_94", "M95_GT",
              "MCAID","ORIGDS",
              "DISABLED_HCC85", "DISABLED_PRESSURE_ULCER",
              "DISABLED_HCC161","DISABLED_HCC39",
              "DISABLED_HCC77", "DISABLED_HCC6",
              "CHF_COPD", "COPD_CARD_RESP_FAIL",
              "SEPSIS_PRESSURE_ULCER",
              "SEPSIS_ARTIF_OPENINGS",
              "ART_OPENINGS_PRESSURE_ULCER",
              "DIABETES_CHF",
              "COPD_ASP_SPEC_BACT_PNEUM",
              "ASP_SPEC_BACT_PNEUM_PRES_ULC",
              "SEPSIS_ASP_SPEC_BACT_PNEUM",
              "SCHIZOPHRENIA_COPD",
              "SCHIZOPHRENIA_CHF",
              "SCHIZOPHRENIA_SEIZURES",
              "HCC1","HCC2","HCC6","HCC8","HCC9","HCC10", "HCC11", "HCC12", 
              "HCC17", "HCC18", "HCC19", "HCC21", "HCC22", "HCC23", "HCC27", "HCC28",
              "HCC29", "HCC33", "HCC34", "HCC35", "HCC39", "HCC40", "HCC46", "HCC47", 
              "HCC48", "HCC51", "HCC52", "HCC54", "HCC55", "HCC57", "HCC58", "HCC70", 
              "HCC71", "HCC72", "HCC73", "HCC74", "HCC75", "HCC76", "HCC77", "HCC78", 
              "HCC79", "HCC80", "HCC82", "HCC83", "HCC84", "HCC85", "HCC86", "HCC87", 
              "HCC88", "HCC96", "HCC99", "HCC100","HCC103","HCC104","HCC106","HCC107",
              "HCC108","HCC110","HCC111","HCC112","HCC114","HCC115","HCC122","HCC124",
              "HCC134","HCC135","HCC136","HCC137","HCC138","HCC139","HCC140","HCC141",
              "HCC157","HCC158","HCC159","HCC160","HCC161","HCC162","HCC166","HCC167",
              "HCC169","HCC170","HCC173","HCC176","HCC186","HCC188","HCC189" ]
  return reg_vars 

pyDatalog.create_terms('CC,B,valid_community_variables,valid_institutional_variables,valid_new_enrolle_variables,indicator')


def load_score_concatenators():
  cvars = community_regression()
  ivars = institutional_regression()
  nevars = new_enrollee_regression()
  (valid_community_variables[B] == concat_(CC,key=CC,sep=',')) <= indicator(B,CC) & CC.in_(cvars)
  (valid_institutional_variables[B] == concat_(CC,key=CC,sep=',')) <= indicator(B,CC) & CC.in_(ivars)
  (valid_new_enrolle_variables[B] == concat_(CC,key=CC,sep=',')) <= indicator(B,CC) & CC.in_(nevars)

def load_rules():
  Ben = Beneficiary
  Diag = Diagnosis

  male(B) <=  (Ben.sex[B] == "male")
  female(B) <=  (Ben.sex[B] == "female")
  medicaid(B) <= (Ben.medicaid[B] == True)
  age(B,A) <= (Ben.age[B] == A)
  old_age_entitled(B) <= (Ben.original_reason_entitlement[B] == EntitlementReason.OASI)
  new_enrollee(B)  <= (Ben.newenrollee_medicaid[B] == True)

  #    %* disabled;
  #    DISABL = (&AGEF < 65 & &OREC ne "0");
  disabled(B) <= (Ben.age[B] < 65) & ~(old_age_entitled(B))
  #    %* originally disabled: CHANGED FIRST TIME FOR THIS SOFTWARE;
  #    ORIGDS  = (&OREC = '1')*(DISABL = 0);
  originally_disabled(B) <= (Ben.original_reason_entitlement[B] == EntitlementReason.DIB) & ~(disabled(B))

  beneficiary_has_cc(B,CC) <= (Diag.beneficiary[D] == B)  & edit(Diag.icdcode[D],Diag.codetype[D],B,CC)
  beneficiary_has_cc(B,CC) <= (Diag.beneficiary[D] == B)  & cc(Diag.icdcode[D],CC,
                                        Diag.codetype[D]) & ~(edit(Diag.icdcode[D],Diag.codetype[D],B,CC2))
  has_cc_that_overrides_this_one(B,CC) <=  beneficiary_has_cc(B,OT)  & overrides(OT,CC)
  beneficiary_has_hcc(B,CC) <= beneficiary_has_cc(B,CC) & ~( has_cc_that_overrides_this_one(B,CC))
  ben_hcc(B,CC) <= beneficiary_has_hcc(B,CC)

  edit(ICD,0,B,"48")  <= female(B) & (ICD.in_(["D66", "D67"]))
  edit(ICD,0,B,"112") <= (Ben.age[B] < 18) & (ICD.in_(["J410", 
                                 "J411", "J418", "J42",  "J430",
                                 "J431", "J432", "J438", "J439", "J440",
                                 "J441", "J449", "J982", "J983"]))

  # lines 363 - 368
  sepsis_card_resp_fail(CC,CC2) <= dc("sepsis",CC) & dc("card_resp_fail",CC2)
  cancer_immune(CC,CC2) <= dc("cancer",CC) & dc("immune",CC2)
  diabetes_chf(CC,CC2) <= dc("diabetes",CC) & dc("chf",CC2)
  chf_copd(CC,CC2) <= dc("chf",CC) & dc("copd",CC2)
  chf_renal(CC,CC2) <= dc("chf",CC) & dc("renal",CC2)
  copd_card_resp_fail(CC,CC2) <= dc("copd",CC) & dc("card_resp_fail",CC2)

  # PRESSURE_ULCER = MAX(HCC157, HCC158, HCC159, HCC160);
  sepsis_pressure_ulcer(CC,CC2) <= dc("sepsis",CC) & dc("pressure_ulcer",CC2) 
  sepsis_artif_openings(CC,"188") <= dc("sepsis",CC)
  art_openings_pressure_ulcer(CC,"188") <= dc("pressure_ulcer",CC)
  diabetes_chf(CC,CC2) <= dc("diabetes",CC) & dc("chf",CC2)
  copd_asp_spec_bact_pneum(CC,"114") <= dc("copd",CC)
  asp_spec_bact_pneum_pres_ulc(CC,"114") <= dc("pressure_ulcer",CC)
  sepsis_asp_spec_bact_pneum(CC,"114") <= dc("sepsis",CC)
  schizophrenia_copd(CC,"57") <= dc("copd",CC)
  schizophrenia_chf(CC,"57") <= dc("chf",CC)
  schizophrenia_seizures("79",CC) <= (CC == "57")

  # these predicates will be used to generate 
  # more specific predicates like "F0_34"
  sex_age_range("male",B,L,U) <= male(B) & age(B,A)& (A <= U) & (A > L) 
  sex_age_range("female",B,L,U) <= female(B) & age(B,A)& (A <= U) & (A > L) 
  sex_age(MF,B,A) <= sex_age_range(MF,B,(A+1),A)
  
  load_indicators()
  load_score_concatenators()

def load_indicators():
  indicator(B,'ART_OPENINGS_PRESSURE_ULCER') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & art_openings_pressure_ulcer(CC,CC2)
  indicator(B,'ASP_SPEC_BACT_PNEUM_PRES_ULC') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & asp_spec_bact_pneum_pres_ulc(CC,CC2)
  indicator(B,'CANCER_IMMUNE') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & cancer_immune(CC,CC2)
  indicator(B,'CHF_COPD') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & chf_copd(CC,CC2)
  indicator(B,'CHF_RENAL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & chf_renal(CC,CC2)
  indicator(B,'COPD_ASP_SPEC_BACT_PNEUM') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & copd_asp_spec_bact_pneum(CC,CC2)
  indicator(B,'COPD_CARD_RESP_FAIL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & copd_card_resp_fail(CC,CC2)
  indicator(B,'DIABETES_CHF') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & diabetes_chf(CC,CC2)
  indicator(B,'DISABLED_HCC110') <=  ben_hcc(B,'110') & disabled(B)
  indicator(B,'DISABLED_HCC161') <=  ben_hcc(B,'161') & disabled(B)
  indicator(B,'DISABLED_HCC176') <=  ben_hcc(B,'176') & disabled(B)
  indicator(B,'DISABLED_HCC34') <=  ben_hcc(B,'34') & disabled(B)
  indicator(B,'DISABLED_HCC39') <=  ben_hcc(B,'39') & disabled(B)
  indicator(B,'DISABLED_HCC46') <=  ben_hcc(B,'46') & disabled(B)
  indicator(B,'DISABLED_HCC54') <=  ben_hcc(B,'54') & disabled(B)
  indicator(B,'DISABLED_HCC55') <=  ben_hcc(B,'55') & disabled(B)
  indicator(B,'DISABLED_HCC6') <=  ben_hcc(B,'6') & disabled(B)
  indicator(B,'DISABLED_HCC77') <=  ben_hcc(B,'77') & disabled(B)
  indicator(B,'DISABLED_HCC85') <=  ben_hcc(B,'85') & disabled(B)
  indicator(B,'DISABLED_HCC85') <=  ben_hcc(B,CC) & dc(CC,'pressure_ulcer') & disabled(B)
  indicator(B,'F0_34') <=  sex_age_range('female',B,0,34)
  indicator(B,'F35_44') <=  sex_age_range('female',B,35,44)
  indicator(B,'F45_54') <=  sex_age_range('female',B,45,54)
  indicator(B,'F55_59') <=  sex_age_range('female',B,55,59)
  indicator(B,'F60_64') <=  sex_age_range('female',B,60,64)
  indicator(B,'F65_69') <=  sex_age_range('female',B,65,69)
  indicator(B,'F70_74') <=  sex_age_range('female',B,70,74)
  indicator(B,'F75_79') <=  sex_age_range('female',B,75,79)
  indicator(B,'F80_84') <=  sex_age_range('female',B,80,84)
  indicator(B,'F85_89') <=  sex_age_range('female',B,85,89)
  indicator(B,'F90_94') <=  sex_age_range('female',B,90,94)
  indicator(B,'F95_GT') <=  sex_age_range('female',B,95,99999)
  indicator(B,'HCC100') <=  ben_hcc(B,'100') 
  indicator(B,'HCC103') <=  ben_hcc(B,'103') 
  indicator(B,'HCC104') <=  ben_hcc(B,'104') 
  indicator(B,'HCC106') <=  ben_hcc(B,'106') 
  indicator(B,'HCC107') <=  ben_hcc(B,'107') 
  indicator(B,'HCC108') <=  ben_hcc(B,'108') 
  indicator(B,'HCC10') <=  ben_hcc(B,'10') 
  indicator(B,'HCC110') <=  ben_hcc(B,'110') 
  indicator(B,'HCC111') <=  ben_hcc(B,'111') 
  indicator(B,'HCC112') <=  ben_hcc(B,'112') 
  indicator(B,'HCC114') <=  ben_hcc(B,'114') 
  indicator(B,'HCC115') <=  ben_hcc(B,'115') 
  indicator(B,'HCC11') <=  ben_hcc(B,'11') 
  indicator(B,'HCC122') <=  ben_hcc(B,'122') 
  indicator(B,'HCC124') <=  ben_hcc(B,'124') 
  indicator(B,'HCC12') <=  ben_hcc(B,'12') 
  indicator(B,'HCC134') <=  ben_hcc(B,'134') 
  indicator(B,'HCC135') <=  ben_hcc(B,'135') 
  indicator(B,'HCC136') <=  ben_hcc(B,'136') 
  indicator(B,'HCC137') <=  ben_hcc(B,'137') 
  indicator(B,'HCC138') <=  ben_hcc(B,'138') 
  indicator(B,'HCC139') <=  ben_hcc(B,'139') 
  indicator(B,'HCC140') <=  ben_hcc(B,'140') 
  indicator(B,'HCC141') <=  ben_hcc(B,'141') 
  indicator(B,'HCC157') <=  ben_hcc(B,'157') 
  indicator(B,'HCC158') <=  ben_hcc(B,'158') 
  indicator(B,'HCC159') <=  ben_hcc(B,'159') 
  indicator(B,'HCC160') <=  ben_hcc(B,'160') 
  indicator(B,'HCC161') <=  ben_hcc(B,'161') 
  indicator(B,'HCC162') <=  ben_hcc(B,'162') 
  indicator(B,'HCC166') <=  ben_hcc(B,'166') 
  indicator(B,'HCC167') <=  ben_hcc(B,'167') 
  indicator(B,'HCC169') <=  ben_hcc(B,'169') 
  indicator(B,'HCC170') <=  ben_hcc(B,'170') 
  indicator(B,'HCC173') <=  ben_hcc(B,'173') 
  indicator(B,'HCC176') <=  ben_hcc(B,'176') 
  indicator(B,'HCC17') <=  ben_hcc(B,'17') 
  indicator(B,'HCC186') <=  ben_hcc(B,'186') 
  indicator(B,'HCC188') <=  ben_hcc(B,'188') 
  indicator(B,'HCC189') <=  ben_hcc(B,'189') 
  indicator(B,'HCC18') <=  ben_hcc(B,'18') 
  indicator(B,'HCC19') <=  ben_hcc(B,'19') 
  indicator(B,'HCC1') <=  ben_hcc(B,'1') 
  indicator(B,'HCC21') <=  ben_hcc(B,'21') 
  indicator(B,'HCC22') <=  ben_hcc(B,'22') 
  indicator(B,'HCC23') <=  ben_hcc(B,'23') 
  indicator(B,'HCC27') <=  ben_hcc(B,'27') 
  indicator(B,'HCC28') <=  ben_hcc(B,'28') 
  indicator(B,'HCC29') <=  ben_hcc(B,'29') 
  indicator(B,'HCC2') <=  ben_hcc(B,'2') 
  indicator(B,'HCC33') <=  ben_hcc(B,'33') 
  indicator(B,'HCC34') <=  ben_hcc(B,'34') 
  indicator(B,'HCC35') <=  ben_hcc(B,'35') 
  indicator(B,'HCC39') <=  ben_hcc(B,'39') 
  indicator(B,'HCC40') <=  ben_hcc(B,'40') 
  indicator(B,'HCC46') <=  ben_hcc(B,'46') 
  indicator(B,'HCC47') <=  ben_hcc(B,'47') 
  indicator(B,'HCC48') <=  ben_hcc(B,'48') 
  indicator(B,'HCC51') <=  ben_hcc(B,'51') 
  indicator(B,'HCC52') <=  ben_hcc(B,'52') 
  indicator(B,'HCC54') <=  ben_hcc(B,'54') 
  indicator(B,'HCC55') <=  ben_hcc(B,'55') 
  indicator(B,'HCC57') <=  ben_hcc(B,'57') 
  indicator(B,'HCC58') <=  ben_hcc(B,'58') 
  indicator(B,'HCC6') <=  ben_hcc(B,'6') 
  indicator(B,'HCC70') <=  ben_hcc(B,'70') 
  indicator(B,'HCC71') <=  ben_hcc(B,'71') 
  indicator(B,'HCC72') <=  ben_hcc(B,'72') 
  indicator(B,'HCC73') <=  ben_hcc(B,'73') 
  indicator(B,'HCC74') <=  ben_hcc(B,'74') 
  indicator(B,'HCC75') <=  ben_hcc(B,'75') 
  indicator(B,'HCC76') <=  ben_hcc(B,'76') 
  indicator(B,'HCC77') <=  ben_hcc(B,'77') 
  indicator(B,'HCC78') <=  ben_hcc(B,'78') 
  indicator(B,'HCC79') <=  ben_hcc(B,'79') 
  indicator(B,'HCC80') <=  ben_hcc(B,'80') 
  indicator(B,'HCC82') <=  ben_hcc(B,'82') 
  indicator(B,'HCC83') <=  ben_hcc(B,'83') 
  indicator(B,'HCC84') <=  ben_hcc(B,'84') 
  indicator(B,'HCC85') <=  ben_hcc(B,'85') 
  indicator(B,'HCC86') <=  ben_hcc(B,'86') 
  indicator(B,'HCC87') <=  ben_hcc(B,'87') 
  indicator(B,'HCC88') <=  ben_hcc(B,'88') 
  indicator(B,'HCC8') <=  ben_hcc(B,'8') 
  indicator(B,'HCC96') <=  ben_hcc(B,'96') 
  indicator(B,'HCC99') <=  ben_hcc(B,'99') 
  indicator(B,'HCC9') <=  ben_hcc(B,'9') 
  indicator(B,'M0_34') <=  sex_age_range('male',B,0,34)
  indicator(B,'M35_44') <=  sex_age_range('male',B,35,44)
  indicator(B,'M45_54') <=  sex_age_range('male',B,45,54)
  indicator(B,'M55_59') <=  sex_age_range('male',B,55,59)
  indicator(B,'M60_64') <=  sex_age_range('male',B,60,64)
  indicator(B,'M65_69') <=  sex_age_range('male',B,65,69)
  indicator(B,'M70_74') <=  sex_age_range('male',B,70,74)
  indicator(B,'M75_79') <=  sex_age_range('male',B,75,79)
  indicator(B,'M80_84') <=  sex_age_range('male',B,80,84)
  indicator(B,'M85_89') <=  sex_age_range('male',B,85,89)
  indicator(B,'M90_94') <=  sex_age_range('male',B,90,94)
  indicator(B,'M95_GT') <=  sex_age_range('male',B,95,99999)
  indicator(B,'MCAID_FEMALE0_64') <= medicaid(B) & sex_age_range('female',B,0,64)
  indicator(B,'MCAID_FEMALE65') <=  medicaid(B) & sex_age('female',B,65)
  indicator(B,'MCAID_FEMALE66_69') <=  medicaid(B) & sex_age_range('female',B,66,69)
  indicator(B,'MCAID_FEMALE70_74') <= medicaid(B) & sex_age_range('female',B,70,74)
  indicator(B,'MCAID_FEMALE75_GT') <=  medicaid(B) & sex_age_range('female',B,75,999)
  indicator(B,'MCAID_Female_Aged') <=   medicaid(B) & ~disabled(B) & female(B)
  indicator(B,'MCAID_Female_Disabled') <=  medicaid(B) & disabled(B) & male(B)
  indicator(B,'MCAID') <= medicaid(B) 
  indicator(B,'MCAID_MALE0_64') <= medicaid(B) & sex_age_range('male',B,0,64)
  indicator(B,'MCAID_MALE65') <=  medicaid(B) & sex_age('male',B,65)
  indicator(B,'MCAID_MALE66_69') <=  medicaid(B) & sex_age_range('male',B,66,69)
  indicator(B,'MCAID_MALE70_74') <= medicaid(B) & sex_age_range('male',B,70,74)
  indicator(B,'MCAID_MALE75_GT') <=  medicaid(B) & sex_age_range('male',B,75,999)
  indicator(B,'MCAID_Male_Aged') <=  medicaid(B) & ~disabled(B) & female(B)
  indicator(B,'MCAID_Male_Disabled') <=   medicaid(B) & disabled(B) & male(B)
  indicator(B,'NEM0_34') <=  sex_age_range("male",B,0,34)
  indicator(B,'NEM35_44') <=  sex_age_range("male",B,35,44)
  indicator(B,'NEM45_54') <=  sex_age_range("male",B,45,54)
  indicator(B,'NEM55_59') <=  sex_age_range("male",B,55,59)
  indicator(B,'NEM60_64') <=  sex_age_range("male",B,60,63)
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC NE '0') NE_AGESEX = 5;
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC='0')    NE_AGESEX = 6;
  indicator(B,'NEM60_64') <=  sex_age("male",B,64) & ~(old_age_entitled(B))
  indicator(B,'NEM65') <=  sex_age("male",B,64) & old_age_entitled(B)
  indicator(B,'NEM65') <=  sex_age("male",B,65)
  indicator(B,'NEM66') <=  sex_age("male",B,66)
  indicator(B,'NEM67') <=  sex_age("male",B,67)
  indicator(B,'NEM68') <=  sex_age("male",B,68)
  indicator(B,'NEM69') <=  sex_age("male",B,69)
  indicator(B,'NEM70_74') <=  sex_age_range("male",B,70,74)
  indicator(B,'NEM75_79') <=  sex_age_range("male",B,75,79)
  indicator(B,'NEM80_84') <=  sex_age_range("male",B,80,84)
  indicator(B,'NEM85_89') <=  sex_age_range("male",B,85,89)
  indicator(B,'NEM90_94') <=  sex_age_range("male",B,90,94)
  indicator(B,'NEM95_GT') <=  sex_age_range("male",B,95,999)
  indicator(B,'NEF0_34') <=  sex_age_range("female",B,0,34)
  indicator(B,'NEF35_44') <=  sex_age_range("female",B,35,44)
  indicator(B,'NEF45_54') <=  sex_age_range("female",B,45,54)
  indicator(B,'NEF55_59') <=  sex_age_range("female",B,55,59)
  indicator(B,'NEF60_64') <=  sex_age_range("female",B,60,63)
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC NE '0') NE_AGESEX = 5;
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC='0')    NE_AGESEX = 6;
  indicator(B,'NEF60_64') <=  sex_age("female",B,64) & ~(old_age_entitled(B))
  indicator(B,'NEF65') <=  sex_age("female",B,64) & old_age_entitled(B)
  indicator(B,'NEF65') <=  sex_age("female",B,65)
  indicator(B,'NEF66') <=  sex_age("female",B,66)
  indicator(B,'NEF67') <=  sex_age("female",B,67)
  indicator(B,'NEF68') <=  sex_age("female",B,68)
  indicator(B,'NEF69') <=  sex_age("female",B,69)
  indicator(B,'NEF70_74') <=  sex_age_range("female",B,70,74)
  indicator(B,'NEF75_79') <=  sex_age_range("female",B,75,79)
  indicator(B,'NEF80_84') <=  sex_age_range("female",B,80,84)
  indicator(B,'NEF85_89') <=  sex_age_range("female",B,85,89)
  indicator(B,'NEF90_94') <=  sex_age_range("female",B,90,94)
  indicator(B,'NEF95_GT') <=  sex_age_range("female",B,95,999)
  indicator(B,'Origdis_female65') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'Origdis_female66_69') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'Origdis_female70_74') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'Origdis_female75_GT') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'Origdis_male65') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'Origdis_male66_69') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'Origdis_male70_74') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'Origdis_male75_GT') <=  originally_disabled(B) & indicator(B, )
  indicator(B,'ORIGDS') <= originally_disabled(B) 
  indicator(B,'OriginallyDisabled_Female') <=  originally_disabled(B) & female(B)
  indicator(B,'OriginallyDisabled_Male') <=  originally_disabled(B) & male(B)
  indicator(B,'SCHIZOPHRENIA_CHF') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & schizophrenia_chf(CC,CC2) 
  indicator(B,'SCHIZOPHRENIA_COPD') <= ben_hcc(B,CC) & ben_hcc(B,CC2) & schizophrenia_copd(CC,CC2) 
  indicator(B,'SCHIZOPHRENIA_SEIZURES') <= ben_hcc(B,CC) & ben_hcc(B,CC2) & schizophrenia_seizures(CC,CC2) 
  indicator(B,'SEPSIS_ARTIF_OPENINGS') <= ben_hcc(B,CC) & ben_hcc(B,CC2) & sepsis_artif_openings(CC,CC2) 
  indicator(B,'SEPSIS_ASP_SPEC_BACT_PNEUM') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & sepsis_asp_spec_bact_pneum(CC,CC2)
  indicator(B,'SEPSIS_CARD_RESP_FAIL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & sepsis_card_resp_fail(CC,CC2)

load_facts()
load_rules()


####################################################

jane = Beneficiary(2,"female","19740824",EntitlementReason.DIB,True)
jane.add_diagnosis(Diagnosis(jane,"D66",ICDType.TEN))  
jane.add_diagnosis(Diagnosis(jane,"C182",ICDType.TEN))  

daniel = Beneficiary(1,"male","19740824",EntitlementReason.DIB)
daniel.add_diagnosis(Diagnosis(daniel,"A0223",ICDType.TEN))  # 51
daniel.add_diagnosis(Diagnosis(daniel,"A0224",ICDType.TEN))  # 52
daniel.add_diagnosis(Diagnosis(daniel,"D66",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C163",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C163",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C182",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C800",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"A072",ICDType.TEN))  
bob = Beneficiary(3,"male","20040824",EntitlementReason.DIB,True)
bob.add_diagnosis(Diagnosis(bob,"A0223",ICDType.TEN))
bob.add_diagnosis(Diagnosis(bob,"A0224",ICDType.TEN))
jacob = Beneficiary(4,"male","1940824",EntitlementReason.DIB,True)

print("bottom")

def a(query):
  answer =pyDatalog.ask(query) 
  if answer != None:
    return (True, answer.answers)
  else:
    return (False,None)

def a2(results):
  if len(results) > 0:
    return True
  else:
    return False



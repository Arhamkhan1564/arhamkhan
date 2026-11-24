"""ASK-T2D exploratory NHANES temporal benchmark; not clinical validation."""
from pathlib import Path
import io, json
import pandas as pd
import numpy as np
import requests
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss
from sklearn.model_selection import train_test_split

ROOT="https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{year}/DataFiles/{name}.xpt"
FILES={
"dev":("2015",["DEMO_I","BMX_I","GHB_I","DIQ_I"]),
"test":("2017",["P_DEMO","P_BMX","P_GHB","P_DIQ"])
}
BASE=["RIDAGEYR","RIAGENDR"]
EXTRA=["BMXBMI","BMXWAIST"]

def xpt(year,name):
    d=Path("data");d.mkdir(exist_ok=True)
    path=d/(name+".xpt")
    if not path.exists():
        url=ROOT.format(year=year,name=name)
        r=requests.get(url,timeout=90);r.raise_for_status()
        if len(r.content)<1000: raise ValueError("Too small: "+url)
        path.write_bytes(r.content)
    return pd.read_sas(path,format="xport")

def load(which):
    year,names=FILES[which]
    frames=[xpt(year,n) for n in names]
    df=frames[0]
    for right in frames[1:]: df=df.merge(right,on="SEQN",how="left",validate="one_to_one")
    required=BASE+EXTRA+["LBXGH","DIQ010"]
    missing=set(required)-set(df)
    if missing: raise ValueError(f"Missing fields: {missing}")
    df=df[(df.RIDAGEYR>=20)&(df.LBXGH.notna())&(df.DIQ010==2)].copy()
    df["y"]=(df.LBXGH>=6.5).astype(int)
    if df.y.nunique()!=2: raise ValueError("Only one label class")
    return df

def predict(train,test,cols):
    pipe=make_pipeline(SimpleImputer(strategy="median"),StandardScaler(),LogisticRegression(max_iter=3000))
    pipe.fit(train[cols],train.y)
    return pipe.predict_proba(test[cols])[:,1]

def score(y,p):
    return {"n":len(y),"n_positive":int(sum(y)),"auroc":float(roc_auc_score(y,p)),
            "average_precision":float(average_precision_score(y,p)),
            "brier":float(brier_score_loss(y,p)),
            "log_loss":float(log_loss(y,p,labels=[0,1]))}

def main():
    dev=load("dev");test=load("test")
    train,val=train_test_split(dev,test_size=0.25,random_state=2026,stratify=dev.y)
    policy={}
    for feature in EXTRA:
        policy[feature]={"validation":score(val.y,predict(train,val,BASE+[feature])),
                         "temporal_test":score(test.y,predict(train,test,BASE+[feature]))}
    chosen=min(EXTRA,key=lambda name:policy[name]["validation"]["brier"])
    results={"status":"NHANES experimental metrics; non-clinical",
             "cycles":{"development":"2015-2016","temporal_test":"2017-March 2020 pre-pandemic"},
             "definition":"Age >=20, DIQ010=2, nonmissing HbA1c; reference HbA1c >=6.5%",
             "sample_sizes":{"development":len(dev),"temporal_test":len(test)},
             "baseline":score(test.y,predict(train,test,BASE)),
             "candidate_extra_tests":policy,"selected_by_validation_brier":chosen,
             "all_features":score(test.y,predict(train,test,BASE+EXTRA)),
             "limitations":["Selection of one global measurement, not adaptive per-person decisions",
                "No economic test costs or calibrated abstention evaluated",
                "NHANES complex sampling weights not modelled; no prevalence inference",
                "Not a medical device or prospective clinical validation"]}
    path=Path("results/nhanes_results.json");path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=="__main__": main()

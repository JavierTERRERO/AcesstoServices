import os
from pathlib import Path
import pandas as pd 
import numpy as np

wd = Path(__file__).resolve().parents[3]
os.chdir(wd)

private = pd.read_csv("Addresses/Schools/raw_data/SCUANAGRAFEPAR20262720260901.csv")
public = pd.read_csv("Addresses/Schools/raw_data/SCUANAGRAFESTAT20262720260901.csv")

private = private[['CODICESCUOLA', 'DENOMINAZIONESCUOLA', 'INDIRIZZOSCUOLA',
                   'CODICECOMUNESCUOLA', 'REGIONE', 'DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA']]
private = private.rename(columns={
    'CODICESCUOLA': 'id',
    'DENOMINAZIONESCUOLA': 'name',
    'INDIRIZZOSCUOLA': 'address',
    'CODICECOMUNESCUOLA': 'municipality_code',
    'REGIONE': 'region',
    'DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA': 'level_or'
})
private = private[private['level_or'] == 'SCUOLA PRIMARIA NON STATALE']
private['sector'] = 'private'

public = public[['CODICEISTITUTORIFERIMENTO', 'DENOMINAZIONEISTITUTORIFERIMENTO', 'INDIRIZZOSCUOLA',
                   'CODICECOMUNESCUOLA', 'REGIONE', 'DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA']]
public = public.rename(columns={
    'CODICEISTITUTORIFERIMENTO': 'id',
    'DENOMINAZIONEISTITUTORIFERIMENTO': 'name',
    'INDIRIZZOSCUOLA': 'address',
    'CODICECOMUNESCUOLA': 'municipality_code',
    'REGIONE': 'region',
    'DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA': 'level_or'
})
public = public[(public['level_or'] == 'SCUOLA PRIMARIA') | (public['level_or'] == 'SCUOLA PRIMO GRADO')]
public['sector'] = 'public'

data = pd.concat([private, public], ignore_index=True)
data.to_csv("Addresses/Schools/old/ita_schools.csv", index=False)
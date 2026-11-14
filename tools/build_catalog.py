import csv, hashlib, io, json, os, pathlib, sqlite3, urllib.request, datetime
URL = 'https://drive.aifa.gov.it/farmaci/confezioni_fornitura.csv'
def build():
    local = os.environ.get('AIFA_CSV')
    if local:
        raw = pathlib.Path(local).read_bytes()
    else:
        req = urllib.request.Request(URL, headers={'User-Agent':'FarmaciDiCasa/2.0'})
        with urllib.request.urlopen(req, timeout=180) as r: raw = r.read()
    if len(raw) < 1000 or raw.startswith(b'version https://git-lfs'):
        raise RuntimeError('CSV AIFA vuoto o puntatore Git LFS: compilazione interrotta')
    try: text = raw.decode('utf-8-sig')
    except UnicodeDecodeError: text = raw.decode('cp1252')
    dialect = csv.Sniffer().sniff(text.splitlines()[0], delimiters=";,\t")
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    required = {'CODICE_AIC','DENOMINAZIONE','DESCRIZIONE'}
    if not required.issubset(set(reader.fieldnames or [])):
        raise RuntimeError('Intestazioni AIFA non riconosciute: '+str(reader.fieldnames))
    out = pathlib.Path('app/src/main/assets'); out.mkdir(parents=True, exist_ok=True)
    path = out/'catalog.db'
    if path.exists(): path.unlink()
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE drugs(aic TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, ingredient TEXT, status TEXT, company TEXT, leaflet TEXT)')
    con.execute('CREATE INDEX drugs_name ON drugs(name COLLATE NOCASE)')
    n=0
    for row in reader:
        aic=row['CODICE_AIC'].strip().strip('"')
        if not aic.isdigit() or len(aic)>9: continue
        aic=aic.zfill(9)
        con.execute('INSERT OR REPLACE INTO drugs VALUES(?,?,?,?,?,?,?)', (aic,row['DENOMINAZIONE'].strip(),row['DESCRIZIONE'].strip(),row.get('PA_ASSOCIATI',''),row.get('STATO_AMMINISTRATIVO',''),row.get('RAGIONE_SOCIALE',''),row.get('LINK_FI','')))
        n+=1
    con.commit()
    count=con.execute('SELECT count(*) FROM drugs').fetchone()[0]
    if count<1000: raise RuntimeError('Catalogo troppo piccolo: '+str(count))
    con.execute('VACUUM');con.close()
    info={'source':URL,'downloaded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'packages':count,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (out/'catalog-info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(info,indent=2))
if __name__=='__main__': build()

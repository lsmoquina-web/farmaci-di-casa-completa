"""Farmaci di casa 2.2: rosa, preferiti e inserimento rapido.
Da eseguire nella radice del repository al posto di tools/restyle.py.
Richiede che tools/restyle.py rimanga presente.
"""
from pathlib import Path
import re
import restyle as base

MARKER='// FARMACI_ROSA_220'

EDIT=r"""void edit(JSONObject source,boolean existing){
 shell(existing?"Modifica confezione":"Nuova confezione",source.optString("name"));
 text(body,source.optString("description")+"\nAIC "+source.optString("aic"),16,INK);
 EditText expiry=dateField(body,"Scadenza della scatola",source.optString("expiry",""),false);
 text(body,"Se è indicato solo mese/anno, seleziona l’ultimo giorno del mese.",12,MUTED);
 CheckBox precise=new CheckBox(this);precise.setText("Voglio contare compresse, ml o altre unità");precise.setTextColor(INK);
 boolean simple=source.optString("unit","confezioni").equals("confezioni");precise.setChecked(existing&&!simple);body.addView(precise);
 TextView quick=text(body,existing&&simple?"Conteggio attuale: "+number(source.optDouble("qty"))+" confezioni.":"Inserimento rapido: salvi 1 confezione, non un numero presunto di compresse o ml.",14,MUTED);
 LinearLayout quantities=new LinearLayout(this);quantities.setOrientation(1);body.addView(quantities);
 EditText qty=field(quantities,"Quantità residua",existing?number(source.optDouble("qty")):"",true);
 EditText unit=field(quantities,"Unità",""+source.optString("unit",""),false);
 if(!existing||simple)unit.setText("");
 text(quantities,"Scelte rapide per l’unità:",13,MUTED);
 Spinner units=new Spinner(this);String[] choices={"Scegli…","compresse","capsule","ml","bustine","gocce","dosi","grammi","cerotti"};
 units.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,choices));quantities.addView(units);
 units.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){public void onItemSelected(android.widget.AdapterView<?> p,View v,int position,long id){if(position>0)unit.setText(choices[position]);}public void onNothingSelected(android.widget.AdapterView<?> p){}});
 Runnable mode=()->{quantities.setVisibility(precise.isChecked()?View.VISIBLE:View.GONE);quick.setVisibility(precise.isChecked()?View.GONE:View.VISIBLE);};mode.run();precise.setOnCheckedChangeListener((v,checked)->mode.run());
 if(existing){precise.setEnabled(false);text(body,"La modalità di conteggio di una confezione già salvata resta invariata, per mantenere coerente lo storico.",12,MUTED);if(!store.history(source.optLong("id")).isEmpty())unit.setEnabled(false);}
 LinearLayout advanced=new LinearLayout(this);advanced.setOrientation(1);
 button(body,"Apertura e altri dettagli (facoltativi)",()->advanced.setVisibility(advanced.getVisibility()==View.VISIBLE?View.GONE:View.VISIBLE));body.addView(advanced);advanced.setVisibility(View.GONE);
 EditText opened=dateField(advanced,"Data di apertura",source.optString("opened",""),true);
 EditText days=field(advanced,"Giorni dopo apertura: solo se indicati nel foglietto",source.optInt("days",0)>0?""+source.optInt("days"):"",true);
 text(advanced,"Se lasci vuoto il periodo dopo apertura, l’app considera solo la scadenza della scatola: non significa che il prodotto aperto duri fino a quella data.",13,MUTED);
 EditText minimum=field(advanced,"Avvisami quando il residuo è uguale o inferiore a",existing?number(source.optDouble("minimum")):"0",true);
 text(advanced,"La soglia usa l’unità scelta: confezioni oppure compresse, ml, ecc. Il valore iniziale 0 avvisa all’esaurimento.",12,MUTED);
 EditText quickQty;if(existing&&simple)quickQty=field(advanced,"Residuo in confezioni (correzione manuale)",number(source.optDouble("qty")),true);else{quickQty=new EditText(this);quickQty.setText("1");}
 EditText lot=field(advanced,"Lotto",source.optString("lot",""),false),notes=field(advanced,"Note",source.optString("notes",""),false);
 button(body,existing?"Salva modifiche":"Aggiungi all’armadietto",()->{try{
  JSONObject b=new JSONObject();if(existing)b.put("id",source.getLong("id"));for(String k:new String[]{"aic","name","description"})b.put(k,source.getString(k));
  b.put("qty",precise.isChecked()?decimal(qty):decimal(quickQty));
  b.put("unit",precise.isChecked()?unit.getText().toString().trim():"confezioni");
  b.put("minimum",minimum.getText().toString().trim().isEmpty()?0:decimal(minimum));
  b.put("expiry",expiry.getText().toString());b.put("opened",opened.getText().toString());
  b.put("days",days.getText().toString().trim().isEmpty()?0:Integer.parseInt(days.getText().toString().trim()));
  b.put("lot",lot.getText().toString());b.put("notes",notes.getText().toString());
  Store.validateBox(b);long id=store.save(b);detail(id);
 }catch(Exception e){error("Seleziona la scadenza. Se hai attivato il conteggio dettagliato, inserisci quantità e unità.\n"+e.getMessage());}});
 button(body,"Annulla",()->{if(existing)detail(source.optLong("id"));else home();});
}"""

RENDER=r"""void renderBoxes(LinearLayout rows,List<JSONObject> boxes){
 rows.removeAllViews();if(boxes.isEmpty()){text(rows,"Nessuna confezione. Aggiungi un medicinale per iniziare.",17,MUTED);return;}
 for(JSONObject b:boxes){LinearLayout c=card(rows);favoriteButton(c,b,null);text(c,b.optString("name"),20,INK).setTypeface(null,Typeface.BOLD);
 text(c,b.optString("description"),14,MUTED);text(c,number(b.optDouble("qty"))+" "+b.optString("unit")+" · scade "+date(Store.effective(b)),16,INK);
 String state=Store.soon(b)?(Store.effective(b).isBefore(LocalDate.now())?"Scaduto / oltre il limite d’uso":"Da controllare entro 30 giorni"):"";
 if(Store.low(b))state+=(state.isEmpty()?"":" · ")+"Scorta bassa";if(!state.isEmpty())text(c,state,14,0xffa14625);
 c.setOnClickListener(v->detail(b.optLong("id")));
 }
}"""

UI_EXTRA=r"""
 // FARMACI_ROSA_220
 void favoriteButton(LinearLayout parent,JSONObject drug,Runnable after){
  LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.END);parent.addView(row,new LinearLayout.LayoutParams(-1,-2));
  Button heart=new Button(this);heart.setAllCaps(false);heart.setTextSize(26);heart.setTextColor(0xffb33868);heart.setBackground(bg(0xffffe5ef,18));heart.setTag("favorite:"+drug.optString("aic"));
  updateHeart(heart,drug.optString("aic"));row.addView(heart,new LinearLayout.LayoutParams(dp(56),dp(48)));
  heart.setOnClickListener(v->{store.toggleFavorite(drug);refreshHearts(page,drug.optString("aic"));if(after!=null)after.run();});
 }
 void updateHeart(Button heart,String aic){boolean saved=store.isFavorite(aic);heart.setText(saved?"\u2665":"\u2661");heart.setContentDescription(saved?"Rimuovi dai preferiti":"Aggiungi ai preferiti");}
 void refreshHearts(View view,String aic){if(view instanceof Button&&("favorite:"+aic).equals(view.getTag()))updateHeart((Button)view,aic);if(view instanceof android.view.ViewGroup){android.view.ViewGroup group=(android.view.ViewGroup)view;for(int i=0;i<group.getChildCount();i++)refreshHearts(group.getChildAt(i),aic);}}
 void favorites(){
  shell("I tuoi preferiti","I medicinali che vuoi ritrovare al volo");
  text(body,"Il cuore salva il medicinale per AIC, non una singola scatola. Aggiungere un preferito non modifica l’inventario.",14,MUTED);
  List<JSONObject> list=store.favorites();
  if(list.isEmpty())text(body,"Tocca il cuoricino nell’armadietto o nei risultati della ricerca per iniziare.",17,INK);
  for(JSONObject drug:list){LinearLayout c=card(body);favoriteButton(c,drug,this::favorites);text(c,drug.optString("name"),20,INK).setTypeface(null,Typeface.BOLD);text(c,drug.optString("description"),15,MUTED);text(c,"AIC "+drug.optString("aic"),13,MUTED);
   button(c,"Aggiungi una confezione",()->{if(catalog==null){error("Attendi la preparazione del catalogo");return;}JSONObject current=catalog.find(drug.optString("aic"));if(current==null){error("Questa voce non è più presente nel catalogo. Cerca il medicinale e verifica la confezione.");return;}confirmDrug(current);});
  }
  button(body,"Cerca nel catalogo",this::search);button(body,"Torna all’armadietto",this::home);
 }
"""

FAVORITE_SCHEMA='CREATE TABLE IF NOT EXISTS favorites(aic TEXT PRIMARY KEY,name TEXT NOT NULL,description TEXT NOT NULL,status TEXT NOT NULL)'
STORE_EXTRA=r"""
 public boolean isFavorite(String aic){try(Cursor c=getReadableDatabase().rawQuery("SELECT 1 FROM favorites WHERE aic=?",new String[]{aic})){return c.moveToFirst();}}
 public void toggleFavorite(JSONObject drug){String aic=drug.optString("aic");if(!aic.matches("[0-9]{9}"))throw new IllegalArgumentException("AIC non valido");SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try{if(isFavorite(aic))d.delete("favorites","aic=?",new String[]{aic});else{ContentValues v=new ContentValues();v.put("aic",aic);v.put("name",drug.optString("name"));v.put("description",drug.optString("description"));v.put("status",drug.optString("status",""));d.insertOrThrow("favorites",null,v);}d.setTransactionSuccessful();}finally{d.endTransaction();}}
 public List<JSONObject> favorites(){List<JSONObject> out=new ArrayList<>();try(Cursor c=getReadableDatabase().rawQuery("SELECT * FROM favorites ORDER BY name,description",null)){while(c.moveToNext())out.add(object(c));}catch(JSONException e){throw new RuntimeException(e);}return out;}
"""

RESTORE=r"""public void restore(JSONObject r)throws Exception {
 if(!r.getString("format").equals("farmaci-di-casa")||r.getInt("version")!=1)throw new Exception("Formato backup non supportato");
 JSONArray bs=r.getJSONArray("boxes"),us=r.getJSONArray("uses"),fs=r.has("favorites")?r.getJSONArray("favorites"):new JSONArray();Set<Long> ids=new HashSet<>(),uids=new HashSet<>();Set<String> aids=new HashSet<>();
 for(int i=0;i<bs.length();i++){JSONObject b=bs.getJSONObject(i);validateBox(b);long id=b.getLong("id");if(id<=0||!ids.add(id))throw new Exception("ID confezione duplicato/non valido");}
 for(int i=0;i<us.length();i++){JSONObject u=us.getJSONObject(i);long id=u.getLong("id");if(id<=0||!uids.add(id)||!ids.contains(u.getLong("box"))||!Double.isFinite(u.getDouble("amount"))||u.getDouble("amount")<=0)throw new Exception("Registro non valido");Instant.parse(u.getString("at"));if(u.getInt("undone")!=0&&u.getInt("undone")!=1)throw new Exception("Annullamento non valido");}
 for(int i=0;i<fs.length();i++){JSONObject f=fs.getJSONObject(i);String aic=f.getString("aic");if(!aic.matches("[0-9]{9}")||!aids.add(aic)||f.getString("name").trim().isEmpty())throw new Exception("Preferiti non validi");f.getString("description");f.getString("status");}
 SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try{
  d.delete("uses",null,null);d.delete("boxes",null,null);d.delete("favorites",null,null);
  for(int i=0;i<bs.length();i++){JSONObject b=bs.getJSONObject(i);ContentValues v=new ContentValues();for(String k:new String[]{"aic","name","description","unit","expiry","opened","lot","notes"})v.put(k,b.getString(k));v.put("id",b.getLong("id"));v.put("qty",b.getDouble("qty"));v.put("minimum",b.getDouble("minimum"));v.put("days",b.getInt("days"));d.insertOrThrow("boxes",null,v);}
  for(int i=0;i<us.length();i++){JSONObject u=us.getJSONObject(i);d.execSQL("INSERT INTO uses(id,box,amount,at,undone) VALUES(?,?,?,?,?)",new Object[]{u.getLong("id"),u.getLong("box"),u.getDouble("amount"),u.getString("at"),u.getInt("undone")});}
  for(int i=0;i<fs.length();i++){JSONObject f=fs.getJSONObject(i);ContentValues v=new ContentValues();for(String k:new String[]{"aic","name","description","status"})v.put(k,f.getString(k));d.insertOrThrow("favorites",null,v);}
  d.setTransactionSuccessful();
 }finally{d.endTransaction();}
}"""

def once(s,old,new):
 if s.count(old)!=1:raise RuntimeError('Sorgente inatteso: '+old[:95]+'. Nessuna modifica salvata.')
 return s.replace(old,new,1)

def patch_main(source):
 if MARKER in source:return source
 source=base.patch(source)
 source=base.replace_method(source,'void edit(JSONObject source,boolean existing)',EDIT)
 source=base.replace_method(source,'void renderBoxes(LinearLayout rows,List<JSONObject> boxes)',RENDER)
 source=once(source,'button(body,"+ Aggiungi medicinale",this::addChoice);','button(body,"+ Aggiungi medicinale",this::addChoice);button(body,"\\u2661 Preferiti",this::favorites);'.replace('\\u2661',r'\u2661'))
 source=once(source,'text(c,b.optString("name"),19,INK);','favoriteButton(c,b,null);text(c,b.optString("name"),19,INK);')
 source=once(source,'LinearLayout c=card(body);text(c,number(b.optDouble("qty"))','LinearLayout c=card(body);favoriteButton(c,b,null);text(c,number(b.optDouble("qty"))')
 source=source.replace('Il backup contiene inventario e registro utilizzi, non il catalogo.','Il backup contiene inventario, registro utilizzi e preferiti, non il catalogo.')
 source=source.replace('Il ripristino sostituisce tutto l’inventario e lo storico.','Il ripristino sostituisce inventario, storico e preferiti. I vecchi backup senza preferiti ripristinano una lista preferiti vuota.')
 palette={
 '0xff117969':'0xffae426b','0xff183730':'0xff51283a','0xff64766f':'0xff815c6d','0xfff4f7f5':'0xffffe6ef',
 '0xffe8f1ee':'0xffffdce9','0xff16796d':'0xffae426b','0xff266e87':'0xffbd668b','0xfaffffff':'0xfffff1f6','0xffdfeae6':'0xffefc6d7',
 '0xff123f3c':'0xff7f3155','0xff1b7069':'0xffa54870','0xff377a95':'0xffbe7398','0xffcde9e3':'0xffffe2ec','0xffe2f1ee':'0xffffedf4',
 '0xffedf7f3':'0xffffdce9','0xfff7f9fd':'0xffffe9f1','0xffe8f1f5':'0xfff3d7e9','0x0c238e7b':'0x12bd5685','0x0b567db0':'0x129a5a9f',
 '0xfff5f7f8':'0xffffe8f0','0xffcedbd7':'0xffdaa9bf'}
 for old,new in palette.items():source=source.replace(old,new)
 source=source.replace('Versione app 2.1.0','Versione app 2.2.0')
 end=source.rfind('}')
 return source[:end]+UI_EXTRA+'\n'+source[end:]

def patch_store(source):
 if '// FAVORITES_SCHEMA_2' in source:return source
 source=once(source,'super(c,"home.db",null,1);','super(c,"home.db",null,2);')
 # Add the new table without rebuilding either of the existing tables.
 begin=source.index('public void onCreate(SQLiteDatabase d)')
 end=source.index(' public void onUpgrade',begin)
 part=source[begin:end];closing=part.rfind('}')
 part=part[:closing]+' d.execSQL("'+FAVORITE_SCHEMA+'");\n '+part[closing:]
 source=source[:begin]+part+source[end:]
 source=base.replace_method(source,'public void onUpgrade(SQLiteDatabase d,int a,int b)','public void onUpgrade(SQLiteDatabase d,int a,int b){if(a<2)d.execSQL("'+FAVORITE_SCHEMA+'");}')
 source=once(source,'root.put("uses",uses);return root;','root.put("uses",uses);root.put("favorites",new JSONArray(favorites()));return root;')
 source=base.replace_method(source,'public void restore(JSONObject r)throws Exception',RESTORE)
 end=source.rfind('}')
 return source[:end]+'\n // FAVORITES_SCHEMA_2\n'+STORE_EXTRA+'\n'+source[end:]

def main():
 java=Path('app/src/main/java/it/farmacidicasa/MainActivity.java');store=java.with_name('Store.java');gradle=Path('app/build.gradle')
 # Prepare all changes in memory before writing any file.
 new_java=patch_main(java.read_text(encoding='utf-8'));new_store=patch_store(store.read_text(encoding='utf-8'))
 build=gradle.read_text(encoding='utf-8');build=re.sub(r'\bversionCode\s+(200|201)\b','versionCode 202',build);build=re.sub(r"versionName '2\.[01]\.0'","versionName '2.2.0'",build)
 java.write_text(new_java,encoding='utf-8');store.write_text(new_store,encoding='utf-8');gradle.write_text(build,encoding='utf-8')
 styles=Path('app/src/main/res/values/styles.xml')
 if styles.exists():
  s=styles.read_text(encoding='utf-8').replace('#117969','#AE426B').replace('#F4F7F5','#FFE6EF');styles.write_text(s,encoding='utf-8')
 print('Versione 2.2: rosa, preferiti con backup e aggiunta rapida. Database aggiornato senza eliminare inventario e utilizzi.')

if __name__=='__main__':main()

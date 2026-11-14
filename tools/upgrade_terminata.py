"""Farmaci 2.4: confezione terminata e riepilogo unico; nessun Calendar.
Richiede tools/upgrade_rosa.py e tools/restyle.py.
"""
from pathlib import Path
import re
import upgrade_rosa as pink
MARKER='// FARMACI_FINISH_240'
FINISH_UI=r"""
 // FARMACI_FINISH_240
 void finishBoxDialog(long id){
  JSONObject b=store.box(id);if(b==null||b.optDouble("qty")<=0){error("La confezione è già esaurita o non è più disponibile");return;}
  new AlertDialog.Builder(this).setTitle("Confezione terminata?")
   .setMessage(b.optString("name")+"\n"+b.optString("description")+"\n\nIl residuo di questa singola scatola ("+number(b.optDouble("qty"))+" "+b.optString("unit")+") sarà azzerato.\n\nLo storico resta disponibile e puoi annullare dal registro. Non riceverai più avvisi di scadenza per questa scatola; potrà restare l’avviso di scorta esaurita.")
   .setPositiveButton("Conferma: terminata",(d,w)->{try{store.finishBox(id);detail(id);Toast.makeText(this,"Confezione terminata. Puoi annullare dal registro.",Toast.LENGTH_LONG).show();}catch(Exception e){error(e.getMessage());}})
   .setNegativeButton("Indietro",null).show();
 }
"""
FINISH_STORE=r"""
 // FINISH_MOVEMENT_240
 public synchronized long finishBox(long id){
  SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try{
   JSONObject b=box(id);if(b==null||b.optDouble("qty")<=0)throw new IllegalArgumentException("La confezione è già esaurita o non esiste");
   double remaining=b.optDouble("qty");d.execSQL("UPDATE boxes SET qty=0 WHERE id=?",new Object[]{id});
   ContentValues v=new ContentValues();v.put("box",id);v.put("amount",remaining);v.put("at",Instant.now().toString());v.put("undone",0);v.put("kind","terminata");
   long movement=d.insertOrThrow("uses",null,v);d.setTransactionSuccessful();return movement;
  }finally{d.endTransaction();}
 }
"""
SEARCH=r"""void search(){
 if(catalog==null){error("Attendi la preparazione del catalogo");return;}
 shell("Trova medicinale","Preferiti in cima · catalogo AIFA offline");
 EditText q=field(body,"Nome commerciale o AIC","",false);LinearLayout rows=new LinearLayout(this);rows.setOrientation(1);body.addView(rows);
 Runnable[] reload=new Runnable[1];reload[0]=()->{
  int token=++searchVersion;String term=q.getText().toString();Set<String> favorites=new HashSet<>();for(JSONObject f:store.favorites())favorites.add(f.optString("aic"));
  handler.postDelayed(()->{if(token!=searchVersion||!alive)return;worker.execute(()->{try{
   List<JSONObject> found=catalog.search(term,favorites);runOnUiThread(()->{if(!alive||token!=searchVersion)return;rows.removeAllViews();
    if(term.trim().length()<2)text(rows,"I tuoi preferiti. Scrivi almeno 2 caratteri per cercare in tutto il catalogo.",14,MUTED);
    if(found.isEmpty())text(rows,term.trim().length()<2?"Nessun preferito ancora. Cerca un medicinale e tocca il cuore.":"Nessun risultato. Controlla il nome o prova l’AIC.",16,MUTED);
    boolean others=false;for(JSONObject b:found){if(!favorites.contains(b.optString("aic"))&&!others){others=true;text(rows,"Altri risultati",15,MUTED);}
     LinearLayout c=card(rows);favoriteButton(c,b,()->reload[0].run());text(c,b.optString("name"),19,INK);text(c,b.optString("description"),15,MUTED);text(c,"AIC "+b.optString("aic")+" · "+b.optString("status"),13,MUTED);c.setOnClickListener(v->confirmDrug(b));}
    if(found.size()==100)text(rows,"Mostrati fino a 100 risultati, preferiti prima. Rendi più precisa la ricerca.",14,MUTED);
   });
  }catch(Exception e){runOnUiThread(()->{if(alive&&token==searchVersion)error(e.getMessage());});}});},200);
 };watch(q,()->reload[0].run());reload[0].run();button(body,"Torna all’armadietto",this::home);
}"""
CATALOG_SEARCH=r"""public List<JSONObject> search(String query){return search(query,Collections.emptySet());}
 public List<JSONObject> search(String query,Set<String> favoriteAics){
  List<JSONObject> result=new ArrayList<>();String q=query.trim();StringBuilder in=new StringBuilder();
  for(String aic:favoriteAics)if(aic!=null&&aic.matches("[0-9]{9}")){if(in.length()>0)in.append(',');in.append('\'').append(aic).append('\'');}
  String member=in.length()==0?"0":"aic IN ("+in+")";String order=" ORDER BY CASE WHEN "+member+" THEN 0 ELSE 1 END,name COLLATE NOCASE,description LIMIT 100";
  String sql;String[] args;
  if(q.length()<2){if(in.length()==0)return result;sql="SELECT * FROM drugs WHERE "+member+order;args=new String[0];}
  else{String esc=q.replace("\\","\\\\").replace("%","\\%").replace("_","\\_");sql="SELECT * FROM drugs WHERE (name LIKE ? ESCAPE '\\' OR aic=?)"+order;args=new String[]{"%"+esc+"%",q};}
  try(Cursor c=db.rawQuery(sql,args)){while(c.moveToNext())result.add(Store.object(c));}catch(Exception e){throw new RuntimeException(e);}return result;
 }
 // FAVORITES_QUERY_230
"""
REMINDER = 'package it.farmacidicasa;\nimport android.Manifest;import android.app.*;import android.content.*;import android.content.pm.PackageManager;import android.os.*;import org.json.*;import java.time.*;\npublic class ReminderReceiver extends BroadcastReceiver {\n private static final int ID=101;\n public static void schedule(Context c){LocalDateTime next=LocalDate.now().atTime(9,0);if(!next.isAfter(LocalDateTime.now()))next=next.plusDays(1);long millis=next.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();PendingIntent p=PendingIntent.getBroadcast(c,1,new Intent(c,ReminderReceiver.class),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);((AlarmManager)c.getSystemService(Context.ALARM_SERVICE)).setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,millis,p);}\n @Override public void onReceive(Context c,Intent i){try{notifyNow(c,false);}finally{schedule(c);}}\n public static void notifyNow(Context c,boolean test){update(c,test,true);}\n public static void refreshExisting(Context c){update(c,false,false);}\n private static void update(Context c,boolean test,boolean create){\n  NotificationManager manager=(NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);manager.createNotificationChannel(new NotificationChannel("reminders","Scadenze e scorte",NotificationManager.IMPORTANCE_DEFAULT));\n  if(Build.VERSION.SDK_INT>=33&&c.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED){if(test)android.widget.Toast.makeText(c,"Abilita le notifiche nelle impostazioni Android",1).show();return;}\n  if(!create){boolean exists=false;for(android.service.notification.StatusBarNotification notification:manager.getActiveNotifications())if(notification.getId()==ID){exists=true;break;}if(!exists)return;}\n  int soon=0,low=0,total=0;try(Store store=new Store(c)){for(JSONObject b:store.boxes("")){boolean expires=Store.soon(b),stock=Store.low(b);if(expires)soon++;if(stock)low++;if(expires||stock)total++;}}\n  if(total==0&&!test){manager.cancel(ID);return;}\n  String text=test?"Notifiche attive. "+soon+" scadenze, "+low+" scorte basse.":total+" confezioni da controllare: "+soon+" per scadenza, "+low+" per scorta bassa o esaurita.";\n  PendingIntent open=PendingIntent.getActivity(c,0,new Intent(c,MainActivity.class),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);\n  manager.notify(ID,new Notification.Builder(c,"reminders").setSmallIcon(R.drawable.ic_home).setContentTitle("Farmaci di casa").setContentText(text).setStyle(new Notification.BigTextStyle().bigText(text)).setContentIntent(open).setOnlyAlertOnce(true).setAutoCancel(true).build());\n }\n}\n'

def patch_main(source):
 if MARKER in source:return source
 source=pink.base.replace_method(source,'void search()',SEARCH)
 source=source.replace('button(body,"Aggiungi a Google Calendar",()->calendarReminder(id));','')
 source=pink.once(source,'button(body,"Registra utilizzo",()->useDialog(id));','if(b.optDouble("qty")>0){button(body,"Registra utilizzo",()->useDialog(id));button(body,"Confezione terminata",()->finishBoxDialog(id));}else{text(body,"Confezione esaurita · conservata per lo storico",16,MUTED);}')
 source=pink.once(source,'text(row,when+" · "+number(u.optDouble("amount"))','text(row,(u.optString("kind","uso").equals("terminata")?"Confezione terminata · ":"")+when+" · "+number(u.optDouble("amount"))')
 source=pink.once(source,'button(row,"Annulla questo utilizzo",','button(row,u.optString("kind","uso").equals("terminata")?"Annulla confezione terminata":"Annulla questo utilizzo",')
 source=pink.once(source,'void shell(String title,String subtitle){','void shell(String title,String subtitle){ReminderReceiver.refreshExisting(this);')
 source=source.replace('Versione app 2.2.0','Versione app 2.4.0').replace('Versione app 2.3.0','Versione app 2.4.0')
 end=source.rfind('}');return source[:end]+FINISH_UI+'\n'+source[end:]

def patch_store(source):
 if '// FINISH_MOVEMENT_240' in source:return source
 source=pink.once(source,'super(c,"home.db",null,2);','super(c,"home.db",null,3);')
 source=pink.once(source,'undone INTEGER NOT NULL DEFAULT 0)"','undone INTEGER NOT NULL DEFAULT 0,kind TEXT NOT NULL DEFAULT \'uso\')"')
 migration='public void onUpgrade(SQLiteDatabase d,int a,int b){if(a<2)d.execSQL("'+pink.FAVORITE_SCHEMA+'");if(a<3)d.execSQL("ALTER TABLE uses ADD COLUMN kind TEXT NOT NULL DEFAULT \'uso\'");}'
 source=pink.base.replace_method(source,'public void onUpgrade(SQLiteDatabase d,int a,int b)',migration)
 source=pink.once(source,'INSERT INTO uses(id,box,amount,at,undone) VALUES(?,?,?,?,?)','INSERT INTO uses(id,box,amount,at,undone,kind) VALUES(?,?,?,?,?,?)')
 source=pink.once(source,'u.getInt("undone")});','u.getInt("undone"),u.optString("kind","uso").equals("terminata")?"terminata":"uso"});')
 end=source.rfind('}');return source[:end]+FINISH_STORE+'\n'+source[end:]

def patch_catalog(source):
 if '// FAVORITES_QUERY_230' in source:return source
 return pink.base.replace_method(source,'public List<JSONObject> search(String query)',CATALOG_SEARCH)

def main():
 pink.main()
 java=Path('app/src/main/java/it/farmacidicasa/MainActivity.java');store=java.with_name('Store.java');catalog=java.with_name('Catalog.java');reminder=java.with_name('ReminderReceiver.java');gradle=Path('app/build.gradle')
 new_java=patch_main(java.read_text(encoding='utf-8'));new_store=patch_store(store.read_text(encoding='utf-8'));new_catalog=patch_catalog(catalog.read_text(encoding='utf-8'))
 build=gradle.read_text(encoding='utf-8');build=re.sub(r'\bversionCode\s+(202|203)\b','versionCode 204',build);build=re.sub(r"versionName '2\.[23]\.0'","versionName '2.4.0'",build)
 java.write_text(new_java,encoding='utf-8');store.write_text(new_store,encoding='utf-8');catalog.write_text(new_catalog,encoding='utf-8');reminder.write_text(REMINDER,encoding='utf-8');gradle.write_text(build,encoding='utf-8')
 print('Versione 2.4: confezione terminata annullabile, riepilogo unico aggiornato, preferiti prima; Calendar non aggiunto.')

if __name__=='__main__':main()

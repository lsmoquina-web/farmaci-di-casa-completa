package it.farmacidicasa;
import android.content.*;import android.database.*;import android.database.sqlite.*;import org.json.*;import java.time.*;import java.util.*;
public class Store extends SQLiteOpenHelper {
 public Store(Context c){super(c,"home.db",null,1);}
 public void onCreate(SQLiteDatabase d){
  d.execSQL("CREATE TABLE boxes(id INTEGER PRIMARY KEY AUTOINCREMENT,aic TEXT NOT NULL,name TEXT NOT NULL,description TEXT NOT NULL,qty REAL NOT NULL,unit TEXT NOT NULL,minimum REAL NOT NULL,expiry TEXT NOT NULL,opened TEXT NOT NULL,days INTEGER NOT NULL,lot TEXT NOT NULL,notes TEXT NOT NULL)");
  d.execSQL("CREATE TABLE uses(id INTEGER PRIMARY KEY AUTOINCREMENT,box INTEGER NOT NULL,amount REAL NOT NULL,at TEXT NOT NULL,undone INTEGER NOT NULL DEFAULT 0)");
 }
 public void onUpgrade(SQLiteDatabase d,int a,int b){throw new IllegalStateException("Migrazione non disponibile");}
 static JSONObject object(Cursor c)throws JSONException {JSONObject o=new JSONObject();for(int i=0;i<c.getColumnCount();i++){int t=c.getType(i);o.put(c.getColumnName(i),t==Cursor.FIELD_TYPE_INTEGER?c.getLong(i):t==Cursor.FIELD_TYPE_FLOAT?c.getDouble(i):c.getString(i));}return o;}
 public synchronized List<JSONObject> boxes(String term){List<JSONObject> rows=new ArrayList<>();try(Cursor c=getReadableDatabase().rawQuery("SELECT * FROM boxes WHERE name LIKE ? OR aic LIKE ? OR lot LIKE ? ORDER BY expiry,name",new String[]{"%"+term+"%","%"+term+"%","%"+term+"%"})){while(c.moveToNext())rows.add(object(c));}catch(JSONException e){throw new RuntimeException(e);}return rows;}
 public JSONObject box(long id){try(Cursor c=getReadableDatabase().rawQuery("SELECT * FROM boxes WHERE id=?",new String[]{""+id})){return c.moveToFirst()?object(c):null;}catch(JSONException e){throw new RuntimeException(e);}}
 public long save(JSONObject o)throws JSONException {ContentValues v=new ContentValues();for(String k:new String[]{"aic","name","description","unit","expiry","opened","lot","notes"})v.put(k,o.getString(k));v.put("qty",o.getDouble("qty"));v.put("minimum",o.getDouble("minimum"));v.put("days",o.getInt("days"));if(o.has("id")){getWritableDatabase().update("boxes",v,"id=?",new String[]{o.getString("id")});return o.getLong("id");}return getWritableDatabase().insertOrThrow("boxes",null,v);}
 public synchronized void use(long id,double amount){SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try {JSONObject b=box(id);if(b==null||amount<=0||!Double.isFinite(amount)||java.math.BigDecimal.valueOf(amount).stripTrailingZeros().scale()>6||amount>b.optDouble("qty"))throw new IllegalArgumentException("Quantità non valida o superiore al residuo");d.execSQL("UPDATE boxes SET qty=ROUND(qty-?,6) WHERE id=?",new Object[]{amount,id});d.execSQL("INSERT INTO uses(box,amount,at,undone) VALUES(?,?,?,0)",new Object[]{id,amount,Instant.now().toString()});d.setTransactionSuccessful();}finally{d.endTransaction();}}
 public synchronized void undo(long useId){SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try(Cursor c=d.rawQuery("SELECT box,amount FROM uses WHERE id=? AND undone=0",new String[]{""+useId})){if(c.moveToFirst()){if(box(c.getLong(0))==null)throw new IllegalArgumentException("Confezione non disponibile");d.execSQL("UPDATE boxes SET qty=ROUND(qty+?,6) WHERE id=?",new Object[]{c.getDouble(1),c.getLong(0)});d.execSQL("UPDATE uses SET undone=1 WHERE id=?",new Object[]{useId});}d.setTransactionSuccessful();}finally{d.endTransaction();}}
 public List<JSONObject> history(long id){List<JSONObject> a=new ArrayList<>();try(Cursor c=getReadableDatabase().rawQuery("SELECT * FROM uses WHERE box=? ORDER BY id DESC",new String[]{""+id})){while(c.moveToNext())a.add(object(c));}catch(Exception e){throw new RuntimeException(e);}return a;}
 public void delete(long id){SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try{d.delete("uses","box=?",new String[]{""+id});d.delete("boxes","id=?",new String[]{""+id});d.setTransactionSuccessful();}finally{d.endTransaction();}}
 public static LocalDate effective(JSONObject b){LocalDate e=LocalDate.parse(b.optString("expiry"));String opened=b.optString("opened");int days=b.optInt("days");if(!opened.isEmpty()&&days>0){LocalDate p=LocalDate.parse(opened).plusDays(days);if(p.isBefore(e))e=p;}return e;}
 public static boolean low(JSONObject b){return b.optDouble("qty")<=b.optDouble("minimum");}
 public static boolean soon(JSONObject b){return b.optDouble("qty")>0&&!effective(b).isAfter(LocalDate.now().plusDays(30));}
 public JSONObject backup()throws JSONException {JSONObject root=new JSONObject();root.put("format","farmaci-di-casa");root.put("version",1);root.put("created",Instant.now().toString());root.put("boxes",new JSONArray(boxes("")));JSONArray uses=new JSONArray();try(Cursor c=getReadableDatabase().rawQuery("SELECT * FROM uses ORDER BY id",null)){while(c.moveToNext())uses.put(object(c));}root.put("uses",uses);return root;}
 public static void validateBox(JSONObject b)throws Exception {
  if(!b.getString("aic").matches("[0-9]{9}"))throw new Exception("AIC non valido");
  if(b.getString("name").trim().isEmpty()||b.getString("unit").trim().isEmpty())throw new Exception("Nome e unità sono obbligatori");
  for(String k:new String[]{"qty","minimum"})if(!Double.isFinite(b.getDouble(k))||b.getDouble(k)<0||java.math.BigDecimal.valueOf(b.getDouble(k)).stripTrailingZeros().scale()>6)throw new Exception("Quantità non valida");
  LocalDate.parse(b.getString("expiry"));String opened=b.getString("opened");if(!opened.isEmpty())LocalDate.parse(opened);
  if(b.getInt("days")<0)throw new Exception("Giorni non validi");
  for(String k:new String[]{"description","lot","notes"})b.getString(k);
 }
 public void restore(JSONObject r)throws Exception {
  if(!r.getString("format").equals("farmaci-di-casa")||r.getInt("version")!=1)throw new Exception("Formato backup non supportato");
  JSONArray bs=r.getJSONArray("boxes"),us=r.getJSONArray("uses");Set<Long> ids=new HashSet<>(),uids=new HashSet<>();
  for(int i=0;i<bs.length();i++){JSONObject b=bs.getJSONObject(i);validateBox(b);long id=b.getLong("id");if(id<=0||!ids.add(id))throw new Exception("ID confezione duplicato/non valido");}
  for(int i=0;i<us.length();i++){JSONObject u=us.getJSONObject(i);long id=u.getLong("id");if(id<=0||!uids.add(id)||!ids.contains(u.getLong("box"))||!Double.isFinite(u.getDouble("amount"))||u.getDouble("amount")<=0)throw new Exception("Registro non valido");Instant.parse(u.getString("at"));if(u.getInt("undone")!=0&&u.getInt("undone")!=1)throw new Exception("Annullamento non valido");}
  SQLiteDatabase d=getWritableDatabase();d.beginTransaction();try {d.delete("uses",null,null);d.delete("boxes",null,null);
   for(int i=0;i<bs.length();i++){JSONObject b=bs.getJSONObject(i);
    ContentValues v=new ContentValues();for(String k:new String[]{"aic","name","description","unit","expiry","opened","lot","notes"})v.put(k,b.getString(k));v.put("id",b.getLong("id"));v.put("qty",b.getDouble("qty"));v.put("minimum",b.getDouble("minimum"));v.put("days",b.getInt("days"));d.insertOrThrow("boxes",null,v);
   }
   for(int i=0;i<us.length();i++){JSONObject u=us.getJSONObject(i);d.execSQL("INSERT INTO uses(id,box,amount,at,undone) VALUES(?,?,?,?,?)",new Object[]{u.getLong("id"),u.getLong("box"),u.getDouble("amount"),u.getString("at"),u.getInt("undone")});}d.setTransactionSuccessful();
  }finally{d.endTransaction();}
 }
}

package it.farmacidicasa;
import android.content.*;import android.database.*;import android.database.sqlite.*;import org.json.*;import java.io.*;import java.nio.file.*;import java.util.*;
public class Catalog implements AutoCloseable {
 private SQLiteDatabase db;
 public final JSONObject info;
 public Catalog(Context c)throws Exception {
  try(InputStream in=c.getAssets().open("catalog-info.json")){info=new JSONObject(new String(IO.read(in,1024*1024),java.nio.charset.StandardCharsets.UTF_8));}
  File dest=new File(c.getFilesDir(),"catalog.db");String hash=info.getString("sha256");
  if(!dest.exists()||!hash.equals(c.getSharedPreferences("catalog",0).getString("hash",""))){
   File tmp=new File(c.getFilesDir(),"catalog.tmp");try(InputStream in=c.getAssets().open("catalog.db");OutputStream out=new FileOutputStream(tmp)){IO.copy(in,out);}
   Files.move(tmp.toPath(),dest.toPath(),StandardCopyOption.REPLACE_EXISTING);c.getSharedPreferences("catalog",0).edit().putString("hash",hash).apply();
  }
  db=SQLiteDatabase.openDatabase(dest.getPath(),null,SQLiteDatabase.OPEN_READONLY);
 }
 public List<JSONObject> search(String query){List<JSONObject> a=new ArrayList<>();String q=query.trim();if(q.length()<2)return a;String esc=q.replace("\\","\\\\").replace("%","\\%").replace("_","\\_");
  try(Cursor c=db.rawQuery("SELECT * FROM drugs WHERE name LIKE ? ESCAPE '\\' OR aic=? ORDER BY name,description LIMIT 100",new String[]{"%"+esc+"%",q})){while(c.moveToNext())a.add(Store.object(c));}catch(Exception e){throw new RuntimeException(e);}return a;
 }
 public JSONObject find(String aic){try(Cursor c=db.rawQuery("SELECT * FROM drugs WHERE aic=?",new String[]{aic})){return c.moveToFirst()?Store.object(c):null;}catch(Exception e){throw new RuntimeException(e);}}
 public void close(){db.close();}
}

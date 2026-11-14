package it.farmacidicasa;
import android.content.*;
public class BootReceiver extends BroadcastReceiver {public void onReceive(Context c,Intent i){ReminderReceiver.schedule(c);}}

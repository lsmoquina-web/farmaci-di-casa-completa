package it.farmacidicasa;
import java.util.*;
public final class Codes {
 public static List<String> candidates(String raw) {
  LinkedHashSet<String> out=new LinkedHashSet<>();
  String s=raw.trim().toUpperCase(Locale.ROOT).replace("*", "");
  if(s.matches("A[0-9]{9}")) s=s.substring(1);
  if(s.matches("[0-9]{9}")) out.add(s);
  if(s.matches("[0-9A-Z]{6}")) {
   String alphabet="0123456789BCDFGHJKLMNPQRSTUVWXYZ"; long n=0;
   boolean ok=true;
   for(char c:s.toCharArray()){int v=alphabet.indexOf(c);if(v<0){ok=false;break;}n=n*32+v;}
   if(ok && n<=999999999L) out.add(String.format(Locale.ROOT,"%09d",n));
  }
  return new ArrayList<>(out);
 }
}

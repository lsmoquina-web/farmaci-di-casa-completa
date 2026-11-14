package it.farmacidicasa;
import java.io.*;
public final class IO {
 public static byte[] read(InputStream in,int max)throws IOException {if(in==null)throw new IOException("File non accessibile");ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[16384];int n,total=0;while((n=in.read(buf))!=-1){total+=n;if(total>max)throw new IOException("File troppo grande");out.write(buf,0,n);}return out.toByteArray();}
 public static void copy(InputStream in,OutputStream out)throws IOException {byte[] b=new byte[16384];int n;while((n=in.read(b))!=-1)out.write(b,0,n);}
}

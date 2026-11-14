package it.farmacidicasa;
import org.junit.Test; import static org.junit.Assert.*;
public class CodesTest {
 @Test public void numeric(){assertEquals("000367045",Codes.candidates("000367045").get(0));}
 @Test public void code32(){assertEquals("020096020",Codes.candidates("0M590N").get(0));}
 @Test public void code32Second(){assertEquals("012345676",Codes.candidates("0CSSBD").get(0));}
 @Test public void human(){assertEquals("020096020",Codes.candidates("A020096020").get(0));}
 @Test public void unknown(){assertTrue(Codes.candidates("1234567890123").isEmpty());}
}

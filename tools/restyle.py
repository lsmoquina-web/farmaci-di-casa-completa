"""Restyling locale di build: nessun invio dati, nessun SDK pubblicitario.
Eseguire prima della compilazione Gradle, dalla radice del repository.
"""
from pathlib import Path
import re

MARKER = '// FARMACI_RESTYLE_210'
JAVA = Path('app/src/main/java/it/farmacidicasa/MainActivity.java')

BUTTON = r"""void button(LinearLayout p,String label,Runnable r){
 Button b=new Button(this);b.setText(label);b.setAllCaps(false);b.setTextSize(16);b.setTypeface(null,Typeface.BOLD);
 boolean secondary=label.startsWith("Torna")||label.equals("Annulla")||label.equals("Backup e informazioni")||label.equals("Avvisi e scadenze");
 boolean danger=label.startsWith("Elimina");
 GradientDrawable shape=new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,danger?new int[]{0xffa94343,0xffbe5c52}:secondary?new int[]{0xffe8f1ee,0xffe8f1ee}:new int[]{0xff16796d,0xff266e87});
 shape.setCornerRadius(dp(17));
 b.setTextColor(secondary?INK:Color.WHITE);
 b.setBackground(new android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x22336666),shape,null));
 b.setElevation(dp(secondary?0:2));b.setPadding(dp(12),dp(8),dp(12),dp(8));b.setMinHeight(dp(54));
 LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(0,dp(10),0,dp(5));p.addView(b,lp);b.setOnClickListener(v->r.run());
}"""

CARD = r"""LinearLayout card(LinearLayout parent){
 LinearLayout l=new LinearLayout(this);l.setOrientation(1);l.setPadding(dp(18),dp(15),dp(18),dp(15));
 GradientDrawable shape=bg(0xfaffffff,21);shape.setStroke(dp(1),0xffdfeae6);l.setBackground(shape);l.setElevation(dp(2));
 LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(dp(2),dp(10),dp(2),dp(7));parent.addView(l,lp);return l;
}"""

SHELL = r"""void shell(String title,String subtitle){
 page=new LinearLayout(this);page.setOrientation(1);page.setBackground(appBackground());page.setPadding(dp(20),dp(12),dp(20),0);setContentView(page);
 page.setOnApplyWindowInsetsListener((v,in)->{v.setPadding(dp(20),dp(12)+in.getSystemWindowInsetTop(),dp(20),in.getSystemWindowInsetBottom());return in;});page.requestApplyInsets();
 LinearLayout hero=new LinearLayout(this);hero.setOrientation(1);hero.setPadding(dp(20),dp(16),dp(20),dp(18));
 GradientDrawable header=new GradientDrawable(GradientDrawable.Orientation.TL_BR,new int[]{0xff123f3c,0xff1b7069,0xff377a95});header.setCornerRadius(dp(25));hero.setBackground(header);hero.setElevation(dp(3));
 page.addView(hero,new LinearLayout.LayoutParams(-1,-2));
 TextView badge=text(hero,catalog==null?"FARMACI DI CASA  /  AVVIO":"FARMACI DI CASA  /  OFFLINE",11,0xffcde9e3);badge.setLetterSpacing(.11f);
 TextView h=text(hero,title,27,Color.WHITE);h.setTypeface(null,Typeface.BOLD);text(hero,subtitle,14,0xffe2f1ee);
 ScrollView sc=new ScrollView(this);sc.setFillViewport(false);sc.setClipToPadding(false);sc.setVerticalScrollBarEnabled(false);
 body=new LinearLayout(this);body.setOrientation(1);body.setPadding(0,dp(9),0,dp(28));sc.addView(body);page.addView(sc,new LinearLayout.LayoutParams(-1,0,1));
}"""

HOME = r"""void home(){
 shell("Il tuo armadietto","Più ordine, meno sprechi. Tutto sotto controllo.");
 List<JSONObject> all=store.boxes("");int soon=0,low=0;for(JSONObject b:all){if(Store.soon(b))soon++;if(Store.low(b))low++;}
 LinearLayout stats=new LinearLayout(this);stats.setOrientation(0);stats.setPadding(0,dp(10),0,dp(7));body.addView(stats);
 statTile(stats,""+all.size(),"Confezioni",0xff16796d);statTile(stats,""+soon,"Scadenze",0xffa86120);statTile(stats,""+low,"Scorte basse",0xff9a4856);
 text(body,"Le scadenze includono il limite dopo apertura. Avvisi entro 30 giorni.",12,MUTED);
 button(body,"+ Aggiungi medicinale",this::addChoice);button(body,"Avvisi e scadenze",this::alerts);
 TextView section=text(body,"I tuoi medicinali",21,INK);section.setTypeface(null,Typeface.BOLD);section.setPadding(0,dp(19),0,dp(5));
 EditText q=field(body,"Cerca nome, AIC o lotto","",false);
 LinearLayout rows=new LinearLayout(this);rows.setOrientation(1);body.addView(rows);
 Runnable refresh=()->renderBoxes(rows,store.boxes(q.getText().toString()));watch(q,refresh);refresh.run();
 button(body,"Backup e informazioni",this::settings);
 adPlaceholder(body);
}"""

EXTRA = r"""
 // FARMACI_RESTYLE_210
 android.graphics.drawable.Drawable appBackground(){
  return new android.graphics.drawable.Drawable(){
   final android.graphics.Paint paint=new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
   public void draw(android.graphics.Canvas canvas){
    android.graphics.Rect b=getBounds();float w=b.width(),h=b.height();if(w<=0||h<=0)return;
    paint.setShader(new android.graphics.LinearGradient(0,0,w,h,new int[]{0xffedf7f3,0xfff7f9fd,0xffe8f1f5},null,android.graphics.Shader.TileMode.CLAMP));canvas.drawRect(b,paint);paint.setShader(null);
    paint.setColor(0x0c238e7b);canvas.drawCircle(w*.98f,h*.26f,w*.48f,paint);
    paint.setColor(0x0b567db0);canvas.drawCircle(-w*.12f,h*.73f,w*.55f,paint);
    paint.setColor(0x09ffffff);canvas.drawCircle(w*.77f,h*.88f,w*.65f,paint);
   }
   public void setAlpha(int a){} public void setColorFilter(android.graphics.ColorFilter f){} public int getOpacity(){return android.graphics.PixelFormat.OPAQUE;}
  };
 }
 void statTile(LinearLayout parent,String number,String label,int accent){
  LinearLayout tile=new LinearLayout(this);tile.setOrientation(1);tile.setGravity(Gravity.CENTER);tile.setPadding(dp(4),dp(13),dp(4),dp(13));
  GradientDrawable shape=bg(0xfaffffff,18);shape.setStroke(dp(1),0xffdfeae6);tile.setBackground(shape);
  LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);lp.setMargins(dp(3),0,dp(3),0);parent.addView(tile,lp);
  TextView count=text(tile,number,26,accent);count.setTypeface(null,Typeface.BOLD);count.setGravity(Gravity.CENTER);
  TextView caption=text(tile,label,11,INK);caption.setGravity(Gravity.CENTER);caption.setMaxLines(2);
 }
 void adPlaceholder(LinearLayout parent){
  LinearLayout frame=new LinearLayout(this);frame.setOrientation(1);frame.setPadding(dp(14),dp(11),dp(14),dp(11));
  GradientDrawable border=bg(0xfff5f7f8,15);border.setStroke(dp(1),0xffcedbd7,dp(5),dp(4));frame.setBackground(border);
  LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.setMargins(dp(2),dp(28),dp(2),dp(8));parent.addView(frame,lp);
  TextView tag=text(frame,"SPAZIO PUBBLICITARIO",10,MUTED);tag.setLetterSpacing(.10f);tag.setGravity(Gravity.CENTER);
  TextView message=text(frame,"Anteprima · nessun annuncio attivo",13,MUTED);message.setGravity(Gravity.CENTER);message.setPadding(0,dp(10),0,dp(10));
  frame.setContentDescription("Spazio riservato a futuri annunci. Nessuna pubblicità attiva.");
 }
"""

def replace_method(source, signature, replacement):
    if source.count(signature) != 1:
        raise RuntimeError('Metodo assente o ambiguo: ' + signature + '. Nessun file modificato.')
    start = source.index(signature)
    opening = source.index('{', start)
    depth = 0
    quote = None
    escape = False
    line_comment = block_comment = False
    i = opening
    while i < len(source):
        c = source[i]
        nxt = source[i:i+2]
        if line_comment:
            if c == '\n': line_comment = False
        elif block_comment:
            if nxt == '*/': block_comment = False; i += 1
        elif quote:
            if escape: escape = False
            elif c == '\\': escape = True
            elif c == quote: quote = None
        elif nxt == '//': line_comment = True; i += 1
        elif nxt == '/*': block_comment = True; i += 1
        elif c in ('"', "'"): quote = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return source[:start] + replacement + source[i+1:]
        i += 1
    raise RuntimeError('Metodo incompleto: '+signature)

def patch(source):
    if MARKER in source: return source
    for signature, replacement in [
        ('void button(LinearLayout p,String label,Runnable r)',BUTTON),
        ('LinearLayout card(LinearLayout parent)',CARD),
        ('void shell(String title,String subtitle)',SHELL),
        ('void home()',HOME),
    ]:
        source = replace_method(source,signature,replacement)
    end=source.rfind('}')
    if end<0: raise RuntimeError('Classe Java non riconosciuta')
    source=source[:end]+EXTRA+'\n'+source[end:]
    return source.replace('Versione app 2.0.0','Versione app 2.1.0')

def main():
    original=JAVA.read_text(encoding='utf-8')
    changed=patch(original)
    gradle=Path('app/build.gradle')
    build=gradle.read_text(encoding='utf-8')
    build=re.sub(r'\bversionCode\s+200\b','versionCode 201',build)
    build=build.replace("versionName '2.0.0'", "versionName '2.1.0'")
    JAVA.write_text(changed,encoding='utf-8')
    gradle.write_text(build,encoding='utf-8')
    print('Restyling 2.1 applicato. Spazio pubblicitario dimostrativo; nessun SDK o annuncio reale.')

if __name__=='__main__':main()

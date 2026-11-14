# Farmaci di casa — progetto Android nativo, versione 2.0.0

## Cosa ricevi

Un progetto sorgente Android in italiano. NON è una pagina HTML e NON è un APK già compilato o certificato.
La cartella `.github/workflows` contiene la compilazione automatica. La build scarica il CSV ufficiale AIFA,
lo converte in SQLite e incorpora il catalogo nell'APK. L'utente finale non importa il catalogo.

## Il percorso più semplice per ottenere l'APK

1. Estrai tutto lo ZIP sul PC, non aprire solo i singoli file dall'archivio.
2. Su GitHub crea un repository NUOVO e vuoto, ad esempio `farmaci-di-casa-completa`. È preferibile al precedente progetto per non mescolare vecchi sorgenti e dipendenze.
3. Prima della prima compilazione, configura la firma stabile seguendo il paragrafo successivo. È un'impostazione del progetto, non dell'app finale.
4. Nel nuovo repository usa **Add file → Upload files**. Trascina IL CONTENUTO della cartella estratta: `.github`, `app`, `tools`, `build.gradle`, `settings.gradle`, `gradle.properties` e i documenti. Includi `.gitignore`. Non caricare il solo ZIP e non aggiungere un livello di cartella sopra questi elementi.
5. Conferma con **Commit changes**. Nella radice del repository devono comparire `app` e `.github` affiancati.
6. Apri **Actions → Compila APK Farmaci di casa**. La build parte al caricamento sul ramo `main` o `master`. Per ripeterla usa **Run workflow**.
7. Quando il job è verde apri la sua pagina e scarica l'artifact **Farmaci-di-casa-APK**. Estrai lo ZIP e installa `app-debug.apk` sul telefono Android (Android 8 o successivo).
8. Consenti l'installazione da quella sorgente solo se riconosci il file. Nell'app concedi il permesso fotocamera per la scansione e notifiche per gli avvisi.

Non serve Android Studio per compilare con Actions. Non serve Gradle sul PC. Non serve configurare il catalogo nell'app.
La prima build richiede Internet e può impiegare diversi minuti. Se AIFA non risponde, la build FALLISCE: non viene prodotto volutamente un APK con catalogo finto o vuoto.

## Firma stabile: una volta sola, importante per gli aggiornamenti

La firma identifica l'autore dell'APK agli occhi di Android. Senza la stessa chiave, Android non consente l'aggiornamento diretto della stessa applicazione.

Sul PC Windows dove è già installato Android Studio:

1. Apri PowerShell nella cartella estratta (dove vedi `app` e `tools`).
2. Esegui:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\create-signing-key.ps1
```

3. Lo script genera una chiave locale e copia la versione Base64 negli appunti. Può trovare il `keytool` di Android Studio nel percorso standard. Se Android Studio è installato altrove e il comando non trova Java, configura Java 17 o il percorso di `keytool`.
4. Su GitHub apri **Settings → Secrets and variables → Actions → New repository secret**.
5. Nome ESATTO: `ANDROID_KEYSTORE_BASE64`. Nel valore incolla gli appunti, poi salva.
6. Conserva anche una copia sicura del file `tools/farmaci-debug.keystore`. NON caricarlo nel repository e NON pubblicare il testo Base64.

La chiave è per questa distribuzione personale/debug, non una procedura Play Store. Le password standard debug sono intenzionali; la chiave privata va comunque protetta.

Se salti il secret, la build funziona ma genera una chiave temporanea: l'APK seguente potrebbe non aggiornarsi sopra quello installato. Esporta il backup PRIMA di disinstallare; disinstallare elimina i dati dell'app. Per evitare questo problema configura la chiave stabile prima della prima installazione.

## Funzioni implementate nei sorgenti

- Schermata iniziale con conteggi, ricerca dell'inventario, avvisi e schede delle confezioni.
- Aggiunta tramite fotocamera oppure ricerca per nome commerciale/AIC, senza rete sul telefono.
- Conversione dei sei caratteri Code 32 letti come Code 39 in AIC numerico a nove cifre, mantenendo gli zeri.
- Associazione solo se l'AIC risultante esiste nel catalogo; conferma obbligatoria di nome, dosaggio/desrizione e confezione.
- Una riga distinta per ogni scatola, anche se ha lo stesso AIC di un'altra.
- Residuo, unità liberamente indicata, soglia minima PER CONFEZIONE, lotto e note.
- Scadenza, apertura e numero di giorni di validità dopo apertura indicati dall'utente. Il limite effettivo è il più vicino tra scadenza e apertura più giorni.
- Registrazione degli utilizzi, sottrazione atomica, blocco di quantità superiori al residuo, storico e annullamento una sola volta per utilizzo.
- Modifica ed eliminazione di una confezione. Eliminare rimuove anche i suoi utilizzi, dopo conferma.
- Notifiche locali quotidiane per scadenze entro 30 giorni / oltre limite e scorta minima, riepilogative.
- Backup JSON completo di inventario e utilizzi. Ripristino validato e transazionale, sostitutivo, con conferma preventiva.
- Catalogo separato dal database domestico: la nuova copia inclusa nel nuovo APK sostituisce solo il catalogo.

## Uso quotidiano

Apri **Aggiungi medicinale** → scansione oppure ricerca. Per la ricerca bastano due caratteri del nome commerciale; se ci sono molti risultati aggiungi lettere. Sono mostrate fino a 100 confezioni. Seleziona dosaggio e confezione esatti e conferma.

Inserisci quantità residua e unità coerenti (per esempio `20` e `compresse`, oppure `80` e `ml`), soglia minima e scadenza. Non vengono presunte quantità standard della scatola. Sono ammesse quantità decimali fino a sei cifre decimali. La data di apertura è facoltativa; il periodo dopo apertura va letto nel foglietto. Per togliere una data di apertura usa **Non aperta** nel calendario.

Apri una scheda e premi **Registra utilizzo** per sottrarre una quantità. Un errore si corregge con **Annulla questo utilizzo**: il movimento resta nello storico come annullato e il residuo viene ripristinato.

In **Backup e informazioni** puoi esportare, ripristinare, aprire i permessi delle notifiche e inviare un avviso di prova.

## Limiti espliciti

- È codice generato, non un'app già collaudata su dispositivi reali. Leggi `VERIFICHE.md`.
- Il catalogo completo è disponibile solo dopo che GitHub lo ha scaricato con successo in fase di build; lo ZIP dei sorgenti non contiene un falso catalogo dimostrativo.
- Lo stato amministrativo AIFA è mostrato e NON viene usato come consiglio terapeutico. Il catalogo non è limitato a confezioni attualmente in commercio.
- Code 32/AIC è supportato dalla logica prevista, ma serve prova fisica su scatole reali e fotocamera reale. ML Kit legge anche altri formati, ma non si inventa una corrispondenza fra un EAN/GTIN/GS1 e un AIC: in assenza di corrispondenza riconosciuta si propone la ricerca manuale.
- Scadenza, lotto, quantità e durata dopo apertura NON sono ricavati dal barcode, neppure se un formato letto contiene più campi.
- La soglia è per la singola confezione, non una somma automatica delle scatole dello stesso farmaco.
- Le notifiche sono promemoria quotidiani indicativamente alle 09:00, non allarmi esatti né promemoria di assunzione. Permessi negati, risparmio energetico, telefono spento e arresto forzato possono impedirle o ritardarle. Dopo arresto forzato riaprire l'app.
- Non sono incluse prescrizioni, consigli sul dosaggio, account, sincronizzazione cloud, uso multiutente o un servizio automatico di aggiornamento catalogo dal telefono.
- L'aggiornamento catalogo avviene ricompilando su Actions e installando il nuovo APK, con stesso applicationId e stessa firma. Le copie domestiche conservano i dati registrati, anche se una voce sparisce dal catalogo nuovo.
- Il backup non è cifrato; scegli una destinazione sicura. La copia automatica cloud Android è disabilitata. Prima di operazioni rischiose esporta un backup.
- L'app non sostituisce il foglietto illustrativo, il farmacista o il medico.

## Compilazione locale facoltativa

Occorrono JDK 17, Android SDK 35, Gradle 8.9 e Python 3. Il wrapper binario Gradle non è incluso: GitHub installa Gradle automaticamente.

```sh
python tools/test_catalog.py
python tools/build_catalog.py
gradle :app:testDebugUnitTest :app:assembleDebug
```

Per usare un CSV AIFA locale durante lo sviluppo imposta la variabile `AIFA_CSV` al percorso del file prima di eseguire il convertitore. Non è un'importazione richiesta all'utente finale.

## Diagnosi di una build fallita

Apri lo step rosso in Actions e copia le ultime righe dell'errore, non soltanto il nome del job. Non sostituire il catalogo con dati casuali per ottenere un risultato verde.

Se nell'emulatore compare `adb: device offline`, Android non è raggiungibile: non è una diagnosi di errore del catalogo o dell'APK. Per il collaudo della fotocamera è preferibile un telefono reale.

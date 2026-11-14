# Stato reale delle verifiche

## Eseguito nell'ambiente di generazione

- Conversione CSV sintetico: 1.200 righe; zeri AIC e campi con punto e virgola preservati.
- Conversione Code 32: verificati i due vettori 0M590N e 0CSSBD con calcolo Python indipendente (non esecuzione Java).
- Tutti i file XML generati sono sintatticamente validi.
- Controllo strutturale delimitatori sui sorgenti Java superato; non equivale a una compilazione.
- Eseguiti 3 test Python ripetibili: conversione CSV, rifiuto puntatore LFS, rifiuto intestazioni errate.

## NON eseguito

- Download del CSV AIFA reale e conversione integrale: in questa sessione i due file catalogo nel progetto non erano leggibili. Nessun contenuto è stato inventato per sostituirli.
- Compilazione Gradle/Android: qui non sono disponibili Java, Gradle e Android SDK. Il primo esito reale arriva dal workflow GitHub.
- Esecuzione dei test JUnit Java: sono inclusi e il workflow li esegue prima di produrre l'APK.
- Installazione e avvio dell'app, resa grafica, scansione con fotocamera, permessi e notifiche sul dispositivo.
- Prova end-to-end di ripristino backup, aggiornamento firmato e conservazione inventario su telefono.

Non presentare questo ZIP come APK già compilato, verificato o privo di difetti. La presenza di una funzione nei sorgenti non equivale al suo collaudo su Android.

## Collaudo consigliato dopo la prima build verde

1. Avvio in modalità aereo: catalogo pronto e ricerca per nome commerciale/AIC funzionanti.
2. Aggiunta di due confezioni dello stesso AIC con quantità/scadenze diverse; devono restare separate.
3. Ricerca AIC con zeri iniziali; confronto di nome, dosaggio e confezione con la scatola.
4. Scansione di Code 32 reali. Codici sconosciuti devono aprire il recupero manuale, non un'associazione casuale.
5. Quantità 20 compresse, utilizzo 2: residuo 18. Annullamento: residuo 20. Annullamento non più disponibile per quello stesso movimento.
6. Quantità decimali, blocco movimento oltre residuo, soglia minima, apertura e limite post-apertura più vicino della scadenza.
7. Notifica di prova con permesso concesso e negato; verifica promemoria quotidiano e dopo riavvio.
8. Esporta il backup, cambia dati di prova, ripristina e confronta inventario, ID e storico, inclusi movimenti annullati.
9. Prova un backup non valido: l'inventario esistente deve restare invariato.
10. Ricompila e aggiorna con la stessa chiave: catalogo rinnovato, dati domestici preservati.

## Stack previsto

Java 17, Gradle 8.9, Android Gradle Plugin 8.7.3, compile/target SDK 35, Android minimo 26.
CameraX 1.3.4, ML Kit barcode-scanning 17.3.0 con modello incorporato, database SQLite locali separati.
Nessun server applicativo, nessun account richiesto, nessun permesso Internet nell'app.

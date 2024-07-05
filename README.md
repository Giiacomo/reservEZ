# Introduzione

Il Sistema di Reservez è una applicazione web progettata per facilitare la prenotazione e l'ordinazione presso una vasta gamma di ristoranti. Gli utenti possono registrarsi e cercare ristoranti, visualizzare i loro menu, effettuare prenotazioni e ordini, e ricevere raccomandazioni personalizzate in base alle loro preferenze gastronomiche. I ristoranti, dopo essersi registrati, possono gestire le proprie pagine con informazioni dettagliate, inclusi foto del locale, descrizioni e menu.

# Come installare

## Clonare

Per installare e avviare l'applicazione, seguire i passaggi seguenti:

1. **Clonare il repository:**

   ```bash
   git clone https://github.com/Giiacomo/reservEZ.git
   cd reservez-app
   ```

## Preparare il database:

Assicurarsi di avere PostgreSQL installato. Creare un database chiamato `reservez` con un utente chiamato `admin` con password a tua scelta e utilizzare la porta di default per PostgreSQL.

Esempio di comandi SQL per PostgreSQL:

```sql
CREATE DATABASE reservez;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE reservez TO admin;
```

## Configurare l'ambiente virtuale:

Creare un ambiente virtuale con venv e attivarlo:

```bash
python3 -m venv venv
source ./venv/bin/activate
```

## Installare le dipendenze:

Installare le dipendenze necessarie elencate nel file requirements.txt:

```bash
pip install -r requirements.txt
```

## Configurare le variabili d'ambiente:

Creare uno script setenv.sh per impostare le variabili d'ambiente necessarie:

```bash
# Contenuto di setenv.sh
export SECRETKEY="secretkey"
export DB_PSW="password"
export DB_USER="admin"
export DB_PORT="porta"  # Utilizzare la porta di default di PostgreSQL
```

## Eseguire lo script per impostare le variabili d'ambiente:

```bash
source ./setenv.sh
```

## Inizializzare il database:

Eseguire lo script per inizializzare il database con dati di configurazione iniziale:

```bash
python3 ./manage.py shell < initialize_db.py
```

## Avviare il server in modalità debug:

Avviare il server Django in modalità debug:

```bash
python3 manage.py runserver
```

L'applicazione sarà disponibile all'indirizzo http://localhost:8000/.

## Documentazione aggiuntiva

Per ulteriori dettagli sull'uso dell'applicazione, consultare la documentazione fornita in formato pdf.

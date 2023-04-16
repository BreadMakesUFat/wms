# TODO:



## Filters
- create views for predefined filters, e.g.: Form 7, last month, last 10?

## BarcodeScanner
- connect to db 
- detect if input is BON or Article ID 
- BON -> find Article ID (server) | Article ID -> find fitting BON via FIFO (server)

## Backup/Recovery
- cron job for backups in seperate folder (NOT IN THE PROJECT PATH!)
- recovery mechanism for all tables

## Refactoring
- reusable css templates for head and body
- sql files with scripts
- seperate js script files

# Deployment
- wsgi: waitress?


# Wichtig:
- Reihenfolge Import csv Dateien vorgeschrieben
- zusätzliche Felder werden ignoriert
- BON MUSS EINDEUTIG SEIN!!!
- ask for confirmation in create_database script

# Sonntag:
- Home Buttons
- Filters
- Add Edit Buttons to table views
- Bookings page
- connect Barcode Scanner APP + adjust it
- Design
- Errors 
- Install Scripts
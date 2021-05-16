This passages come from my bachelor thesis "Optimierung eines GNSS gestützten Bildflugverbandes für photogrammetrische Auswertungen" from the beginning of 2021

# Leverarm-Correction
Die Bearbeitung und Auswertung von Bild
ugen in Auswertesoftware erfordert oft vorab
eine Nachbearbeitung der gemessenen und aufgenommen Sensor- und Bilddaten. Fur
diese sich wiederholenden Tatigkeiten bietet sich eine weitere Automatisierung der Arbeitsabl
aufe an, um eine schnelle Bearbeitung und Vermeidung von Bearbeitungs- und
Kopierfehlern zu erreichen. Im folgenden Kapitel werden drei im Rahmen dieser Arbeit
entwickelten Skripte in der Programmiersprache Python erlautert und deren Funktionsweise
beschrieben. Ein besonderer Schwerpunkt liegt auf einer breiten Kompatibilitat mit
verschiedenen Python Interpretern. Aus diesem Grund wird auf die Anbindung weiterer
und externer Bibliotheken verzichtet.

## PictureCenter.py
Die photogrammetrische Auswertung von Bild
ugen mit Hilfe von bekannten Bildmitten
kann auf unterschiedliche Weise erfolgen. Jedoch ist es essentiell, die Zuordnung zwischen
Luftbild und Koordinaten herzustellen. Eine Moglichkeit besteht darin, die Bildmitteninformationen
in den Metadaten der einzelnen Luftbilder zu hinterlegen. Dies erfordert
jedoch eine direkte Kommunikation und Anbindung zwischen der Bild- und Positionsbestimmungssensorik, bei der wahrend des Schreibvorgangs der Luftbilder die Position der
Bildaufnahmen in den Metadaten hinterlegt werden.
Eine weitere Moglichkeit besteht darin, die Informationen der einzelnen Sensoren aus den
Logdateien auszulesen und mit den Bildnamen in einer Datei zu verknupfen. Kann eine solche
Datei nicht automatisiert erstellt werden, ist es erforderlich, die Sensordaten handisch
aus den Logdateien zu kopieren und zusammenzufuhren. Eine solche Datei ermoglicht
zudem eine handische Nachbearbeitung und Anpassung.
Das Python Skript PictureCenter bietet dem Anwender die Moglichkeit, eine funktionsf
ahige Bildmittendatei aus verschiedenen Logdateien zu erstellen. Das Skript verknupft
hierfur alle angegebenen Bilder im angegebenen Verzeichnis mit allen hinterlegten Informationen
uber die gemessenen Bildmitten. Die Koordinaten konnen hierbei aus einer CAM
Datei (reine GNSS Codelosung) sowie aus einer Eventle (Prazise DGNSS Messung, Justin
Postprocessing) stammen. Durch die Angabe einer Hexalogdatei wird ebenfalls die
Lage des Kopters zum Zeitpunkt der Aufnahme berucksichtigt. Hierfur wird eine Hebelarmkorrektur,
wie in Kapitel 3.1 beschrieben, auf die Bildmittenkoordinaten angewendet.
Zusatzlich erlaubt das Skript das Anbringen eines Oset Wertes an den Hohenwerten,
wodurch z.B. im Fall von unbekannten Roll-, Nick- und Gierwinkeln der Hohenversatz
zwischen Kamerabrennpunkt und GNSS Antenne ohne Hebelarmkorrektur ausgeglichen
werden kann. Durch die Angabe eines Genauigkeitswertes wird dieser jeder Aufnahme in
der Exportdatei angefugt.

### Übergabe der Eingabeparameter
Die Parameterubergabe erfolgt in beliebiger Reihenfolge. Hierfur wird fur einen neuen
Parameter als Schlusselzeichen ein
'-' gesetzt, auf dem der eigentliche Bezeichner folgt. Im
Anschluss an diesen Bezeichner wird nach einem Leerzeichen der Wert des Parameters
angegeben. Weitere Parameter werden anschlieend in der gleichen Form ubergeben. Das
Listing 3.1 zeigt, wie eine Parameterubergabe erfolgen kann.
Die Tabelle 3.4 gibt eine Ubersicht uber die Eingabeparameter und zeigt auf, welche
als P
ichtparameter angegeben werden mussen und welche optional hinzugefugt werden
konnen.

−justin Eventdatei.txt −pic Bildflugordner −hex Hexalogdatei.log −o Ausgabedatei.txt

![parameters](https://user-images.githubusercontent.com/84079331/118392865-11ed7600-b63c-11eb-9200-ca44d7a578fa.PNG)

### Implementierung
![UML](https://user-images.githubusercontent.com/84079331/118392938-7c9eb180-b63c-11eb-9798-6b1be29bd364.PNG)

## ImportImageFlight.py
Dieses Skript greift auf die in Agisoft Metashape Professional integrierte Python Bibliothek
Metashape zu. Mithilfe dieser Bibliothek ist es moglich, auf die einzelnen Funktionen
und Parameter der Software aus einem Skript heraus Ein
uss zu nehmen und sich wiederholende
Arbeitsschritte automatisiert ausfuhren zu lassen. Auerdem erlaubt diese Python
Bibliothek Zugri auf Funktionalitaten, auf die in der graschen Ober
ache nicht zugegriffen
werden kann. Zu einer dieser Funktionen gehort die Moglichkeit, verschiedene Sensoren,
welche die verschiedenen Kameramodelle mit ihren Parametern reprasentieren, zuzuweisen.
Werden in einer Auswertung Bilddaten verschiedener Kamerasensoren verwendet, ist
es erforderlich, diese mit getrennten Kameraparametern auszuwerten. Bei Missachtung
dieser Trennung wird im Rahmen der Bundelblockausgleichung eine gemeinsame Korrektur
der Kalibrierungswerte vorgenommen, sodass die Ergebnisse stark verfalscht werden
konnen. Die Implementierung basiert auf der Dokumentation der Python API Metashape
der Agisoft LLC (Agisoft LLC, 2021).

### Zusammenfassung
Das Skript integriert sich in den Standardablauf einer Bearbeitung eines Agisoft Metashape
Professional Projektes. Die Verwendung in der Standard Edition von Agisoft Metashape
ist aufgrund der fehlenden Unterstutzung fur Python Scripting nicht moglich. Das Skript
ubernimmt im Work
ow die Funktionen des Imports der auszuwertenden Bilder. Die Bilder
werden dabei im aktiven Chunk (ein Datencontainer in Agisoft Metashape) innerhalb
einer eigenen Kameragruppe eingeladen. Die Kameragruppe ubernimmt als Bezeichner
den Namen des Bildverzeichnisses und bekommt einen separaten Sensor zugewiesen.
Die Abfolge der einzelnen Bearbeitungsschritte lasst sich wie folgt darstellen:
1. Die Namen alle im Ordner bendlichen Dateien werden aufgelistet, um den Pfad
jedes einzelnen Bildes zusammensetzen zu konnen.
2. Dem aktiven Chunk wird eine neue Kameragruppe mit dem Verzeichnisnamen als
Bezeichner hinzugefugt.
3. Das erste Bild aus dem Verzeichnis wird dem Chunk hinzugefugt, anhand dessen die
Kameraparameter aus den Metadaten abgeleitet werden.
4. Aus den abgeleiteten Kameraparametern wird ein Sensor fur die Kameragruppe
erzeugt bzw. aus diesen die fehlenden Parameter berechnet.
5. Die Liste der Bilder wird durchlaufen und jedes Bild der Kameragruppe hinzugefugt.
Zudem wird jedem Bild der erstellte Sensor zugewiesen.
Der Aufruf des Skriptes muss fur jeden Bild
ug einzeln aufgerufen und wiederholt werden
und erlaubt keine Angabe mehrerer Bildverzeichnisse.

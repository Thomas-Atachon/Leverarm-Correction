This passages come from my bachelor thesis "Optimierung eines GNSS gestützten Bildflugverbandes für photogrammetrische Auswertungen" from the beginning of 2021

# Leverarm-Correction
Die Bearbeitung und Auswertung von Bild
ügen in Auswertesoftware erfordert oft vorab
eine Nachbearbeitung der gemessenen und aufgenommen Sensor- und Bilddaten. Für
diese sich wiederholenden Tätigkeiten bietet sich eine weitere Automatisierung der Arbeitsabl
äufe an, um eine schnelle Bearbeitung und Vermeidung von Bearbeitungs- und
Kopierfehlern zu erreichen. Im folgenden Kapitel werden drei im Rahmen dieser Arbeit
entwickelten Skripte in der Programmiersprache Python erläutert und deren Funktionsweise
beschrieben. Ein besonderer Schwerpunkt liegt auf einer breiten Kompatibilität mit
verschiedenen Python Interpretern. Aus diesem Grund wird auf die Anbindung weiterer
und externer Bibliotheken verzichtet.

## PictureCenter.py
Die photogrammetrische Auswertung von Bild
ügen mit Hilfe von bekannten Bildmitten
kann auf unterschiedliche Weise erfolgen. Jedoch ist es essentiell, die Zuordnung zwischen
Luftbild und Koordinaten herzustellen. Eine Möglichkeit besteht darin, die Bildmitteninformationen
in den Metadaten der einzelnen Luftbilder zu hinterlegen. Dies erfordert
jedoch eine direkte Kommunikation und Anbindung zwischen der Bild- und Positionsbestimmungssensorik, bei der während des Schreibvorgangs der Luftbilder die Position der
Bildaufnahmen in den Metadaten hinterlegt werden.
Eine weitere Möglichkeit besteht darin, die Informationen der einzelnen Sensoren aus den
Logdateien auszulesen und mit den Bildnamen in einer Datei zu verknüpfen. Kann eine solche
Datei nicht automatisiert erstellt werden, ist es erforderlich, die Sensordaten händisch
aus den Logdateien zu kopieren und zusammenzuführen. Eine solche Datei ermöglicht
zudem eine händische Nachbearbeitung und Anpassung.
Das Python Skript PictureCenter bietet dem Anwender die Möglichkeit, eine funktionsf
ähige Bildmittendatei aus verschiedenen Logdateien zu erstellen. Das Skript verknüpft
hierfür alle angegebenen Bilder im angegebenen Verzeichnis mit allen hinterlegten Informationen
über die gemessenen Bildmitten. Die Koordinaten können hierbei aus einer CAM
Datei (reine GNSS Codelösung) sowie aus einer Eventfile (Präzise DGNSS Messung, Justin
Postprocessing) stammen. Durch die Angabe einer Hexalogdatei wird ebenfalls die
Lage des Kopters zum Zeitpunkt der Aufnahme berücksichtigt. Hierfür wird eine Hebelarmkorrektur,
wie in Kapitel 3.1 beschrieben, auf die Bildmittenkoordinaten angewendet.
Zusätzlich erlaubt das Skript das Anbringen eines Offset Wertes an den Höhenwerten,
wodurch z.B. im Fall von unbekannten Roll-, Nick- und Gierwinkeln der Höhenversatz
zwischen Kamerabrennpunkt und GNSS Antenne ohne Hebelarmkorrektur ausgeglichen
werden kann. Durch die Angabe eines Genauigkeitswertes wird dieser jeder Aufnahme in
der Exportdatei angefügt.

### Übergabe der Eingabeparameter
Die Parameterübergabe erfolgt in beliebiger Reihenfolge. Hierfür wird für einen neuen
Parameter als Schlüsselzeichen ein
'-' gesetzt, auf dem der eigentliche Bezeichner folgt. Im
Anschluss an diesen Bezeichner wird nach einem Leerzeichen der Wert des Parameters
angegeben. Weitere Parameter werden anschließend in der gleichen Form übergeben. Das
Listing 3.1 zeigt, wie eine Parameterübergabe erfolgen kann.
Die Tabelle 3.4 gibt eine übersicht über die Eingabeparameter und zeigt auf, welche
als P
ichtparameter angegeben werden müssen und welche optional hinzugefügt werden
können.

−justin Eventdatei.txt −pic Bildflugordner −hex Hexalogdatei.log −o Ausgabedatei.txt

![parameters](https://user-images.githubusercontent.com/84079331/118392865-11ed7600-b63c-11eb-9200-ca44d7a578fa.PNG)

### Implementierung
![UML](https://user-images.githubusercontent.com/84079331/118392938-7c9eb180-b63c-11eb-9798-6b1be29bd364.PNG)

## ImportImageFlight.py
Dieses Skript greift auf die in Agisoft Metashape Professional integrierte Python Bibliothek
Metashape zu. Mithilfe dieser Bibliothek ist es möglich, auf die einzelnen Funktionen
und Parameter der Software aus einem Skript heraus Ein
uss zu nehmen und sich wiederholende
Arbeitsschritte automatisiert ausführen zu lassen. Außerdem erlaubt diese Python
Bibliothek Zugriff auf Funktionalitäten, auf die in der grafischen Ober
äche nicht zugegriffen
werden kann. Zu einer dieser Funktionen gehört die Möglichkeit, verschiedene Sensoren,
welche die verschiedenen Kameramodelle mit ihren Parametern repräsentieren, zuzuweisen.
Werden in einer Auswertung Bilddaten verschiedener Kamerasensoren verwendet, ist
es erforderlich, diese mit getrennten Kameraparametern auszuwerten. Bei Missachtung
dieser Trennung wird im Rahmen der Bündelblockausgleichung eine gemeinsame Korrektur
der Kalibrierungswerte vorgenommen, sodass die Ergebnisse stark verfälscht werden
können. Die Implementierung basiert auf der Dokumentation der Python API Metashape
der Agisoft LLC (Agisoft LLC, 2021).

### Zusammenfassung
Das Skript integriert sich in den Standardablauf einer Bearbeitung eines Agisoft Metashape
Professional Projektes. Die Verwendung in der Standard Edition von Agisoft Metashape
ist aufgrund der fehlenden Unterstützung für Python Scripting nicht möglich. Das Skript
übernimmt im Work
ow die Funktionen des Imports der auszuwertenden Bilder. Die Bilder
werden dabei im aktiven Chunk (ein Datencontainer in Agisoft Metashape) innerhalb
einer eigenen Kameragruppe eingeladen. Die Kameragruppe übernimmt als Bezeichner
den Namen des Bildverzeichnisses und bekommt einen separaten Sensor zugewiesen.
Die Abfolge der einzelnen Bearbeitungsschritte lässt sich wie folgt darstellen:
1. Die Namen alle im Ordner befindlichen Dateien werden aufgelistet, um den Pfad
jedes einzelnen Bildes zusammensetzen zu können.
2. Dem aktiven Chunk wird eine neue Kameragruppe mit dem Verzeichnisnamen als
Bezeichner hinzugefügt.
3. Das erste Bild aus dem Verzeichnis wird dem Chunk hinzugefügt, anhand dessen die
Kameraparameter aus den Metadaten abgeleitet werden.
4. Aus den abgeleiteten Kameraparametern wird ein Sensor für die Kameragruppe
erzeugt bzw. aus diesen die fehlenden Parameter berechnet.
5. Die Liste der Bilder wird durchlaufen und jedes Bild der Kameragruppe hinzugefügt.
Zudem wird jedem Bild der erstellte Sensor zugewiesen.
Der Aufruf des Skriptes muss für jeden Bild
ug einzeln aufgerufen und wiederholt werden
und erlaubt keine Angabe mehrerer Bildverzeichnisse.

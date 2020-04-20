# Work Packages
## Prio 1
These work Packages should indicate the main developer(s) where and what should be implemented next, i.e. which fixes have to made or at least a description of the bug which has occured

Highest priority fixes that influence the useability of the **Pipeline**


### Beta devel fixes for **Pipeline** in intended use-case for OVD-thickness determination
(Melli's BA - description in German)

##### Melli's Bug-Report
- [x] Issue 1.1/1.2: Ist es möglich das Fadenkreuz, mit dem die Punkte beim manuellen Segmentieren ausgewählt werden, in einer anderen Farbe z.B. gelb darzustellen? In Schwarz ist das Fadenkreuz auf dem schwarz-weiß OCT-Bild schwierig zu erkennen. Feste Anzahl an Punkten sehr unvorteilhaft, da Grenzflächen von b-Scan zu b-Scan unterschiedlich lang sind  <br />
-> 1.1 gefixt: Fadenkreuz ist jetzt doppellagig und weiß
-> 1.2 additional fix: keine feste Anzahl an Punkten mehr notwenig - User bestimmt mit Doppelklick das Ende der Segemtierung.

- [x] Issue 2: Wenn bei erster Textbox (Abfrage ob Endothel und OVD-Schicht genügend sichtbar zur Segmentierung) ausgewählt wird, dass nur Endothel und nicht OVD sichtbar ist, springt es nicht zum nächsten Fenster, nachdem der Bildbereich ausgewählt wurde. <br />
-> gefixt: springt in den nächsten b-Scan. Nicht sicher, was die Fehlerursache behoben hat... (evtl. refactoring?) )

- [x] Issue 3: Checken, ob bei reiner Endo-Segementierung die OVD Schicht berechnet wird und dann (fälschlicher Weise) in die Masken geschrieben wird <br />
-> gefixt: Einträge, die vom OVD in die Masken geschrieben werden, werde hart auf 0 gesetzt und damit nicht in den Masken übernommen

- [x] Issue 4: nachdem im ersten bScan beide Layer segmentiert wurden, springt es nicht automatisch zum nächsten BScan.  <br />
-> gefixt: springt nach erfolgreicher Segmentierung zum nächsten b-Scan im Volumen

- [x] Issue 5: Option, wenn keine OVD-Schicht sichtbar -> nicht segmentieren.  <br />
-> gefixt: Option ob beide Schichten (jeweils) sichtbar sind. Wenn nein -> keine Segemtierung nötig

- [x] Issue 6: Randbedingsungsproblem bei Polynomfit - außerhalb vom Bildrand interpolierte Punkte werfen Fehler. <br />
-> gefixt: keine Werte < 0 mehr als valides interpoliertes Ergebnis und in links/ rechts Randbereichen wird die Schicht

- [x] Issue 7: sehr inhomogene Schicht detektierbar? Cornea ist rund und homogen, gut zu segmentieren. Die OVD-Schicht ist oft nur ein Hügel und die Schicht nicht durchgängig von rechts nach links, also sehr inhomogen.  <br /
-> Ja, ist jetzt auch sehr inhomogene Schichten segementierbar

- [x] Issue 8: Wenn textbox "Points are not unique, please reselect!" angezeigt wird, muss man dann die bis dahin gefitteten B-Scans von einem Volumen nochmals fitten, oder kann man nur den einzelnen nochmals wiederholen? Manchmal schließt das Fenster, manchmal springt es zum nächsten Bscan. Bisher kann ich nicht feststellen, woran das liegt.  <br />
-> not really fixable: Jeder Punkt in x (Bildbreite) darf max. einen y-Punkt (in der Bildhöhe) "zugewiesen" haben, da Interpolation sonst nicht eindeutig ist. Bis das passiert, wird dieser Fehler den User neu segmentieren lassen


#### Phils bug reports
- [x] Issue 1: Masken können größer werden, als die eigentlichen Bilder.  <br />
-> fixed: Masken werden anhand der Bildgrößen in gekapselten Funtionen erstellt

- [x] Issue 2: Implement lobal path and file-selection more dynamically, for making it work more easily on different machines and on different drives and directories. <br />
-> fixed: takes the global variable

- [x] Issue 3: If only the Endothel is visible the plotting and mapping plots and masks doesnt work <br />
-> fixed: Added if condition to check to check if the second set of entries (i.e. non-existent boundaries that idicate that no 2nd laver (OVD is visible) empty -> values equal to 0 are ignore when masks are created/ saved

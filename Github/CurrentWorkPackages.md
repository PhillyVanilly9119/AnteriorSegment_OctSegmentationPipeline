# Work Packages
## Prio 1
These work Packages should indicate the main developer(s) where and what should be implemented next, i.e. which fixes have to be made or at least a detailed description of the bug, where and when it occured and so on.

Highest priority fixes that influence the useability of the **Pipeline**


### Beta devel fixes for **Pipeline** in intended use-case for OVD-thickness determination
(Melli's BA - description in German)

##### Melli's Bug-Report
- [x] Issue 1.1/1.2: Ist es möglich das Fadenkreuz, mit dem die Punkte beim manuellen Segmentieren ausgewählt werden, in einer anderen Farbe z.B. gelb darzustellen? In Schwarz ist das Fadenkreuz auf dem schwarz-weiß OCT-Bild schwierig zu erkennen. Feste Anzahl an Punkten sehr unvorteilhaft, da Grenzflächen von b-Scan zu b-Scan unterschiedlich lang sind  <br />
-> 1.1 gefixt: Fadenkreuz ist jetzt doppellagig und weiß
-> 1.2additional fix: keine feste Anzahl an Punkten mehr notwenig - User bestimmt mit Doppelklick das Ende der Segemtierung.

- [ ] Issue 2: Wenn bei erster Textbox (Abfrage ob Endothel und OVD-Schicht genügend sichtbar zur Segmentierung) ausgewählt wird, dass nur Endothel und nicht OVD sichtbar ist, springt es nicht zum nächsten Fenster, nachdem der Bildbereich ausgewählt wurde.

- [ ] Issue 3: Checken, ob bei reiner Endo-Segementierung die OVD Schicht berechnet wird und dann (fälschlicher Weise) in die Masken geschrieben wird

- [x] Issue 4: nachdem im ersten bScan beide Layer segmentiert wurden, springt es nicht automatisch zum nächsten BScan.  <br />
-> gefixt: springt nach erfolgreicher Segmentierung zum nächsten b-Scan im Volumen

- [x] Issue 5: Option, wenn keine OVD-Schicht sichtbar -> nicht segmentieren.  <br />
-> gefixt: Option ob beide Schichten (jeweils) sichtbar sind. Wenn nein -> keine Segemtierung nötig

- [x] Issue 6: Randbedingsungsproblem bei Polynomfit - außerhalb vom Bildrand interpolierte Punkte werfen Fehler. <br />
-> gefixt: keine Werte < 0 mehr als valides interpoliertes Ergebnis und in links/ rechts Randbereichen wird die Schicht

- [x] Issue 7: sehr inhomogene Schicht detektierbar? Cornea ist rund und homogen, gut zu segmentieren. Die OVD-Schicht ist oft nur ein Hügel und die Schicht nicht durchgängig von rechts nach links, also sehr inhomogen.  <br />
-> Ja, ist jetzt auch sehr inhomogene Schichten segementierbar

- [x] Issue 8: Wenn textbox "Points are not unique, please reselect!" angezeigt wird, muss man dann die bis dahin gefitteten B-Scans von einem Volumen nochmals fitten, oder kann man nur den einzelnen nochmals wiederholen? Manchmal schließt das Fenster, manchmal springt es zum nächsten Bscan. Bisher kann ich nicht feststellen, woran das liegt.  <br />
-> not really fixable: Jeder Punkt in x (Bildbreite) darf max. einen y-Punkt (in der Bildhöhe) "zugewiesen" haben, da Interpolation sonst nicht eindeutig ist. Bis das passiert, wird dieser Fehler den User neu segmentieren lassen

- [ ] Issue 9: Wenn Endothel und OVD-Schicht nicht sichtbar (manchmal in Randbereichen der Kornea der Fall) und nicht segmentiert, wird da keine Maske ausgegeben. Ist es möglich, dennoch eine "leere" Maske zu generieren, damit später bei der Auswertung keine Lücke entsteht?

- [ ] Issue 10: bei der manuellen Segmentierung passiert es öfters, dass es nicht zum nächsten Bscan weiterspringt, sondern mit folgender Fehlermeldung abbricht:
      Unrecognized function or variable 'posEndo'.

      Error in segmentaScanDerivative (line 37)
        [~, posesOVD] = maxk(aScan(posEndo+offset:end), 3); %find OVD

      Error in mainSegmentationLoop (line 20)
        [mask, curve] = segmentaScanDerivative(b_Scan, label, frames);

      Error in Run (line 101)
      mainSegmentationLoop(DataStruct, ProcessedOctCube);

      kann es daran liegen, dass der ausgewählte Bereich (wo die Schichten jeweils gut sichtbar sind) von Endothel kleiner ist als von der OVD-Schicht?

- [ ] Issue 11: leider ist der Parabelfit des Endothels nur in den zentralen BScans passend und muss meist noch manuell segmentiert werden


#### Phils Fix-suggestions
- [x] Masken können größer werden, als die eigentlichen Bilder.  <br />
-> fixed: Masken werden anhand der Bildgrößen in gekapselten Funtionen erstellt

- [x] Implement lobal path and file-selection more dynamically, for making it work more easily on different machines and on different drives and directories. <br />
-> fixed: takes the global variable

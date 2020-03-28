# Work Packages
## Prio 1
These work Packages should indicate the main developer(s) where and what should be implemented next, i.e. which fixes have to made or at least a description of the bug which has occured

Highest priority fixes that influence the useability of the **Pipeline**


### Beta devel fixes for **Pipeline** in intended use-case for OVD-thickness determination (Melli's BA)

##### Melli's Bug-Report
- [x] nachdem im ersten bScan beide Layer segmentiert wurden, springt es nicht automatisch zum nächsten BScan.  <br />
-> gefixt: springt nach erfolgreicher Segmentierung zum nächsten b-Scan im Volumen

- [x] Option: keine OVD-Schicht sichtbar -> nicht segmentieren.  <br />
-> gefixt: Option ob beide Schichten (jeweils) sichtbar sind. Wenn nein -> keine Segemtierung nötig

- [x] Randbedingsungsproblem bei Polynomfit - außerhalb vom Bildrand interpolierte Punkte werfen Fehler.  <br />
-> gefixt: keine Werte < 0 mehr als valides interpoliertes Ergebnis und in links/ rechts Randbereichen wird die Schicht

- [x] sehr inhomogene Schicht detektierbar? Cornea ist rund und homogen, gut zu segmentieren. Die OVD-Schicht ist oft nur ein Hügel und die Schicht nicht durchgängig von rechts nach links, also sehr inhomogen.  <br />
-> Ja, ist jetzt auch sehr inhomogene Schichten segementierbar

- [x] Wenn textbox "Points are not unique, please reselect!" angezeigt wird, muss man dann die bis dahin gefitteten B-Scans von einem Volumen nochmals fitten, oder kann man nur den einzelnen nochmals wiederholen? Manchmal schließt das Fenster, manchmal springt es zum nächsten Bscan. Bisher kann ich nicht feststellen, woran das liegt.  <br />
-> not really fixable: Jeder Punkt in x (Bildbreite) darf max. einen y-Punkt (in der Bildhöhe) "zugewiesen" haben, da Interpolation sonst nicht eindeutig ist. Bis das passiert, wird dieser Fehler den User neu segmentieren lassen


#### Phils Fix-suggestions
- [x] Masken können größer werden, als die eigentlichen Bilder.  <br />
-> fixed: Masken werden anhand der Bildgrößen in gekapselten Funtionen erstellt

- [ ] Implement lobal path and file-selection more dynamically, for making it work more easily on different machines and on different drives and directories. <br />
-> fixed: NO

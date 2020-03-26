# Work Packages
These work Packages should indicate the main developer(s) where and what should be implemented next, i.e. which fixes have to made or at least a description of the bug which has occured
## Prio 1

Highest priority fixes that influence the useability of the **Pipeline**
##### Melli
- [x] nachdem im ersten bScan beide Layer segmentiert wurden, springt es nicht automatisch zum nächsten BScan
gefixt: springt nach erfolgreicher Segmentierung zum nächsten b-Scan im Volumen
- [x] Option: keine OVD-Schicht sichtbar
gefixt: Option ob beide Schichten (jeweils) sichtbar sind. Wenn nein -> keine Segemtierung nötig
- [x] Randbedingsungsproblem bei Polynomfit der segmentierten Punkte gelöst (keine Werte < 0 mehr als valides interpoliertes Ergebnis) 
- [ ] sehr inhomogene Schicht detektierbar?
Verstehe den Bug nicht... Kannst beschreiben was du damit meinst?

#### Phil
- [ ] Masken können größer werden, als die eigentlichen Bilder -> checken

#### Main (RUN.m)


#### Concrete functions (Main)
- [ ] example fix: fix it!

#### Abstract functions (Sub)
- [ ] example fix: fix it!

## Prio 2
Quick fixes that only influence the processing
#### Main (RUN.m)
- [ ] example fix: fix it!

#### Concrete functions (Main)
- [ ] example fix: fix it!

#### Abstract functions (Sub)

## Prio 3
Least priority fixes ("Nice-To-Haves")
#### Main (RUN.m)
- [ ] example fix: fix it!

#### Concrete functions (Main)
- [ ] example fix: fix it!

#### Abstract functions (Sub)
- [ ] example fix: fix it!

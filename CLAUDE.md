# Planner – Anleitung für Claude

Pascals eigene Planer-App (früher „Tagesbuch“): eine PWA für Handy (Android), iPad und PC/Laptop.
Live unter https://pxscxlll.github.io/tagesbuch/ (GitHub Pages, Branch `main`).

## ⚠️ Arbeitsweise (Pascals ausdrücklicher Wunsch)
- **Nicht sofort programmieren.** Ideen und Wünsche zuerst gemeinsam besprechen: Vorschlag machen und offene Fragen klären. Erst nach Pascals ausdrücklichem OK anfangen. Das gilt auch für kleine Änderungen.
- Antworten auf Deutsch, kurz und direkt, Pascal mit Vornamen ansprechen.
- Pascal ist kein Programmierer. Fachbegriffe kurz erklären.

## Dateien
- `index.html`: die ganze App (HTML, CSS und JS inline)
- `sw.js`: Service Worker (network-first, `cache:'no-cache'`)
- `manifest.webmanifest`, `icons/`, `datenschutz.html`
- `tools/layout-check.py`: Layout-Prüfung für Handy, iPad und Laptop

## Bei jeder Änderung (nach OK)
1. Versionsnummer an zwei Stellen erhöhen:
   - in `index.html`: `<span class="ver" id="appVer">Version NN</span>`
   - in `sw.js`: `const CACHE = 'planner-vNN';`
2. Testen mit Playwright (Python):
   - Im Repo `python3 -m http.server 8766` starten.
   - Google (Identity, Drive, Calendar) mocken, `service_workers='block'`.
3. **Layout-Check vor dem Push:** `python3 tools/layout-check.py` darf nichts melden. Neue Elemente zusätzlich per Screenshot auf Handy- und Laptop-Breite prüfen.
4. Vor dem Push `git pull --rebase`, weil auch Cloud-Sitzungen in das Repo pushen.
5. Commit-Nachricht auf Deutsch, kurz.
6. Nach dem Push prüfen, ob GitHub Pages veröffentlicht hat (z. B. `gh run list`). Bleibt die Veröffentlichung hängen, einen leeren Commit pushen.

## Daten und Google
- **Daten** liegen nicht im Repo, sondern in Google Drive (appDataFolder, Datei `tagesbuch.json`).
  - Sync nach „letzter Stand gewinnt“, getrennt für Tage, Abos, Tabs, Sportarten, `gsel`, Tab-Reihenfolge, Tab-Namen, gelöschte Tabs, evgen, `uni` und `ideas`.
  - Wöchentliche Backups `planner-backup-JJJJ-MM-TT.json`, die letzten 8 bleiben erhalten.
- **App-Anmeldung:** Scopes `drive.appdata` und `calendar.readonly`.
- **Erinnerungen und Termin-Bearbeitung:** eigener Token Client mit `calendar.events` und `login_hint` pascal.gerlach23@gmail.com, `primary`-Kalender. In der App angelegte Events tragen `extendedProperties.shared.planner = '1'`.

## Datenmodell
- **Pro Tag `days[k]`:** `weight`, `sports`, `tasks` (`{id,text,done,n?}`), `note`, `custom[tabId]`, `checks`, `evnotes`
- **`UNI = {lessons, todos}`:**
  - Lessons: `{id,s,a,r,f,t, d (1–7) | k (Datum), from?, until?, w?}`
  - Todos: `{id,x,from, day | due, done?, n?}`
  - Uni-Modus: `TABSET.uni` (der eingebaute Aufgaben-Tab heißt dann fest „Uni“, bei Pascal so). Früher wurde das über den Tab-Namen erkannt; ohne gespeichertes `TABSET` wird es aus `tabNames.tasks` übernommen.
- **`IDEAS = [{id,x,n?,done?}]`:** Tab „Ideen“, eine Liste ohne Datum.
- **Eigene Tabs:** `customTabs: [{id,name,items:[{id,text,rep,start,until?,n?}],kind?,inotes?,todos?}]` mit `kind` `uni`, `physio` oder `todo`. Physio hat keine Notizen pro Eintrag.
- **To-do-Tab** (`kind: "todo"`, Katalog „To-do“): Aufgaben wie bei Uni (Tag oder Frist, Notizen, verschieben, Frist entfernen), aber im eigenen Speicher `c.todos` (gleiche Form wie `UNI.todos`). Zugriff immer über `todoFind`/`todoList`/`todoSave`; `migrateUni` lässt To-do-Tabs in Ruhe.
- **`TABSET = {on:[ids], uni}`:** sichtbare feste Tabs, synchronisiert als `tabset`. Ohne gespeichertes `TABSET`: Nutzer mit alten Daten sehen alle festen Tabs, neue Nutzer nur `START_TABS` (Alle, Termine, Ideen, Notiz).

## Tabs
- **Alle** (Standard beim Öffnen, ganz links): Termine und Stundenplan des Tages sowie offene Aufgaben, nach Herkunft gruppiert. Nur ansehen und abhaken, Notizen aufklappbar.
- Termine, Gewicht, Sport, Aufgaben (bei Pascal „Uni“: Stundenplan | Aufgaben mit Frist), Notiz, Ideen, eigene Tabs (Physio, To-do)

## Pascals UX-Regeln
- Das Format muss auf Handy, iPad und PC/Laptop stimmen: keine Überschneidungen.
- Nichts doppelt pflegen. Jeder Tab zeigt nur seine Daten, „Alle“ fasst nur zusammen.
- Tabs gibt es nur in der oberen Leiste. Sie lassen sich verschieben, aber nicht umbenennen (feste Namen). Neue Tabs kommen über „+“ aus dem Katalog (`CATALOG`), dort lassen sie sich auch entfernen.
- Beim Öffnen startet die App immer bei Tag → heute → Alle.
- Keine Notiz-Vorschau, nur ein Notiz-Symbol.
- Nie automatisch fokussieren (Tastatur). Einzige Ausnahme ist „+ Übung“.
- So wenig Scrollen wie möglich. Die Seite hat keine Scrollleiste.
- Kein Zoomen am Handy/iPad (weder Doppeltipp noch zwei Finger): Viewport `maximum-scale=1,user-scalable=no`, `touch-action: pan-x pan-y`, `gesturestart` wird blockiert.
- Hover-Effekt auf allen Buttons und Tabs. Ausgewählter Tag mit Rand in der Akzentfarbe, heute mit Datum in der Akzentfarbe.
- Dunkles Design mit genug Kontrast.
- **Farben pro Tab** (`--k-events/weight/sport/tasks/uni/physio/note/ideas`, hell und dunkel): Im Tab ersetzt seine Farbe die Akzentfarbe (`applyTabColor` setzt `--accent` auf `#panel`), in „Alle“ pro Gruppe (`kStyle`). Tabs zeigen Symbol, Name (am Handy nur Symbol) und Farbpunkt (`tabKind`, `TAB_ICONS`).
- **Akzentfarbe** Silber/Rosa/Limette unter Einstellungen, pro Gerät (`tagesbuch:accent`, `data-accent` am html). Gilt für alles ohne eigenen Tab.
- Leere Zustände mit `emptyHtml`, Ladeanimation (`.skel`) solange `ready` falsch ist.
- **Tagesring** hinter dem Datum (nur Tagesansicht, `renderRing`): Anteil erledigter Aufgaben aus „Alle“, bei 100 % ein ✓. Fristaufgaben zählen erst ab ihrem Fristtag (überfällige also weiter), vorher nur, wenn sie an diesem Tag erledigt wurden.
- **Physio-Serie** 🔥 (`physioStreak` → `{run,total}`): Tage in Folge mit allen fälligen Übungen; Tage ohne Übungen zählen nicht, ein offener heutiger Tag unterbricht nicht. Im Physio-Tab und in „Alle“ zusätzlich „✓ N× geschafft“ (alle Tage insgesamt, reißt nicht ab). Jede wiederkehrende Übung zeigt ihre eigene Serie „🔥 N Tage“ (`itemStreak`), in beiden Ansichten.
- **Sport-Serie** (`sportStreak`, oben im Sport-Tab): Wochen Mo–So mit mindestens 2× Krafttraining oder Bouldern (Sportart passt auf `/kraft|bould/i`). Zeigt „Diese Woche x von 2“, „🔥 N Wochen“ in Folge (laufende Woche unterbricht nicht) und „✓ N Wochen in JJJJ“.
- **Frist früh geschafft:** Beim Abhaken einer Fristaufgabe vor dem Fristtag kommt „🎉 N Tage vor der Frist geschafft!“.
- **„läuft gerade“ und Countdown** (`liveStates`, nur für heute) bei Terminen, in „Alle“ und im Stundenplan; wird jede Minute aufgefrischt, außer während man tippt.
- Vor dem Löschen immer nachfragen, mit „Löschen“ und „Abbrechen“.
- Feier beim Abhaken (Uni/Aufgaben, Physio, Alle; nicht Ideen): Häkchen-Pop, Konfetti, Spruch und „… erledigt!“, wenn eine Kategorie komplett ist. Fortschrittsbalken neben dem Kategorienamen (`progHead`), „x von y erledigt“ bleibt sichtbar. Dazu ein Ton (bei „… erledigt!“ die längere Variante).
- Zahnrad oben rechts (`setBtn`) öffnet das Fenster „Einstellungen“ (`setCard`, über der App). Schließen mit ×, Tipp daneben oder Escape. Darin aufklappbare Bereiche (`details.set-sec`), zugeklappt mit Kurzinfo rechts:
  - **Ton** (`setSnd`): an/aus, Lautstärke, Tonart (7 Töne in `SOUNDS`, Standard „Weiches Pling“, mit ▶/★ zum Probehören). Gespeichert nur pro Gerät in `localStorage` (`tagesbuch:snd`), nicht über Drive.
  - **Kalender** (`setCal`): die Kalender-Abos (früher eigener Knopf „Kalender“). `aboOpen` ist wahr, wenn die Karte offen und dieser Bereich aufgeklappt ist.
- Aufgaben bearbeiten (✎): Tagesaufgaben lassen sich auf einen anderen Tag verschieben und im Uni-Tab mit Frist zur Fristaufgabe machen. Fristaufgaben haben „Frist entfernen“; im eingebauten Uni-Tab werden sie dann zur normalen Tagesaufgabe (`uniDropDue`).

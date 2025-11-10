# Jak używać multi-line input w Kimi Writer

## ✅ Naprawione błędy:

1. **Bug z tool_call_id** - Teraz każde wywołanie narzędzia ZAWSZE dostaje odpowiedź, nawet gdy wystąpi błąd
2. **Multi-line input** - Możesz teraz wpisywać wiele linii tekstu interaktywnie

---

## 🎯 Jak użyć multi-line input

### Opcja 1: Tryb interaktywny (bez argumentów)

Po prostu uruchom:
```bash
python kimi-writer.py
```

Potem wpisz wiele linii:
```
Napisz artykuły na tematy:
1. Wprowadzenie do Python
2. Machine Learning dla początkujących
3. Webscrapowanie w praktyce

[naciśnij Enter dwa razy żeby zakończyć]
```

### Opcja 2: Z argumentem w jednej linii

```bash
python kimi-writer.py "Napisz 3 artykuły: Python, ML, Webscraping"
```

### Opcja 3: PowerShell - wklej z pliku

**Stwórz plik `lista.txt`:**
```
Napisz następujące artykuły:
1. Podstawy Pythona
2. Zaawansowane funkcje
3. Programowanie obiektowe
4. Testowanie kodu
5. Dokumentacja projektów
```

**PowerShell:**
```powershell
$tekst = Get-Content lista.txt -Raw
python kimi-writer.py "$tekst"
```

### Opcja 4: CMD - z pliku

**CMD (Windows):**
```cmd
set /p tekst=<lista.txt
python kimi-writer.py "%tekst%"
```

Albo użyj here-string:
```cmd
python kimi-writer.py "$(type lista.txt)"
```

### Opcja 5: Bash/Git Bash

```bash
python kimi-writer.py "$(cat lista.txt)"
```

---

## 📝 Przykład kompletnego workflow:

### 1. Stwórz plik z listą tematów:

**`moje_artykuly.txt`:**
```
Napisz serię artykułów o AI:

1. Co to jest sztuczna inteligencja - wprowadzenie dla każdego
2. Historia AI - od Turinga do ChatGPT
3. Jak działa machine learning w prostych słowach
4. Deep learning i sieci neuronowe wyjaśnione
5. AI w życiu codziennym - praktyczne zastosowania
6. Etyka AI - dylematy i wyzwania
7. Przyszłość sztucznej inteligencji

Każdy artykuł powinien mieć:
- Wprowadzenie
- 3-4 sekcje główne
- Przykłady praktyczne
- Podsumowanie
- Około 2000-3000 słów
```

### 2. Uruchom w PowerShell:

```powershell
# Wczytaj plik
$prompt = Get-Content moje_artykuly.txt -Raw

# Uruchom kimi-writer
python kimi-writer.py "$prompt"
```

### 3. Program automatycznie:
- Stworzy projekt (np. `output/ai_articles/`)
- Napisze wszystkie 7 artykułów
- Każdy jako osobny plik `.md`
- Z pełną treścią (2000-3000 słów każdy)

---

## 🔧 Co zostało naprawione:

### Bug #1: Tool call responses
**Przed:**
```
✗ Error: tool_call_id did not have response message
```

**Po naprawie:**
- Każdy `tool_call_id` ZAWSZE dostaje odpowiedź
- Błędy są łapane i zwracane jako odpowiedź narzędzia
- Program nie wywala się przy błędach w narzędziach

### Bug #2: Single-line input
**Przed:**
```python
prompt = input("> ").strip()  # Tylko jedna linia!
```

**Po naprawie:**
```python
# Multi-line input z automatycznym wykrywaniem końca
lines = []
while True:
    line = input()
    if not line and lines:  # Pusta linia = koniec
        break
    lines.append(line)
```

---

## 💡 Wskazówki:

1. **Tryb interaktywny**: Naciśnij Enter **dwa razy** żeby zakończyć
2. **Z pliku**: Najlepsze dla długich list (10+ artykułów)
3. **Jeden argument**: Najszybsze dla krótkich próśb
4. **Formatowanie**: Możesz używać numeracji, punktorów, akapitów - AI wszystko zrozumie

---

## ✅ Teraz możesz:

- ✓ Wpisywać wiele linii interaktywnie
- ✓ Kopiować listy z plików tekstowych
- ✓ Używać złożonych promptów z instrukcjami
- ✓ Program nie wywala się przy błędach
- ✓ Każde wywołanie narzędzia jest poprawnie obsłużone

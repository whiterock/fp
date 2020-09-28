# fp

Wir haben zuerst die vorgeschlagene Syntax aus dem Angaben-pdf implementiert wobei wir dann an einem Punkt etwas stecken geblieben sind. Ich bin dann nicht mehr weitergekommen und hab mir eine alternative Syntax überlegt und begonnen diese zu implementieren. Fabian konnte schließlich die erste retten und so haben wir nun zwei Implementationen zweier unterschiedlicher Syntax (wobei wir uns trotzdessen stark gegenseitig geholfen haben und eigentlich sehr gut von der Zweigleisigkeit profitieren konnten), genannt `fpd` (d für default wie in der Angabe) und `fpa` (a für alternativ). Die Interpreter haben auch diese Namensgebung - mehr zur Syntax weiter unten.

## how to compile

Python: entfällt.

## how to run

Je nach Version

```bash
python fpd.py file.fpd
```

oder 

```bash
python fpa.py file.fpa
```

Zum Beispiel liegt Beispiel `gen` aus der Angabe in `test_gen.(fpd|fpa)`.

### test_gen.fpd
```lisp
{
append= x->y->cond x {head=x head, tail=append(x tail)y} y,
gen=x->cond x (append(gen(minus x 1)) {head=x, tail={}}) {}
}
gen 3
```
Ausführen liefert
```bash
❯ python fpd.py test_gen.fpd
{'head': 1, 'tail': {'head': 2, 'tail': {'head': 3, 'tail': {}}}}
```

### test_gen.fpa
```lisp
(
    {
        APPEND=<x>(<y>(? x {HEAD=(x HEAD), TAIL=(APPEND (x TAIL) y)} y)), 
        GEN=<x>(? x (APPEND (GEN (- x 1)) {HEAD=x, TAIL={}}) {})
    } 
    (GEN 3)
)
```
Ausführen liefert
```bash
❯ python fpa.py test_gen.fpa
{'HEAD': i'1,
 'TAIL': {'HEAD': i'2, 'TAIL': {'HEAD': i'3, 'TAIL': {}}}}
```

Weil ja schließlich mindestens eine Version bewertet werden muss, entscheiden wir uns für `fpa` und der Rest dieser Readme beschäftigt sich nur mehr damit.

# fpa

## syntax
* Zahl: `zahl`, z.B. `3`, `80`, `-6`
* Operatoren:
    * `+` Addition
    * `-` Subtraktion
    * `*` Multiplikation
    * `/` Division
    * `?` Ternary Operator / Conditional
* Lambda function: `<varname>(...)` wobei `varname` lowercase sein muss und `...` den function body darstellt
* Record: `{IDENTONE=..., IDENTTWO=..., .,.}` wobei die Identifier uppercase sein müssen und `...` die zuzuweisende Expression darstellt, welche eine Zahl, ein anderer Record, eine Lambda function, oder ein Call sein kann. `.,.` weißt darauf hin, dass records beliebig groß sein können (falls ihr Computer den nötigen RAM hat)
* Call: `(callee arg1 arg2 arg3 ...)` wobei die argumente beliebig sind. Die Ausführung eines calls hängt vom callee ab:
    * Lambda function: Wird mit dem letzten Argument aufgerufen. Die restlichen werden rekursiv als call_stack nach innen weitergegeben.
    * Record: Der Eintrag des Records mit dem Identifier oder Call arg1 wird evaluiert. Es muss genau ein Argument übergeben werden, sonst Fehler.
    * Operator:
        * `*` und `+`: Beliebig viele argumente, also z.b. `(+ 1 2 3 4)`
        * `/` und `-`: Genau zwei Argumente, also z.B. `<x>(- x 1)` oder `(/ 8 2)`
        * `?`: Genau drei Argumente mit der Semantik `(? condition then else)`. Condition ist dann erfüllt wenn sie zu ungleich 0 evaluiert. Siehe z.B. das Beispiel zur Fakultät weiter unten.
        
Betrachten wir das Beispiel der Fakultät (an diesem wir auch Rekursion sehen können):
```lisp
({FAC=<x>(? x (* x (FAC (- x 1))) 1)} (FAC 4))
```
Zuerst stecken wir unsere Fakultätsfunktion in einen Record um sie leicht rekursiv aufrufen zu können. Dann betrachten wir die Variable x, falls Sie ungleich 0 ist, so machen wir einen call der `x` multipliziert mit dem Ergebnis eines rekursives Aufrufs von `FAC` dessen Argument `(- x 1)` ist, also eines weniger als `x`, andernfalls geben wir 1 zurück, was auch die Rekursion stoppt. Um nun diese Funktion aufrufen zu können, packen wir Sie in einen Call mit dem Record als Callee und haben nun im (einzigen) Argument Zugriff darauf, wo wir FAC mit 4 ausführen. Alternativ kann man auch wie folgt vorgehen:
```lisp
(({FAC=<x>(? x (* x (FAC (- x 1))) 1)} FAC) 4)
```
In beiden Fällen lautet das Ergebnis 24.

## testing

Klarerweise wurde während der Implementation die ganze Zeit getestet. Folgende Tests haben sich als nützlich herausgestellt beim Einführen neuer Features während des Entwicklungsprozesses das Brechen älterer Features zu erkennen bzw. zu verhindern:

```python
assert parse("(+ 5 (* 3 9))").eval() == 32
assert parse("(((+ 5 ((((* ((3)) 9)))))))").eval() == 32
assert parse("(<x>(* 5 x) 3)").eval() == 15
assert parse("(<y>(<x>(- y x)) 5 3)").eval() == 2
assert parse("(<y>(((<x>(- y x)))) 3 5)").eval() == -2
assert parse("((<y>(<x>(- y x)) 5) 3)").eval() == 2
assert parse("((<y>(<x>(- y x)) 3) 5)").eval() == -2
assert parse("({A = 5, B = <x>(+ A x)} (B 11))").eval() == 16
assert parse("({A = 5, B = <x>(+ A x)} (B A))").eval() == 10
assert parse("({FAC=<x>(? x (* x (FAC (- x 1))) 1)} (FAC 4))").eval() == 24
assert parse("(({FAC=<x>(? x (* x (FAC (- x 1))) 1)} FAC) 4)").eval() == 24
assert parse("({A=8, B={C=3}} (B C))").eval() == 3
assert parse("(<x>(x A) {A=5})").eval() == 5
```

### complexity

Zur Laufzeit von parse lässt sich sagen, dass, bezeichne `n` die Länge des Programms als Input, mindestens ein Zeichen behandelt wird und pro Zeichen mit maximal konstanter Anzahl an Aufrufen alle Zeichen danach betrachtet werden. Pro Zeichen lässt sich dieser Aufwand dann mit `cn` von oben beschränken und damit erhalten wir insgesamt die worst case performance von parse mit `O(n^2)`

Die Laufzeit des Evaluierens hängt klarerweise von dem zu interpretierenden Programmes ab.

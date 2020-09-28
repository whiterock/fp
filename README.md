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

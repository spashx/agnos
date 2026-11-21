# agnos-perf-center — call graph : analyse opérationnelle et recommandations

**Destinataire** : agent chargé de définir les exigences d'évolution.
**Objet** : qualité du graphe d'appels produit par `callgraph.py` et de ses effets sur le contrôle `functions-traced`.
**Statut** : analyse statique du code source. Aucun ID AGNOS nouveau n'est proposé ici — la définition des exigences reste à votre charge.

---

## 1. Périmètre et méthode

**Base analysée** : `spashx/agnos`, branche `dev`, clone superficiel.

| Artefact | Rôle dans l'analyse |
|---|---|
| `.github/skills/agnos-perf-center/scripts/callgraph.py` (405 l.) | lu intégralement |
| `assets/callgraph/*.scm` (7 fichiers) | lus intégralement |
| `assets/callgraph/languages.json` | lu |
| `requirements-callgraph.txt` | versions épinglées des grammaires |
| `references/rules.md`, `references/data-format.md` | contrat de scoring et de données |
| `agnos-process/1.requirements/FTR-TRC-002-call-graph.md` | exigences en vigueur |
| `tests/test_callgraph.py` (966 l.), `tests/test_languages.py` (179 l.) | comportement épinglé |
| `tests/fixtures/repo/calls/`, `tests/fixtures/languages/` | couverture de test réelle |

**Niveaux de preuve employés ci-dessous** :

- **[P]** *prouvé* — établi par lecture du code, d'un `.scm` ou d'une assertion de test, avec référence `fichier:ligne`.
- **[D]** *déduit* — conséquence logique du code, non exercée par un test ; demande une vérification empirique.
- **[V]** *à vérifier* — dépend d'un nom de nœud tree-sitter que je n'ai pas pu confirmer sur les grammaires épinglées (environnement sans réseau, grammaires non installées).

**Versions épinglées** (`requirements-callgraph.txt`) : `tree-sitter==0.25.2`, `tree-sitter-c==0.24.1`, `tree-sitter-cpp==0.23.4`, `tree-sitter-c-sharp==0.23.5`, `tree-sitter-java==0.23.5`, `tree-sitter-javascript==0.25.0`, `tree-sitter-python==0.25.0`, `tree-sitter-rust==0.24.2`. Toute vérification des points **[V]** doit se faire sur ces versions exactes.

---

## 2. Rappel du critère d'arbitrage

Le call graph n'entre dans le score que par un seul contrôle. `references/rules.md:42` :

> `Functions traced (functions-traced)` | medium | functions (with `--call-graph`; no score without it) | **functions citing no ID**

Deux conséquences qui bornent toute évolution :

1. **La couverture des exigences ne passe pas par les arêtes d'appel.** `rules.md:14` définit `indirect` par la chaîne d'artefacts process (DEC, TASK, ADR, PLAN, FTR), jamais par un appel de fonction. **[P]**
2. **Le contrôle `functions-traced` n'utilise aucune arête.** Il ne lit que `function["ids"]`, peuplé en `callgraph.py:198-200` depuis `cited`.  **[P]**

**Critère retenu pour prioriser** : *ce qui fausse le score passe avant ce qui dégrade la lisibilité du graphe.* Un seul défaut identifié fausse le score (§4, R1). Les autres n'affectent que la justesse des arêtes, donc l'exploitabilité de la page.

---

## 3. Principe directeur et options écartées

Le perf center mesure l'**implémentation** : le code qui exécute une implémentation. L'unité de traçabilité est donc la fonction, et chaque fonction doit citer son propre ID. `FTR-TRC-002-call-graph.md:86-88` l'énonce :

> The trace generator SHALL link a function to every AGNOS ID written in its line range or in the comment just above […] *Rationale* : AGNOS puts requirement IDs in doc comments; the function is where they belong.

Deux évolutions ont été examinées et **doivent être écartées**. Elles paraissent séduisantes et un agent qui analyserait le code sans ce principe les proposerait. Elles sont consignées ici pour éviter leur réintroduction.

### 3.1 — ÉCARTÉE : faire hériter les IDs du scope englobant

**Constat technique** : `callgraph.py:193` n'itère que sur `caps[DEFINITION]`. `caps[SCOPE]` ne sert qu'à `scope_names` (l. 177) et `declared_scopes` (l. 210). Un ID placé dans le bloc de commentaires au-dessus d'une classe n'est donc attaché à aucune fonction, et chaque méthode de cette classe reste un constat de `functions-traced`. **[P]**

**Motif de rejet** : un ID sur une classe ne prouve rien sur l'implémentation. Il n'établit aucune trace vers le corps des méthodes, qui est le code effectivement exécuté. Le faire hériter transformerait un constat juste en conformité apparente — c'est-à-dire en faux négatif de contrôle, le défaut le plus coûteux pour un outil de traçabilité. Le comportement actuel est conforme à l'intention et à `FTR-TRC-002`.

**À retenir pour la rédaction des exigences** : toute exigence d'évolution doit préserver explicitement cette propriété. Ne pas la formuler comme une limitation à corriger.

### 3.2 — ÉCARTÉE : un palier « tracée indirectement » pour `functions-traced`

**Proposition examinée** : une fonction sans ID, appelée uniquement par des fonctions tracées, serait réputée tracée indirectement — par analogie avec le palier `indirect` des exigences.

**Motif de rejet** : identique, et plus grave car il porte sur le score. L'appelant tracé ne dit rien de l'implémentation de l'appelé. De plus, l'arête qui fonderait la déduction peut elle-même être fausse : §4-R4 et §5 montrent que les arêtes comportent des hypothèses non résolues. Fonder un score sur une résolution heuristique, c'est importer l'incertitude du graphe dans le score de qualité.

**À retenir** : les arêtes d'appel sont un support d'exploration et de diagnostic. Elles ne doivent pas devenir une source de conformité.

---

## 4. Recommandations

### R1 — Détecter les fichiers qui ne parsent pas

**Priorité : haute. C'est le seul défaut identifié qui fausse le score, et dans le sens dangereux.**

**Constat [P]** : `callgraph.py:68-69`

```python
def parse(self, language, data):
    return self.api.Parser(language).parse(data).root_node
```

Aucun appel à `root.has_error`, `is_error` ou `is_missing` n'existe dans `scripts/` (vérifié par recherche sur l'ensemble des scripts du skill). Le parseur de tree-sitter est tolérant aux erreurs : il produit toujours un arbre, en y insérant des nœuds `ERROR` et `MISSING`.

**Impact [D]** : un fichier syntaxiquement cassé, ou écrit dans un dialecte que la grammaire épinglée ne couvre pas, produit un arbre dégradé, donc peu ou pas de `@definition`. Les fonctions absentes du graphe ne peuvent pas être signalées comme non tracées. **Le score `functions-traced` est donc gonflé par un échec de parsing.** `files-traced` ne compense pas : il ne regarde que les citations d'ID du fichier, pas sa structure. Le `summary()` (l. 339-347) ne mentionne que les paquets manquants, jamais un parsing dégradé.

Ce mode de défaillance est silencieux et monotone dans la mauvaise direction : plus un fichier est cassé, meilleur paraît le score.

**Proposition** : exposer la détection d'erreur comme une donnée de premier ordre.

1. Relever `root.has_error` par fichier dans `file_functions` (l. 184) ou dans `analyse` (l. 395).
2. Ajouter un compteur à `CallGraph` (l. 330-337) et la liste des fichiers concernés.
3. L'inscrire dans `summary()` (l. 339) et dans `callGraph.counts` (l. 374), donc dans `references/data-format.md:64`.
4. Décision de process à prendre : un fichier non parsable doit-il être un constat de qualité à part entière, ou seulement une mention ? Un constat est défendable : un fichier illisible par l'outil n'est pas un fichier tracé.

**Vérification** : ajouter à `tests/fixtures/languages/` un fichier volontairement cassé par langage, et affirmer que le compteur le signale. Nommage à respecter : `test_<ID>_given_..._when_..._then_...` (convention observée dans `test_languages.py`, ID en doc comment selon `DEC-PLG-021`).

**Coût** : faible. Trois à cinq lignes de Python. Aucun `.scm` à modifier. Commun aux 7 langages, car `has_error` est une propriété du cœur de tree-sitter et non d'une grammaire.

**Risque** : la valeur de `callGraph.counts` change, donc le hash épinglé des pages de test (`test_callgraph.py:32`, `DATA_BEFORE_PLAN_SHA256`) devra être re-épinglé.

---

### R2 — Décomposer le compteur `external`

**Priorité : haute, comme prérequis d'arbitrage.** Sans cette décomposition, les recommandations R3 à R6 ne peuvent pas être priorisées sur des mesures.

**Constat [P]** : `callgraph.py:269-274`

```python
for (caller_index, name), lines in grouped.items():
    caller = graph.functions[caller_index]
    candidates = definitions.get((caller[LANGUAGE_FUNCTION], name), [])
    chosen = preferred(caller, candidates, separators[...]) if candidates else []
    if not chosen:
        graph.external += 1
```

`external` agrège quatre causes hétérogènes :

| Cause | Nature | Référence |
|---|---|---|
| appel à une bibliothèque hors périmètre | **normal**, non corrigible | — |
| appel de constructeur non résolu | **arête interne manquée** | §R4 |
| appel inter-langages | limite de conception | `callgraph.py:264`, clé `(langue, nom)` |
| nom rejeté en amont par `NAME_RE` | non compté ici, abandonné en `l. 229` | `callgraph.py:50`, `229` |

**Preuve que la confusion est réelle et déjà visible [P]** : `tests/test_languages.py:140`

```python
self.assertEqual((0, 2), (self.graph.ambiguous, self.graph.external))      # print, the class Greeter()
```

Dans cette unique assertion, la valeur `2` additionne un appel de bibliothèque légitime (`print`) et une arête interne manquée (`Greeter()`). Le nombre ne permet pas de les distinguer : le commentaire du test est la seule source d'information.

**Proposition** : remplacer le compteur unique par une ventilation par cause dans `CallGraph` puis dans `callGraph.counts`. Compter aussi les noms abandonnés par `NAME_RE` en `l. 229`, aujourd'hui invisibles de bout en bout.

**Vérification** : réécrire l'assertion ci-dessus en distinguant les deux causes, ce qui documentera au passage le défaut R4 au lieu de le dissimuler dans un commentaire.

**Coût** : faible. Pur Python, aucun `.scm`.

---

### R3 — Conserver le récepteur de l'appel

**Priorité : haute. Meilleur rapport gain/coût de l'ensemble.**

**Constat [P]** : `callgraph.py:135-137`

```python
def last_part(name):
    """The name a call is looked up by: the last part of 'a.b->c::d'."""
    return MEMBER_RE.split(name)[-1]
```

Appelé en `l. 228`, `last_part` jette tout ce qui précède le dernier segment. `self.f()`, `this.f()`, `autre.f()` et `Type::f()` deviennent indiscernables : tous se réduisent à `f`.

**Impact [D]** : la résolution perd une information qui, pour `self` et `this`, est **certaine** et non heuristique — l'appelé appartient à la classe de l'appelant ou à l'un de ses ancêtres. `preferred` (l. 239-254) ne peut alors que *préférer* la classe de l'appelant, au lieu de *restreindre* à celle-ci. Lorsque le nom est fréquent, le nombre de candidats peut dépasser `MAX_AMBIGUOUS = 5` (l. 43) et **l'arête est perdue** (l. 275-276).

Cas d'amplification identifiés **[D]** :

- Python : `super().__init__()` se réduit à `__init__`, donc à l'ensemble des `__init__` du projet.
- Rust : `Foo::new()` se réduit à `new`, donc à l'ensemble des `new` du projet — convention quasi universelle en Rust.
- Tout langage : `get`, `run`, `name`, `value`.

**Proposition** : conserver le préfixe produit par `plain_name(text_of(expression))` avant l'appel à `last_part`, le transporter jusqu'à `resolve`, puis ajouter à `preferred` un niveau de restriction préalable :

- récepteur `self` / `this` → restreindre aux candidats de la classe de l'appelant, puis de ses ancêtres (dépend de R5) ;
- récepteur qualifié par un type ou un namespace connu (`Type::f`, `Mod.f`) → restreindre aux candidats de ce scope ;
- récepteur inconnu (variable locale) → comportement actuel inchangé.

Attention à la distinction sémantique : restreindre et préférer ne sont pas la même opération. Pour un récepteur certain, une liste vide après restriction est une information valide (l'appelé est hors périmètre) et doit compter en `external`, non retomber sur l'ensemble du projet.

**Vérification** : un cas par langage opposant `self.f()` et `autre.f()` avec deux définitions homonymes dans des classes distinctes ; affirmer que seule la bonne arête existe. Un cas Python avec six `__init__` et un `super().__init__()`, affirmant que l'arête est créée alors qu'elle est aujourd'hui perdue.

**Coût** : faible à moyen. Entièrement en Python, **aucun fichier `.scm` à écrire** — l'expression appelée est déjà capturée par `@call.name` dans les 7 langages. C'est le seul gain de précision substantiel qui n'ajoute aucun coût par langage.

---

### R4 — Capturer les appels de constructeurs

**Priorité : moyenne. Exige une décision de process avant implémentation, car le comportement actuel est épinglé par un test.**

**Constat [P]** : aucun des 7 fichiers `.scm` ne capture `object_creation_expression` ni `new_expression` (recherche exhaustive sur `assets/callgraph/*.scm`). Les captures d'appel sont :

| Langage | Capture d'appel | Constructeur capturé comme définition ? |
|---|---|---|
| java | `(method_invocation name: (identifier) @call.name) @call` | **oui**, `(constructor_declaration …) @definition`, nommé `Foo` |
| csharp | `(invocation_expression function: (_) @call.name) @call` | **oui**, `(constructor_declaration …) @definition`, nommé `Foo` |
| cpp | `(call_expression function: (_) @call.name) @call` | **oui** via `function_definition` **[D]** |
| javascript | `(call_expression function: (_) @call.name) @call` | **oui** via `method_definition`, nommé `constructor` |
| python | `(call function: (_) @call.name) @call` | `__init__` seulement ; la classe est un `@scope`, jamais un `@definition` |
| rust | `(call_expression function: (_) @call.name) @call` | sans objet (`Foo::new()` est un appel ordinaire) |
| c | `(call_expression function: (_) @call.name) @call` | sans objet |

**Preuve que le défaut est épinglé, non ignoré [P]** : `tests/test_languages.py:137-140` affirme que l'instanciation `Greeter()` du fixture Python compte en `external`. Le commentaire du test la nomme explicitement. **Ce n'est donc pas un bug latent : c'est un comportement spécifié par le test.** Toute évolution implique de re-épingler cette assertion, et donc une décision tracée.

**Preuve du cas non exercé [P]** : `tests/fixtures/languages/java/Greeter.java` définit `public Greeter() {}`, capturé comme fonction (`test_languages.py:80-82` affirme `demo.shapes.Greeter.Greeter` parmi les fonctions), mais aucun fixture ne l'instancie. Même situation en C#. Le constructeur est donc un **nœud orphelin** : présent dans le graphe, sans aucune arête entrante. Le défaut existe mais n'est aujourd'hui pas exercé par les tests sur ces deux langages.

**Impact [D]** : les constructeurs apparaissent comme jamais appelés. La page les affiche en racines, ce qui fausse toute lecture de la structure d'appel. Le chaînage se rompt en amont du code d'initialisation, qui est souvent le plus porteur d'exigences.

**Proposition**, par langage, avec le coût réel de résolution :

- **java, csharp** — capturer `object_creation_expression` avec le type en `@call.name` **[V]**. La résolution fonctionne alors **sans aucune autre modification**, puisque le constructeur est déjà une définition nommée `Foo` : `last_part("Foo")` donne `Foo`, qui est la clé de `definitions`. Rapport gain/coût le plus favorable.
- **cpp** — capturer `new_expression` **[V]**. À noter que la construction sur la pile (`Foo f(1);`) est une déclaration et non une expression d'appel : elle restera hors du graphe. À arbitrer explicitement dans l'exigence pour éviter une attente non tenue.
- **javascript** — capturer `new_expression` **[V]** ne suffit pas : le nom capturé serait `Foo` alors que la définition est nommée `constructor`. Demande un mappage dans `resolve`.
- **python** — l'instanciation est déjà capturée comme `call`, mais aucune définition ne porte le nom de la classe. Demande un mappage classe → `__init__`, donc l'accès au scope depuis la résolution. C'est le cas le plus coûteux.

**Recommandation d'étagement** : traiter java et csharp d'abord (une ligne de requête chacun, aucun code), puis arbitrer cpp, javascript et python sur la base des mesures issues de R2. L'intérêt de R2 apparaît ici : sans la ventilation d'`external`, rien ne dit si ces appels sont nombreux dans les projets réels.

**Rappel de contrainte** : `references/rules.md:52-55` pose que les langages sont des données — ajouter un langage ne doit pas modifier les scripts. Les variantes javascript et python ci-dessus demandent du code, donc dérogent à ce principe. L'exigence devra soit assumer la dérogation, soit porter le mappage dans `languages.json` pour préserver la propriété.

---

### R5 — Ajouter un niveau « classes ancêtres » à la résolution

**Priorité : moyenne.**

**Constat [P]** : `callgraph.py:239-254`

```python
scope = caller[KEY_SCOPE]
namespace = scope.rpartition(separator)[0]
levels = (
    lambda f: scope and f[KEY_SCOPE] == scope,
    lambda f: namespace and f[KEY_SCOPE] == namespace,
    lambda f: f[KEY_FILE] == caller[KEY_FILE],
    lambda f: folder_of(f[KEY_FILE]) == folder_of(caller[KEY_FILE]),
)
```

Le niveau classe est une **égalité de chaîne** sur le scope qualifié.

**Impact [D]** : une méthode héritée a par construction un scope différent de celui de l'appelant. Elle ne satisfait jamais le niveau 1. Le niveau 2 ne la rattrape pas : `f[KEY_SCOPE] == namespace` ne sélectionne que les fonctions dont le scope est *exactement* le namespace, c'est-à-dire les fonctions libres — pas les méthodes d'une classe sœur. Un appel à une méthode héritée retombe donc sur le niveau fichier, puis dossier, puis projet entier, avec le risque de dépassement de `MAX_AMBIGUOUS` et de perte de l'arête.

Ce défaut touche en priorité java, csharp, cpp et python, où l'héritage est structurant.

**Proposition** : capturer la clause d'héritage (`superclass` / `extends` / `implements` / `base_clause` / liste de classes de base / `argument_list` de `class_definition` en Python) **[V]** dans un nouveau nom de capture, construire la chaîne d'ancêtres par scope qualifié, et insérer un niveau entre le niveau 1 et le niveau 2 de `preferred`.

**Point d'attention d'implémentation [P]** : `captures_of` (l. 140-150) comporte un `break` sur un ordre fixe de kinds et ne retient que `caps[kind][0]`, soit **un seul nœud par nom de capture et par match**. Ajouter un nom de capture impose de modifier le tuple de la l. 145, et une clause d'héritage à plusieurs types (`implements A, B`) ne peut pas être capturée sous un nom unique sans perdre les types suivants. À concevoir en conséquence.

**Coût** : moyen. Un pattern par langage, plus du code de résolution. À engager après R3, dont il est complémentaire : la restriction par `self` n'a tout son effet que si les ancêtres sont connus.

---

### R6 — Filtrer par arité

**Priorité : basse.**

**Constat [P]** : rien dans `callgraph.py` ne lit le nombre de paramètres d'une définition ni le nombre d'arguments d'un appel. La résolution est exclusivement nominale (`l. 264`, `l. 271`).

**Impact [D]** : les surcharges — C++, Java, C# — ne sont pas discriminées. Toutes les variantes d'un même nom sont candidates, ce qui alimente le compteur `ambiguous` et les dépassements de `MAX_AMBIGUOUS`.

**Proposition** : compter les arguments au site d'appel et les paramètres à la définition, puis l'utiliser comme filtre *avant* `preferred`. Le filtre doit être non bloquant : arguments par défaut, variadiques, paramètres implicites et `this` explicite rendent l'égalité stricte fausse. Un filtre « arité compatible » plutôt que « arité égale ».

**Coût** : moyen. Le nom du champ des paramètres diffère par langage (`parameters` en python et java, `declarator` en cpp), ce qui impose une entrée supplémentaire dans `languages.json` pour respecter `rules.md:52-55`. Gain limité aux projets à fortes surcharges. À n'engager que si R2 démontre que la part d'`ambiguous` le justifie.

---

### R7 — Rendre visibles les appels hors fonction

**Priorité : basse, à arbitrer.**

**Constat [P]** : `callgraph.py:229`

```python
if stack and NAME_RE.match(name):
```

Une pile vide signifie que l'appel n'est contenu dans aucune définition. L'appel est alors purement abandonné : il n'apparaît ni en arête, ni en `external`, ni en `ambiguous`.

**Impact [D]** : le code d'initialisation au niveau module — fréquent en Python, JavaScript et Rust — est invisible. Il n'est ni tracé, ni signalé comme non tracé.

**Décision de process requise** : au regard du principe du §3, l'unité de traçabilité est la fonction. Un appel au niveau module n'appartient à aucune fonction, donc n'a rien à tracer. Deux lectures défendables :

1. **Statu quo justifié** : ce code ne relève pas de `functions-traced`. Il relève de `files-traced`, qui le couvre déjà par la citation d'ID du fichier.
2. **Lacune à combler** : ce code s'exécute, donc il implémente. Une pseudo-fonction par fichier le rendrait visible et traçable.

Je recommande de **trancher explicitement** plutôt que de laisser l'abandon implicite dans le code. Au minimum, compter ces appels (cf. R2) pour en mesurer le volume avant de décider.

---

## 5. Précision de vocabulaire à fixer dans les exigences

Le mot « arête » et le mot « appel » ne désignent pas la même chose, et la page affiche les deux sous le même intitulé. À clarifier avant toute exigence chiffrée.

**Constat [P]** : `callgraph.py:281-284`

```python
link = links.setdefault((caller_index, index[id(callee)]), [ambiguous, set()])
link[1].update(lines)
...
graph.calls = [[caller, callee, ambiguous, sorted(lines)] for (caller, callee), (ambiguous, lines) in sorted(links.items())]
```

Une arête est un quadruplet `[index appelant, index appelé, ambigu, [lignes]]`, **agrégé par paire (appelant, appelé)**.

| Propriété | Conséquence | Preuve |
|---|---|---|
| Une arête agrège tous les sites d'appel d'une paire | dix appels de `f` vers `g` donnent **une** arête à dix lignes | `l. 281-282` |
| `len(self.calls)` compte des paires | le libellé « N calls » de `summary()` est un **nombre d'arêtes** | `l. 283`, `l. 343` |
| Un site d'appel produit 0, 1, ou 2 à 5 arêtes | 0 si `external`, si `> MAX_AMBIGUOUS`, si `NAME_RE` rejette, si hors fonction | `l. 229`, `274-282` |
| Une arête `ambiguous` est une **hypothèse** | de 2 à 5 arêtes mutuellement exclusives ; une au plus correspond à l'appel réel | `l. 278-282` |
| `ambiguous` et `external` comptent des couples `(appelant, nom)` | pas des arêtes, pas des sites d'appel | `l. 267`, `274-279` |

**Conséquence opérationnelle** : les quatre valeurs de `callGraph.counts` (`functions`, `calls`, `ambiguous`, `external`) ne sont ni additionnables ni comparables entre elles — trois échelles différentes. Une exigence qui porterait un seuil sur ces nombres doit d'abord fixer l'unité. C'est une raison supplémentaire d'engager R2.

C'est aussi l'argument de fond du §3.2 : un graphe qui contient des disjonctions non résolues ne peut pas fonder un score de conformité.

---

## 6. Limites de conception à documenter, non à corriger

Ces points ne sont pas des défauts. Ils devraient figurer dans la documentation pour éviter des exigences mal ciblées.

| Limite | Preuve | Commentaire |
|---|---|---|
| Aucune arête inter-langages possible | `l. 264` : `definitions` est clé par `(langue, nom)` | par conception ; gonfle `external` sur un dépôt polyglotte |
| Les noms non conformes sont abandonnés | `l. 50`, `l. 229` : `NAME_RE` rejette `(*fp)` | pointeurs de fonction, appels calculés : hors de portée d'une analyse syntaxique |
| Au-delà de 5 candidats, aucune arête | `l. 43`, `l. 275-276` | choix assumé ; R3 réduit la fréquence du cas plutôt que le seuil |
| C n'a pas de scope | `languages.json`, entrée `c` sans clé `scopes` ; `l. 310`, `l. 323` | conforme au langage |
| Le genre d'un scope non déclaré est deviné | `l. 316` : classe si partie la plus interne, sinon namespace | heuristique documentée en `DEC-TRC-019` |

---

## 7. Synthèse priorisée

| # | Recommandation | Effet | Coût | `.scm` ? | Dépendance |
|---|---|---|---|---|---|
| **R1** | détecter les erreurs de parsing | **corrige un score faussé** | faible | non | — |
| **R2** | décomposer `external` | rend la qualité mesurable | faible | non | — |
| **R3** | conserver le récepteur | précision des arêtes | faible/moyen | **non** | — |
| **R4a** | constructeurs java, csharp | arêtes manquantes | faible | oui, 1 ligne | décision + re-épinglage |
| **R5** | niveau ancêtres | précision des arêtes | moyen | oui | après R3 |
| **R4b** | constructeurs cpp, js, python | arêtes manquantes | moyen | oui + code | après R2 |
| **R6** | filtre d'arité | précision des arêtes | moyen | oui + `languages.json` | après R2 |
| **R7** | appels hors fonction | décision de process | faible | non | mesurer d'abord |

**Séquence recommandée** : R1 et R2 d'abord, indépendamment — R1 parce qu'il corrige le score, R2 parce qu'il conditionne tout arbitrage ultérieur. Puis R3, meilleur gain sans coût par langage. Puis R4a. Les autres sur la base des mesures que R2 aura rendues disponibles.

---

## 8. Fonctions nouvelles envisageables

Compatibles avec le principe du §3, car elles servent l'exploration et le diagnostic, non la conformité.

1. **Racines et fonctions inatteignables**, calculables depuis `graph.calls` à coût nul. Double usage : exploration de la page, et **diagnostic** — une proportion élevée de constructeurs parmi les racines est la signature directe du défaut R4. À ne pas transformer en constat de qualité : une fonction inatteignable par analyse statique n'est pas pour autant non tracée (point d'entrée, callback, réflexion).
2. **Analyse d'impact inverse** : quelles exigences atteignent une fonction donnée. `callGraph.ids` et `callGraph.calls` suffisent. C'est le cas où la propagation le long des arêtes est légitime, puisqu'elle sert à explorer et non à attribuer une conformité. Préciser dans l'interface que les arêtes `ambiguous` sont des hypothèses.
3. **Détection de cycles**, uniquement si la fonction 2 est retenue, pour borner le parcours.

---

## 9. Ce qui n'a pas été vérifié

Honnêteté méthodologique — à lever avant rédaction des exigences :

- **Noms de nœuds tree-sitter marqués [V]** : `object_creation_expression`, `new_expression`, et les nœuds de clause d'héritage n'ont pas pu être confirmés sur les versions épinglées. L'environnement d'analyse était sans accès réseau et les grammaires n'étaient pas installées. **À confirmer avant toute rédaction** : `pip install -r requirements-callgraph.txt` puis inspection de l'arbre sur un cas minimal par langage.
- **Aucune exécution** : `callgraph.py` n'a pas été lancé, aucun test n'a été exécuté. Tous les points **[D]** sont des déductions de lecture, non des mesures. Chaque recommandation est assortie d'une procédure de vérification à cette fin.
- **`perf_center.py` et `scorecard.py` n'ont pas été lus intégralement** — seules les lignes relatives au call graph et au scoring. Il est possible qu'une partie du traitement attendu existe déjà en aval ; à confirmer avant d'ouvrir une exigence sur R1 et R2.
- **Volumétrie réelle inconnue** : aucune mesure de la fréquence des cas R3 à R7 sur un projet réel. C'est précisément ce que R2 permettrait d'obtenir, et c'est la raison de le placer en tête malgré son absence d'effet direct sur la qualité du graphe.

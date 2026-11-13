<!--
FTR-WEB-001 : RQ-WEB-003 à RQ-WEB-012 / ADR-WEB-001 : DEC-WEB-003. Site AGNOS, texte français.
Modifiez librement les mots ; gardez la structure, puis relancez le build du skill agnos-meta-website.
- "## <section>" ouvre un élément de la page, "### <champ>" l'un de ses textes. Gardez ces identifiants identiques dans
  en.md et fr.md : le build refuse un champ absent d'une langue, ou inconnu du gabarit de la page.
- Un champ est un paragraphe, une liste d'éléments "- ", un extrait d'index entre deux lignes ``` (les lignes
  commençant par @ sont atténuées), ou une image : ![texte alternatif](screens/<fichier>.png)
- En ligne : *emphase*, **gras**, `code`, [texte du lien](adresse). Terminez une ligne par \ pour forcer un retour à la ligne.
- Écrivez des espaces ordinaires avant : ; ? ! et des apostrophes droites : le build pose les espaces insécables et
  les apostrophes typographiques.
- Les commentaires comme celui-ci sont ignorés.
-->

## page

### title
AGNOS - Agentic efficiency by traceability

### description
AGNOS, un processus d'ingénierie léger pour les équipes de développement AI-native.

## notice

### label
Démo

### text
Les vues de cette page viennent de Roombook, le projet de démonstration d'AGNOS, dont l'équipe et les deux mois d'historique sont simulés.

## brand

### name
AGNOS

### tagline
Agentic efficiency by traceability

## nav

### tour
Tour d'horizon

### start
Démarrer

### demo
Démo

### sections
Sections

### language
Langue

### english
EN

### french
FR

## hero

### kicker
Processus d'ingénierie pour l'IA agentique

### title
Les agents IA écrivent le code, ou bien plus.\
*Vous gardez le contrôle.*

### text
AGNOS est un processus léger, outillé, pour les équipes de développement *AI-native* (pods de quelques personnes ou solo). Exigences, décisions, tâches, code et commits portent les mêmes identifiants : le travail reste explicable, et le processus se mesure sur chaque projet, en temps réel grâce à l'application intégrée AGNOS Performance Center.

### cta-demo
Ouvrir le Performance Center de démo

### cta-tour
Tour d'horizon

### tools
Fonctionne avec Claude Code, GitHub Copilot (support OpenAI Codex à venir). Ses artefacts sont en Markdown, versionnés dans git, afin de maximiser l'efficacité opérationnelle.

## chain

### title
La boucle agentique, du besoin jusqu'au commit

### mode-mixed
Mixte

### mode-on
Supervision de bout en bout

### in-loop
Human in the loop

### in-loop-text
L'agent rédige ; vous décidez et approuvez chaque étape.

### on-loop
Human on the loop

### on-loop-text
L'agent exécute la tâche approuvée ; vous supervisez, et intervenez si besoin.

### on-loop-draft-text
Invité à travailler en toute autonomie, l'agent rédige et prend les décisions ; vous supervisez, et intervenez si besoin.

### approve-on
Décisions déléguées à l'agent

### requirement
Exigence

### requirement-text
L'expression du besoin, formalisé pour être testable

### decision
Architecture et décision

### decision-text
Pourquoi cette conception, et ce qui a été écarté

### task
Tâche

### task-text
Calibrée selon le risque, approuvée avant de démarrer

### approve
Vous approuvez

### code
Tests, puis code

### code-text
Chaque élément cite ses identifiants

### done
Liste de contrôle validée

### commit
Commit

### commit-text
Un par tâche, ses identifiants vérifiés par un script

### measure-text
Supervision end-to-end du process, sur l'ensemble du projet

### foot
Le travail se fait en sessions : un domaine fonctionnel, une branche, dix tâches au plus, pour une gestion optimale du contexte

### supervision
Supervision

### requirement-id
RQ-BKG-003

### decision-id
DEC-BKG-002

### task-id
TASK-BKG-003

### code-id
OverlapRule.check

### commit-id
12dc6e4

### measure
Performance Center

## tour

### eyebrow
Tour d'horizon

### title
Le Performance Center : votre développement agentique d'un coup d'œil

### text
Les cinq vues du Performance Center répondent au besoin fondamental de monitoring de vos développements.
Chaque exemple de vue ci-dessous est une capture du Performance Center sur Roombook, le projet de démonstration d'AGNOS. Cliquez sur l'une d'elles pour l'ouvrir, en direct, dans la démo.

## labels

### see
Ce que vous voyez

### why
Ce qui le rend possible

## matrix

### view
Vue Matrice

### question
Ce qui a été demandé est-il vraiment construit ?

### see
La matrice de traçabilité de bout en bout, des capacités fonctionnelles au code, sur une page unique, exportable directement.

### why
Chaque élément du process est identifié de manière unique, de la capacité fonctionnelle au commit. La spécification et les tests, exprimés dans des syntaxes testables (*EARS*, *Gherkin*), réduisent au minimum l'interprétation agentique à l'implémentation.

### tags
- EARS
- Gherkin
- Identifiants dans le code

### shot
![Vue Matrice](screens/matrix.png)

### caption
La vue Matrice du Performance Center

## examples

### requirement
![Une exigence](screens/example-requirement.png)

### requirement-caption
Une exigence 

### adr
![Architecture Decision Record, et diagrammes auto-générés](screens/example-adr.png)

### adr-caption
Architecture Decision Record, et diagrammes auto-générés

### plan
![Plan d'exécution et tâche d'implémentation](screens/example-plan.png)

### plan-caption
Plan d'exécution et tâche d'implémentation

### zoom
Exemple agrandi

### close
Fermer

## graph

### view
Vue Graph

### question
Pourquoi ce code existe-t-il, et que toucherait une modification ?

### see
L'arbre de dépendance d'un élément sélectionné: sa fonctionnalité, les décisions qui l'ont façonnée, les tâches qui l'ont livrée, les fichiers et fonctions qui l'implémentent.

### why
La synergie de l'arbre syntaxique d'implémentation (arbre *AST*) et de la grammaire unique d'identification garantissent une vision holistique et explorable des relations entre artefacts.

### tags
- Abstract Syntax Tree
- Grammaire d'identifiants
- Graph explorable

### shot
![La vue Graph du Performance Center](screens/graph.png)

### caption
La vue Graph du Performance Center



## history

### view
Vue History

### question
Qui a modifié quoi, et quand ? Agent, humain, ou les deux ?

### see
Chaque modification d'une exigence, d'une décision, d'un fichier ou d'une fonction, attribuée à ses auteurs depuis git. Chaque identité est classée humaine ou agent IA. Chaque commit, humain, agentique ou collaboratif, est traçable par une vue exigence ou une vue implémentation.

### why
Un commit par tâche, fait par un skill qui écrit les identifiants de tâche et d'ADR dans son message au standard *Conventional Commits*. Git reste l'unique système de référence, indépendant de toute infrastructure.

### tags
- Vue chronologique
- Un commit par tâche
- Humain ou agent

### shot
![La vue Historique du Performance Center](screens/history.png)

### caption
La vue Historique du Performance Center

## delivery

### view
vue Delivery

### question
Qu'est-ce qui a été livré et à quelle vitesse ? La vélocité agentique est-elle maîtrisée ?

### see
Les tâches livrées au fil du temps, pondérées par leur niveau, et la friction de chaque session : questions que l'agent a dû poser, reprises sur erreur, tâches recalibrées, écarts détectés à la vérification.

### why
Le travail se fait en sessions de dix tâches au plus, pour une utilisation optimale du contexte. Chaque session se clôt sur ses compteurs de friction ; si l'un d'eux n'est pas nul, une étape d'auto-amélioration propose des règles pour le projet, appliquées une fois approuvées et sur un budget défini.

### tags
- Sessions
- Compteurs de friction
- Auto-amélioration

### shot
![La vue Delivery du Performance Center](screens/delivery.png)

### caption
La vue Delivery du Performance Center

## quality

### view
Vue Quality

### question
La traçabilité est-elle garantie, par domaine fonctionnel ?

### see
Des KPIs simples à comprendre de A à E, calculés à partir de contrôles pondérés par le risque. Chaque écart désigne l'élément à corriger : sur Roombook, des fonctions qui ne citent pas encore d'exigence.

### why
Des portes que l'agent ne peut pas contourner. Chaque tâche répond à un besoin, ne démarre qu'une fois approuvée (Definition of Ready) et ne se clôt qu'une fois sa liste de contrôle validée (Definition of Done). Son niveau, (S)mall, (M)edium ou (L)arge, proportionne la cérémonie au risque de la modification. Un contrôle en échec a droit à une correction, puis l'agent s'arrête et rend compte.

### tags
- Definition of Ready
- Definition of Done
- Niveaux S, M, L

### shot
![La vue Quality du Performance Center](screens/quality.png)

### caption
La vue Quality du Performance Center 

## more

### eyebrow
Derrière les vues

### title
Trois autres raisons pour lesquelles cela tient à l'échelle

## index-card

### title
Pensé pour les agents : l'index

### text
Un script indexe chaque artefact, une ligne chacun, avec son emplacement exact. L'agent lit d'abord ce petit fichier et n'ouvre que les lignes utiles. Il y prend le prochain identifiant libre : aucun n'est jamais dupliqué. Le Performance Center lit le même index : ce que voit l'agent et ce que vous mesurez ne peuvent pas diverger. L'index est recalculé automatiquement, au début de chaque session et avant chaque commit, par un skill déterministe.

### caption
Roombook : un extrait de l'index.

### excerpt
```
@agnos-process/1.requirements/FTR-BKG-001-room-reservation.md
RQ-BKG-003|42-56||Double booking rejection
@agnos-process/3.plan/PLAN-BKG-001-core-booking.md
TASK-BKG-003|50-66|Done|Implement overlap rule
```

## id-card

### title
Des liens exacts, pas des ressemblances

### text
Chaque exigence, décision, tâche et fonction porte un identifiant unique, et chaque élément cite ceux dont il dépend, comme une clé primaire et ses clés étrangères dans une base de données. L'agent suit donc des liens exacts au lieu de deviner, par proximité sémantique, quel texte se rapporte à quoi. Les mêmes entrées donnent les mêmes liens : le travail de l'agent devient plus déterministe, et vérifiable.

### foreign-key
Clé étrangère

### cites
cite

### primary-key
Clé primaire

### requirement
```
### RQ-BKG-003: Double booking rejection
```

### task
```
### TASK-BKG-003: Implement overlap rule
- Requirement refs: ==RQ-BKG-003==
- ADR refs: ADR-BKG-001 (DEC-BKG-002)
```

### adr
```
# ADR-BKG-002: Initial reservation storage
Motivated by: RQ-BKG-002, ==RQ-BKG-003==, RQ-BKG-005 (FTR-BKG-001); builds on ADR-BKG-001.
### DEC-BKG-003: In-memory dictionary for reservations
```

### semantic
Rapprochement sémantique : un lien probable

### exact
Identifiant : un lien exact

### code
```
@service/roombook/rules/overlap_rule.py
# ==RQ-BKG-003==, DEC-BKG-002 (ADR-BKG-001)
class OverlapRule:
    """Rejects an interval that overlaps an existing reservation (==RQ-BKG-003==)."""

    def check(self, room: Room, request: ReservationRequest, existing: Sequence[Reservation]) -> None:
        """Raise ReservationConflict naming the first overlapping reservation (==RQ-BKG-003==)."""
```

### graph
TASK-BKG-003, ADR-BKG-002 et overlap_rule.py citent tous RQ-BKG-003

### task-id
TASK-BKG-003

### requirement-id
RQ-BKG-003

### adr-id
ADR-BKG-002

### requirement-title
Double booking rejection

### task-title
Implement overlap rule

### adr-title
Initial reservation storage

### file-id
overlap_rule.py

### file-title
OverlapRule


## design-card

### title
Des IHMs sous le même contrôle

### text
Un projet avec IHM définit son design system depuis le template AGNOS, avant son premier écran, sous forme d'exigence et de décision d'architecture.
Le design system est une spécification comme une autre, projetée sous forme de design tokens et implémentés dans le code.

### primary-name
Principal

### primary-tokens
```
button.primary.background
→ colour.accent.default
→ colour.blue.600 = ==#2563eb==
```

### primary-css
```
.button-primary {
  background: var(--button-primary-background);
  color: var(--button-primary-text);
}
```

### primary-button
Réserver cette salle

### danger-name
Danger

### danger-tokens
```
button.danger.background
→ colour.error.strong
→ colour.red.700 = ==#b91c1c==
```

### danger-css
```
.button-danger {
  background: var(--button-danger-background);
  color: var(--button-danger-text);
}
```

### danger-button
Annuler cette réservation

### caption
Boutons du projet Roombook, exploitant les design token spécifiés.

## close

### title
Voyez-le sur un vrai projet

### text
La page de démo contient toutes les vues, tous les liens et tous les commits des deux mois simulés de Roombook.

### address
Généré par agnos-perf-center sur Roombook, et publié avec ce site.

### cta
Ouvrir le Performance Center de démo

## start

### title
Trois étapes jusqu'à la première session

### step1-title
Installer le plugin

### step1-text
Une seule marketplace pour Claude Code et GitHub Copilot (support OpenAI Codex à venir).

### step1-command
```
claude plugin marketplace add <marketplace>
claude plugin install agnos@agnos-marketplace
```

### step2-title
Ajouter AGNOS à un projet

### step2-text
Un appel à `agnos-init`. Vos propres fichiers restent intacts.

### step2-command
```
Appelez le skill agnos-init.
```

### step3-title
Démarrer une session

### step3-text
Dans une nouvelle conversation, l'agent enregistre la session et ouvre sa branche.

### step3-command
```
Démarrez une nouvelle session AGNOS, trigramme <TRI>.
```

## footer

### developers
[Pour vos développeurs : la documentation sur GitHub](https://github.com/spashx/agnos-lightweight-process)

### license
AGNOS est distribué sous licence GNU Affero General Public License v3.

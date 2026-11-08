<!--
FTR-WEB-001 : RQ-WEB-003 à RQ-WEB-012 / ADR-WEB-001 : DEC-WEB-003. Site AGNOS, texte français.
Modifiez librement les mots ; gardez la structure, puis relancez le build du skill agnos-meta-website.
- "## <section>" ouvre un élément de la page, "### <champ>" l'un de ses textes. Gardez ces identifiants identiques dans
  en.md et fr.md : le build refuse un champ absent d'une langue, ou inconnu du gabarit de la page.
- Un champ est un paragraphe, une liste d'éléments "- ", un extrait d'index entre deux lignes ``` (les lignes
  commençant par @ sont atténuées), ou une image cliquable : [![texte alternatif](screens/<fichier>.png)](<adresse>)
- En ligne : *emphase*, **gras**, `code`, [texte du lien](adresse). Terminez une ligne par \ pour forcer un retour à la ligne.
- Écrivez des espaces ordinaires avant : ; ? ! et des apostrophes droites : le build pose les espaces insécables et
  les apostrophes typographiques.
- {{index.documents}}, {{index.size}} et {{index.ratio}} sont mesurés sur la démo par le build.
- Les commentaires comme celui-ci sont ignorés.
-->

## page

### title
AGNOS · Agentic efficiency by traceability

### description
AGNOS, un processus d'ingénierie léger pour les équipes qui développent avec des agents IA.

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
La visite

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
Les agents IA écrivent le code.\
*Vous gardez le contrôle.*

### text
AGNOS est un processus léger, outillé, pour les équipes qui développent avec des agents IA. Exigences, décisions, tâches, code et commits portent les mêmes identifiants : le travail reste explicable, et le processus se mesure sur chaque projet.

### cta-demo
Ouvrir le Performance Center de démo

### cta-tour
Suivre la visite

### tools
Fonctionne avec Claude Code, GitHub Copilot et OpenAI Codex. Ses artefacts sont en Markdown, versionnés dans git.

## chain

### title
Une exigence, suivie du besoin jusqu'au commit

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
Ce qui doit être vrai, écrit pour être testé

### decision
Décision

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
Mesure toute la chaîne, sur chaque projet

### foot
Le travail se fait en sessions : un domaine fonctionnel, une branche, dix tâches au plus.

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
3aec803

### measure
Performance Center

### measure-id
Roombook

## tour

### eyebrow
La visite

### title
Cinq vues du Performance Center, cinq questions que se pose une DSI

### text
Chaque vue est une capture de la page générée par AGNOS sur Roombook, son projet de démonstration. Cliquez sur l'une d'elles pour l'ouvrir, en direct, dans la démo.

## labels

### see
Ce que vous voyez

### why
Ce qui le rend possible

### open
Ouvrir dans la démo

## stop-overview

### view
Overview

### question
Ce qui a été demandé est-il vraiment construit ?

### see
Pour chaque domaine fonctionnel, les exigences que le code cite directement, seulement via une tâche ou une décision, ou pas du tout, avec la note de l'ensemble du projet.

### why
Les exigences sont écrites comme des phrases testables (EARS), avec des critères d'acceptation (Gherkin). Chaque fichier source nomme, en commentaire, les exigences qu'il implémente.

### tags
- EARS
- Gherkin
- Identifiants dans le code

### shot
[![La vue Overview du Performance Center sur Roombook](screens/overview.png)](demo/PERF-CENTER.html)

### caption
Roombook : chaque exigence est citée par le code qui l'implémente.

## examples

### requirement
![Une exigence de Roombook, en EARS avec ses critères Gherkin](screens/example-requirement.png)

### requirement-caption
L'exigence RQ-BKG-003

### adr
![Une décision d'architecture de Roombook, avec son diagramme](screens/example-adr.png)

### adr-caption
ADR-BKG-001 et son diagramme

### plan
![Un plan de Roombook, avec l'une de ses tâches](screens/example-plan.png)

### plan-caption
PLAN-BKG-001 et TASK-BKG-003

### zoom
Exemple agrandi

### close
Fermer

## stop-graph

### view
Graph

### question
Pourquoi ce code existe-t-il, et que toucherait une modification ?

### see
Une exigence et tout ce qui s'y rattache : sa fonctionnalité, les décisions qui l'ont façonnée, les tâches qui l'ont livrée, les fichiers et fonctions qui l'implémentent.

### why
Une seule grammaire d'identifiants, écrite en commentaire dans les documents, le code, les tests et les messages de commit. Chaque décision d'architecture a son propre identifiant : le code cite la décision exacte qu'il applique.

### tags
- Décisions d'architecture (ADR)
- Une grammaire d'identifiants
- Identifiants en commentaire

### shot
[![La vue Graph du Performance Center, centrée sur l'exigence RQ-BKG-003](screens/graph.png)](demo/PERF-CENTER.html#RQ-BKG-003)

### caption
`RQ-BKG-003`, No double booking, et tout ce qui la cite.

## stop-quality

### view
Quality

### question
Peut-on se fier à la façon dont le processus a été appliqué ?

### see
Une note de A à E, calculée à partir de contrôles pondérés par le risque. Chaque écart désigne l'élément à corriger : sur Roombook, des fonctions qui ne citent pas encore d'exigence.

### why
Des portes que l'agent ne peut pas contourner. Une tâche ne démarre qu'une fois approuvée (Definition of Ready) et ne se clôt qu'une fois sa liste de contrôle validée (Definition of Done). Son niveau, S, M ou L, proportionne le formalisme au risque de la modification. Un contrôle en échec a droit à une correction, puis l'agent s'arrête et rend compte.

### tags
- Definition of Ready
- Definition of Done
- Niveaux S, M, L

### shot
[![La vue Quality du Performance Center sur Roombook](screens/quality.png)](demo/PERF-CENTER.html)

### caption
Le bulletin de Roombook, et les contrôles derrière sa note.

## stop-history

### view
History

### question
Qui a modifié quoi, et quand ?

### see
Chaque modification d'une exigence, d'une décision, d'un fichier ou d'une fonction, attribuée à ses auteurs depuis git. Chaque identité est classée humaine ou agent IA, et chaque commit humain, agent ou les deux ensemble.

### why
Un commit par tâche, fait par un skill qui écrit les identifiants de tâche et d'ADR dans son message. Git reste l'unique système de référence.

### tags
- Un commit par tâche
- Humain ou agent

### shot
[![La vue History du Performance Center sur Roombook](screens/history.png)](demo/PERF-CENTER.html)

### caption
Deux mois d'historique de Roombook.

### note
L'équipe simulée de Roombook n'est pour l'instant qu'humaine : des identités d'agent IA seront ajoutées à la démo.

## stop-delivery

### view
Delivery

### question
Qu'est-ce qui a été livré, et le processus s'améliore-t-il ?

### see
Les tâches livrées au fil du temps, pondérées par leur niveau, et la friction de chaque session : questions que l'agent a dû poser, reprises sur erreur, tâches recalibrées, écarts détectés à la vérification.

### why
Le travail se fait en sessions de dix tâches au plus, pour que le contexte de l'agent reste net. Chaque session se clôt sur ses compteurs de friction ; si l'un d'eux n'est pas nul, une étape d'auto-amélioration propose des règles pour le projet, appliquées une fois approuvées et dans un budget de lignes.

### tags
- Sessions
- Compteurs de friction
- Auto-amélioration

### shot
[![La vue Delivery du Performance Center sur Roombook](screens/delivery.png)](demo/PERF-CENTER.html)

### caption
Ce que Roombook a livré, période par période.

## more

### eyebrow
Derrière les vues

### title
Trois autres raisons pour lesquelles cela tient à l'échelle

## index-card

### title
Pensé pour les agents : l'index

### text
Un script indexe chaque artefact, une ligne chacun, avec son emplacement exact. L'agent lit d'abord ce petit fichier et n'ouvre que les lignes utiles. Il y prend le prochain identifiant libre : aucun n'est jamais dupliqué. Le Performance Center lit le même index : ce que voit l'agent et ce que vous mesurez ne peuvent pas diverger.

### documents
Documents du processus, {{index.documents}}

### index
L'index, {{index.size}}

### caption
Roombook : l'index fait environ {{index.ratio}} des documents qu'il décrit.

### excerpt
```
@agnos-process/1.requirements/FTR-BKG-001-room-reservation.md
RQ-BKG-003|42-56||No double booking
@agnos-process/3.plan/PLAN-BKG-001-core-booking.md
TASK-BKG-003|50-66|Done|Overlap rule
```

## id-card

### title
Des liens exacts, pas des ressemblances

### text
Chaque exigence, décision, tâche et fonction porte un identifiant unique, et chaque élément cite ceux dont il dépend, comme une clé primaire et ses clés étrangères dans une base de données. L'agent suit donc des liens exacts au lieu de deviner, par proximité sémantique, quel texte se rapporte à quoi. Les mêmes entrées donnent les mêmes liens : le travail de l'agent devient plus déterministe, et vérifiable.

### foreign-key
Clé étrangère

### task-id
TASK-BKG-003

### cites
cite →

### primary-key
Clé primaire

### requirement-id
RQ-BKG-003

### semantic
Rapprochement sémantique : un lien probable

### exact
Identifiant : un lien exact

### caption
Roombook : `OverlapRule.check` cite RQ-BKG-003 ; `grep RQ-BKG-003` retrouve tout ce qui en dépend.

## design-card

### title
Des interfaces sous le même contrôle

### text
Un projet avec interface définit son design system avant son premier écran, sous forme d'exigence et de décision d'architecture. Les écrans le citent, et le code lit chaque couleur et chaque taille dans un jeton. Sur Roombook, un test rejette toute valeur brute.

### component
Composant

### semantic
Sémantique

### global
Global, seule valeur brute

### caption
Le fond d'un bouton, dans les jetons de Roombook : `FTR-DSN-001` et `ADR-DSN-001`.

### component-token
button.primary.background

### semantic-token
colour.accent.default

### global-token
colour.blue.600

### global-value
#2563eb

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
Une seule marketplace pour Claude Code, GitHub Copilot et OpenAI Codex.

### step2-title
Ajouter AGNOS à un projet

### step2-text
Un appel à `agnos-init`. Vos propres fichiers restent intacts.

### step3-title
Démarrer une session

### step3-text
Dans une nouvelle conversation, l'agent enregistre la session et ouvre sa branche.

## footer

### developers
[Pour vos développeurs : la documentation sur GitHub](https://github.com/spashx/agnos-lightweight-process)

### license
AGNOS est distribué sous licence GNU Affero General Public License v3.

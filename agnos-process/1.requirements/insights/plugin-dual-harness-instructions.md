# Instructions IA : structurer et valider un plugin pour Claude Code ET GitHub Copilot CLI

> Fichier d'entrée pour un agent IA. Rédigé le 2026-10-31. Les formats évoluent vite : revérifie les sources de la section 9 avant de figer une structure.

## 0. Règles de conduite (prioritaires)

1. Ne rien inventer. Chaque règle de format que tu appliques doit être marquée dans ton rapport : `[OFFICIEL]` (doc éditeur lue), `[TIERS]` (dépôt ou article communautaire) ou `[À VÉRIFIER]` (hypothèse). Si tu ne sais pas, dis-le.
2. Avant de produire des fichiers, pose au plus 5 questions de clarification (section 1). Si l'utilisateur est absent, prends l'hypothèse la plus raisonnable, annonce-la en tête du rapport et continue.
3. Sois concis dans tes réponses. Livre des fichiers, pas des commentaires.
4. Ne marque jamais une validation comme réussie sans avoir exécuté la commande. Si un CLI n'est pas installé, écris « non exécuté » et donne la commande à lancer.
5. Pas de secrets, tokens ni chemins absolus de la machine dans les fichiers du plugin.

## 1. Entrées à obtenir de l'utilisateur

- Nom du plugin (kebab-case, 64 caractères max, lettres minuscules, chiffres, tirets) et description en une phrase.
- Composants voulus : skills (par défaut), agents, hooks, serveurs MCP, commandes.
- Dépôt cible (owner/repo), licence, auteur.
- Langages ou OS à supporter pour les scripts (bash seul, ou aussi PowerShell).
- Le plugin doit-il rester uniquement skills + MCP (portable maximal) ?
- Le dépôt utilise-t-il déjà `AGENTS.md` ou `.agents/` ? Veut-on le Mode C (source canonique `.agents/`) ? L'équipe est-elle sous Windows (symlinks Git) ? Quelle version de Claude Code est utilisée ?

## 2. Décision d'architecture

**Mode A (par défaut) : un seul manifeste lu par les deux harness.**
- Copilot CLI accepte un manifeste legacy dans `.claude-plugin/plugin.json` `[OFFICIEL]`. Claude Code le lit nativement `[OFFICIEL]`.
- Ordre de recherche du manifeste plugin par Copilot (legacy) : `.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, `.claude-plugin/plugin.json` `[OFFICIEL]`.
- Ordre de recherche du manifeste marketplace par Copilot : `marketplace.json`, `.plugin/marketplace.json`, `.github/plugin/marketplace.json`, `.claude-plugin/marketplace.json` `[OFFICIEL]`.
- Conséquence : si tu ne crées pas de manifeste en amont dans cet ordre, les deux harness lisent le même fichier `.claude-plugin/…`. Pour diverger plus tard, ajoute `.github/plugin/plugin.json` (Copilot le lit avant `.claude-plugin/`).
- Ne mets PAS de `$schema` Agent Plugins dans ce manifeste : sans lui, Copilot charge en mode legacy `[OFFICIEL]`.

**Mode B (optionnel, plugin limité à skills + MCP).** Format ouvert « Agent Plugins 1.0 » : `plugin.json` à la racine avec `$schema` = `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` ; skills dans `skills/` ; MCP dans `mcp.json` racine (avec son propre `$schema`) ; composants propres à Copilot dans `com.github.copilot/` `[OFFICIEL]`. Ce mode a un schéma de manifeste fermé : pas de champs `agents`, `skills`, `hooks`, `mcpServers` dans le manifeste. Pour Claude Code, ajoute en plus `.claude-plugin/plugin.json` et `.mcp.json` `[TIERS : exemple prerenderbuddy-plugins]`. À utiliser seulement si l'utilisateur le demande.

**Mode C (option, combinable avec A) : `.agents/` comme source canonique.** Une seule copie des skills et des instructions, dans `.agents/` et `AGENTS.md`, réutilisée par Claude Code et Copilot. Deux niveaux distincts : usage dans le dépôt (C-1) et distribution via marketplace (C-2).

*C-1, niveau dépôt (usage dans le dépôt lui-même)*
- Skills : `.agents/skills/<skill>/SKILL.md` est la source unique. Copilot lit `.agents/skills` (projet) et `~/.agents/skills` (personnel) `[OFFICIEL : CLI plugin reference, ordre de précédence]`. Claude Code ne lit que `.claude/skills` `[TIERS : ssw.com.au, guide Adobe ; demande « .agents/skills » toujours ouverte, issue anthropics/claude-code #31005]`.
- Redirection Claude Code : un symlink relatif **par skill** : `ln -s ../../.agents/skills/<skill> .claude/skills/<skill>`, puis `git add .claude/skills` `[TIERS : guide Adobe]`. Alternative documentée par SSW : `ln -s ../.agents/skills .claude/skills` (dossier entier). Déconseillée par défaut : l'issue #31005 rapporte que Claude Code y ajoute des fichiers `.system/` (issue #20820), ce qui polluerait `.agents/skills` `[TIERS, non confirmé : lu via un résumé]`. Ne symlinke jamais tout `.claude/` (réglages propres à Claude Code) `[TIERS]`.
- Pas de doublon côté Copilot : les skills sont dédupliqués par `name`, premier trouvé gagne (`.github/skills`, puis `.agents/skills`, puis `.claude/skills`) `[OFFICIEL]`.
- Instructions : `AGENTS.md` à la racine est la source unique. Copilot le lit `[TIERS : SSW]`. Claude Code ne le lit qu'en repli si `CLAUDE.md` est absent (note de version v2.1.277 du 2026-09-18, citée dans l'issue #31005) `[TIERS : à confirmer dans le changelog officiel]`. Donc crée un `CLAUDE.md` qui contient `@AGENTS.md` (import) suivi d'éventuelles consignes propres à Claude `[TIERS : SSW, Adobe, travis.media]`. Un `CLAUDE.md` qui dit seulement « lis AGENTS.md » ne fonctionne pas `[TIERS : SSW]`. Préfère l'import au symlink `CLAUDE.md → AGENTS.md` si l'équipe est sous Windows.
- Windows : sans `git config core.symlinks true` (et mode développeur), Git enregistre le symlink comme fichier texte `[TIERS]`. Repli : `.claude/commands/<skill>.md` contenant `@.agents/skills/<skill>/SKILL.md` (invocation manuelle seulement) `[TIERS : Adobe]`.

*C-2, niveau distribution (plugin installé depuis un marketplace)* : le dossier `.agents/` et les symlinks ne suivent pas forcément à l'installation. Variantes, par ordre de préférence :
1. **Copie générée (recommandée).** Un script `tools/sync-skills` copie `.agents/skills/*` vers `plugins/<plugin-name>/skills/` (copies réelles, pas de symlinks), lancé en pre-commit et en CI ; la CI échoue en cas de dérive. Raison : deux issues Claude Code, dont seuls les titres ont pu être lus, signalent que l'installeur ne résout pas les symlinks lors de la copie vers le cache et qu'une régression (v2.1.117) ne copiait plus les skills symlinkés `[TIERS : titres d'issues #57339 et #53948, pages inaccessibles]`.
2. **Racine du plugin = racine du dépôt.** Marketplace `source: "./"` ; les manifestes déclarent `"skills": "./.agents/skills"` (champ de chemin supporté par Copilot legacy `[OFFICIEL]` ; côté Claude Code `[À VÉRIFIER]`) ; pas de `skills/` dupliqué `[TIERS : wiki i-9-ai/skills]`. Conflit avec C-1 : si le dépôt contient `.claude/skills` (symlinks de dev), la racine du plugin contiendra un dossier `.claude/`, or une issue Claude Code (#44120, v2.1.92, statut inconnu) rapporte que `skills/` est alors ignoré `[TIERS]`. À n'utiliser que si le test de la section 7 passe.
3. **Symlinks dans `plugins/<plugin-name>/skills/`** vers `.agents/skills/`. Déconseillé (issues ci-dessus) sauf test d'installation concluant depuis un clone propre.

Interdit en distribution : un dossier `.claude/` dans la racine d'un plugin distribué `[TIERS : #44120]`.

## 3. Arborescence cible (Mode A)

```
<repo>/
├── .claude-plugin/marketplace.json        # catalogue, lu par Claude Code ET Copilot
├── plugins/<plugin-name>/
│   ├── .claude-plugin/plugin.json         # manifeste commun
│   ├── skills/<skill-name>/SKILL.md       # portable (format Agent Skills)
│   │   ├── scripts/  references/          # optionnels
│   ├── agents/<agent-name>.agent.md       # optionnel (voir §5)
│   ├── hooks/hooks.json                   # optionnel, format à valider par harness (voir §5)
│   ├── .mcp.json                          # optionnel
│   └── scripts/                           # scripts partagés
├── tools/validate-plugin.(py|sh)          # script de validation statique (voir §6)
└── README.md                              # install et validation pour les deux harness
```

Règle `[OFFICIEL]` (Claude Code) : tous les dossiers de composants sont à la racine du plugin, jamais dans `.claude-plugin/`. Seul le manifeste va dans `.claude-plugin/`.

**Variante Mode C, C-2 variante 1 (copie générée) :**
```
<repo>/
├── AGENTS.md                              # source unique des instructions
├── CLAUDE.md                              # "@AGENTS.md" + consignes propres à Claude (optionnel)
├── .agents/skills/<skill>/SKILL.md        # source unique des skills
├── .claude/skills/<skill> -> ../../.agents/skills/<skill>   # symlinks relatifs, usage dans le dépôt
├── .claude-plugin/marketplace.json
├── plugins/<plugin-name>/
│   ├── .claude-plugin/plugin.json
│   └── skills/<skill>/SKILL.md            # COPIE générée par tools/sync-skills (ne pas éditer)
└── tools/{sync-skills,validate-plugin}.*
```
Le dossier `plugins/<plugin-name>/` ne doit contenir aucun `.claude/`.

## 4. Fichiers types

`plugins/<plugin-name>/.claude-plugin/plugin.json` (champs communs aux deux harness) :
```json
{
  "name": "<plugin-name>",
  "version": "0.1.0",
  "description": "<une phrase, 1024 caractères max>",
  "author": { "name": "<nom>" },
  "license": "MIT",
  "keywords": ["<mot-clé>"]
}
```
- Claude Code : `name` est le seul champ obligatoire, kebab-case `[OFFICIEL]`.
- Copilot legacy : `name` obligatoire, kebab-case, 64 caractères max ; `author.name` obligatoire si `author` est présent ; `description` 1024 caractères max `[OFFICIEL]`.

`.claude-plugin/marketplace.json` (racine du dépôt) :
```json
{
  "name": "<marketplace-name>",
  "owner": { "name": "<organisation ou auteur>" },
  "metadata": { "description": "<description>", "version": "0.1.0" },
  "plugins": [
    { "name": "<plugin-name>", "description": "<description>", "version": "0.1.0",
      "source": "./plugins/<plugin-name>" }
  ]
}
```
- Champs obligatoires : `name`, `owner`, `plugins` ; par entrée : `name` et `source` `[OFFICIEL, les deux harness]`.
- Le `name` de l'entrée doit être identique au `name` du manifeste, sinon l'installation par nom du manifeste échoue côté Claude Code `[OFFICIEL]`.
- `source` : chemin relatif sans `..` (rejeté par `claude plugin validate`) `[OFFICIEL]`. Un chemin inexistant passe la validation mais échoue à l'installation `[OFFICIEL]` : vérifie toi-même l'existence.
- N'utilise pas un nom de marketplace réservé par Claude Code (par ex. `claude-code-plugins`, `claude-plugins-official`, `anthropic-*`, `agent-skills`, …) `[OFFICIEL]`.

## 5. Règles par composant

**Skills (cœur portable).** Dossier `skills/<skill-name>/SKILL.md` avec frontmatter YAML `name` et `description`. Le `name` doit correspondre au dossier. Copilot déduplique les skills par `name` : premier trouvé gagne, et un skill projet ou personnel de même nom masque celui du plugin `[OFFICIEL]`. Choisis donc des noms uniques. Contraintes détaillées du frontmatter (longueurs, caractères) : `[À VÉRIFIER]` dans la spécification Agent Skills. Mets la logique dans des scripts appelés par le skill, avec chemins `${CLAUDE_PLUGIN_ROOT}/scripts/...` (alias reconnu par Copilot, qui expose aussi `${PLUGIN_ROOT}` et `${COPILOT_PLUGIN_ROOT}`) `[OFFICIEL]`.

**Agents.** Copilot : `agents/*.agent.md`, dédupliqués par nom de fichier `[OFFICIEL]`. Claude Code : `agents/*.md` avec frontmatter `name`, `description`, `model`, `tools`… `[OFFICIEL, page docs.claude.com]`. Hypothèse à tester : un fichier `x.agent.md` est chargé correctement par les deux `[À VÉRIFIER]`. Si le test échoue, sépare via les champs de chemin des manifestes (`agents`) et deux manifestes distincts.

**Hooks.** Chemin par défaut identique : `hooks/hooks.json` (ou `hooks.json` côté Copilot legacy) `[OFFICIEL]`. Les schémas internes (noms d'événements, champs) ne sont pas confirmés identiques `[À VÉRIFIER]` : lis la page « Hooks reference » de Copilot et la doc hooks de Claude Code. En cas de divergence, deux manifestes avec champ `hooks` pointant vers deux fichiers différents. Par défaut, n'inclus pas de hooks en v0.1 sauf demande explicite.

**MCP.** `.mcp.json` à la racine du plugin, lu par Claude Code `[OFFICIEL]` et par Copilot legacy `[OFFICIEL]`. Compatibilité du contenu : `[À VÉRIFIER]`. Pour les serveurs `stdio`, utilise `${CLAUDE_PLUGIN_ROOT}` pour les chemins.

**Commandes.** Concept présent des deux côtés (`commands/` Claude Code ; champ `commands` ou `com.github.copilot/commands/` Copilot) `[OFFICIEL]`. Équivalence de format : `[À VÉRIFIER]`. Préfère un skill.

## 6. Script de validation statique à produire (`tools/validate-plugin`)

Le script doit échouer (code ≠ 0) sur chacune de ces conditions :
1. JSON invalide dans `plugin.json`, `marketplace.json`, `.mcp.json`, `hooks.json`.
2. `name` non kebab-case ou > 64 caractères (manifeste et entrées marketplace).
3. `name` du manifeste ≠ `name` de l'entrée marketplace.
4. `source` absolu, contenant `..`, ou pointant vers un dossier inexistant.
5. Un skill sans `SKILL.md`, sans `name` ou sans `description` dans le frontmatter, ou dont le `name` ≠ nom du dossier ; noms de skills dupliqués dans le dépôt.
6. Dossiers de composants présents dans `.claude-plugin/` (interdit).
7. Présence d'un `$schema` Agent Plugins dans un manifeste en Mode A (interdit).
8. Motifs de secrets évidents (clés API, tokens) dans tout fichier.
9. Chemins absolus de machine (`/home/`, `C:\`) dans les fichiers du plugin.

Contrôles supplémentaires si le Mode C est activé :

10. Chaque `.claude/skills/<skill>` est un symlink relatif, non cassé, qui pointe vers `.agents/skills/<skill>`.
11. (C-2 variante 1) `plugins/<plugin-name>/skills/` est identique octet pour octet à `.agents/skills/` ; sinon échec et message « lancer tools/sync-skills ».
12. Aucun dossier `.claude/` dans la racine d'un plugin distribué.
13. `CLAUDE.md`, s'il existe, contient `@AGENTS.md` ; il n'est pas un symlink si l'équipe utilise Windows.
14. Noms de skills uniques à travers `.agents/skills`, `.github/skills` et `.claude/skills`.

## 7. Procédure de validation par environnement

**Claude Code** (CLI `claude`) :
1. `claude plugin validate ./plugins/<plugin-name>` puis `claude plugin validate .` pour le marketplace. Attendu : « Validation passed » `[OFFICIEL]`.
2. Chargement local sans installation : `claude --plugin-dir ./plugins/<plugin-name>` `[OFFICIEL]`.
3. Installation depuis le catalogue : `/plugin marketplace add ./` puis `/plugin install <plugin-name>@<marketplace-name>` ; `claude plugin list` `[OFFICIEL]`.
4. Invoque chaque skill et vérifie qu'il est découvert.

**GitHub Copilot CLI** (CLI `copilot`) :
1. Aucune commande `validate` n'apparaît dans la référence consultée `[OFFICIEL, absence constatée]`. Vérifie avec `copilot plugin --help`.
2. `copilot plugin marketplace add ./` puis `copilot plugin marketplace browse <marketplace-name>` : le plugin doit apparaître `[OFFICIEL]`.
3. `copilot plugin install <plugin-name>@<marketplace-name>` (ou `copilot plugin install ./plugins/<plugin-name>`) ; `copilot plugin list --json` doit montrer `enabled: true` `[OFFICIEL]`.
4. Les plugins d'un marketplace local chargent en direct depuis leur dossier ; redémarre la session après modification (`/restart`) `[OFFICIEL]`.
5. Invoque chaque skill et agent dans une session.

**Tests croisés obligatoires** (cases du rapport) : mêmes skills visibles dans les deux ; aucun avertissement de schéma ; collisions de noms absentes ; installation depuis un clone propre du dépôt (pas depuis ton répertoire de travail).

**Tests supplémentaires du Mode C :**
- Clone propre, sans plugin installé : Claude Code découvre les skills via `.claude/skills` ; Copilot CLI les découvre via `.agents/skills` ; aucun doublon signalé.
- Installation via marketplace depuis un clone propre : les skills sont bien présents dans le plugin installé (invoque chacun). Si l'installation passe par des symlinks, ce test décide de la variante C-2 retenue.
- Si l'équipe utilise Windows : checkout sans `core.symlinks` et vérification du repli (shim `commands/` ou copie générée).
- Vérifie la version de Claude Code utilisée (`claude --version`) : la lecture de `AGENTS.md` en repli dépend de la version.

## 8. Rapport final attendu

Un tableau : composant | Claude Code (validé / non exécuté / échec) | Copilot CLI (idem) | niveau de preuve (`OFFICIEL`/`TIERS`/`À VÉRIFIER`). Puis la liste des hypothèses `[À VÉRIFIER]` restantes et les commandes exactes à lancer pour les lever.

## 9. Sources et niveau de confiance

Officielles (lues le 2026-10-31) :
- GitHub Docs, About Copilot plugins : https://docs.github.com/en/copilot/concepts/agents/about-plugins
- GitHub Docs, CLI plugin reference (manifestes, emplacements, commandes, précédence) : https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference
- Claude Code docs, création de marketplace et validation : https://code.claude.com/docs/en/plugins/create-marketplace.md
- Claude Code docs, création de plugin : https://code.claude.com/docs/en/plugins/create.md
- Claude Code docs, référence du manifeste (extraits de recherche uniquement, page non lue en entier) : https://code.claude.com/docs/en/plugins/manifest-reference.md
- Claude Code docs, référence des plugins (ancien domaine) : https://docs.claude.com/en/docs/claude-code/plugins-reference

Tierces (indicatives, à ne pas traiter comme normatives) :
- Convention `.agents` : SSW https://www.ssw.com.au/rules/symlink-agents-to-claude ; guide Adobe https://opensource.adobe.com/ai-repo-harness-guide/skills/harness-setup/references/claude/ ; import `@AGENTS.md` https://travis.media/blog/claude-md-import-agents-md
- Demande de support `.agents/skills` et `AGENTS.md` dans Claude Code (lue via résumé) : https://github.com/anthropics/claude-code/issues/31005
- Plugin et dossier `.claude/` : https://github.com/anthropics/claude-code/issues/44120
- Symlinks et cache d'installation (titres seulement, pages bloquées) : https://claudeissues.com/issue/57339-plugin-installer-does-not-resolve-symlinks-when-copying-to-cache-breaking-plugin , https://claudeissues.com/issue/53948-bug-plugin-install-no-longer-copies-symlinked-skills-to-cache-regression-in-v2-1
- Plugin multi-harness pointant vers `.agents/skills` : https://github.com/i-9-ai/skills/wiki/Plugin-Preparation
- Dépôts exemples double cible : https://github.com/m1stegmann/coding-agent-skills , https://github.com/sergepetit/sp-skills , https://github.com/irarainey/agent-plugins , https://github.com/kopachlager/prerenderbuddy-plugins
- Miroirs du skill « plugin-structure » d'Anthropic (hooks, `${CLAUDE_PLUGIN_ROOT}`) : https://openskillindex.com/skills/anthropics-claude-code-plugin-structure

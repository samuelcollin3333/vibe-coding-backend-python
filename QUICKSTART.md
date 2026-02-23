# Quickstart

## Setup (5 min)

```bash
# Installer les hooks git (bloque si tests rouges, lint KO ou types KO)
./scripts/install-hooks.sh

# Recherche sémantique (optionnel mais recommandé)
curl -sSL https://raw.githubusercontent.com/yoanbernabeu/grepai/main/install.sh | sh
grepai init
grepai watch  # Lance l'indexation continue en arrière-plan

# Lancer Claude
claude
```

## grepai

`grepai` indexe le code en continu et permet à Claude de faire de la recherche sémantique (par intention) plutôt que par texte exact. Ça économise des tokens et donne de meilleurs résultats.

- `grepai init` : crée l'index initial du projet
- `grepai watch` : surveille les changements et met à jour l'index en continu (à lancer dans un terminal dédié ou en background avec `grepai watch &`)

## Philosophie

> **L'intention humaine est le contrat. Les tests le prouvent.**

4 commandes spécialisées, chacune avec son propre contexte isolé.

## Les 4 commandes

| Commande | Rôle |
|----------|------|
| `/clarify` | Clarifie le besoin → spec |
| `/specify` | Génère les tests (doivent échouer) |
| `/implement` | Écrit le code (tests passent) |
| `/refactor` | Améliore le code (tests restent verts) |

## Utilisation

**Option 1 : Laisser Claude choisir**

```
> Je veux permettre l'annulation de commande

Claude: [utilise automatiquement clarifier]
        C'est quoi le comportement attendu ?
```

**Option 2 : Demander explicitement**

```
> /clarify annulation de commande
> /specify
> /implement
```

## Exemple complet

```
> /clarify annulation de commande

Claude: C'est quoi le comportement attendu ?

> Le client peut annuler si < 24h et pas expédiée

Claude: Et si les conditions sont pas remplies ?

> Erreur avec le motif

Claude: OK, je résume :
- Client annule sa commande
- OK si < 24h ET non expédiée
- Sinon erreur "Too late" ou "Already shipped"
Correct ?

> Oui

Claude: Spec écrite. /clear puis /specify

> /specify

Claude: Tests générés. Ils échouent. /clear puis /implement

> /implement

Claude: Code écrit. Tests passent.

> git commit -m "[domain/order] add cancellation rule"

✅ Commit OK (pre-commit vérifie tests + lint + types)
```

## Infra et autres tâches

Pour tout ce qui n'est pas du code métier (Docker, CI, config...), parle directement :

```
> Dockerise le projet
```

Pas besoin de commandes spécialisées pour ça.

## Protection automatique

- **Hook pre-commit** : Bloque si tests rouges, lint KO ou types KO
- **Hook Claude** : Bloque si architecture violée (imports interdits, dataclass non frozen)

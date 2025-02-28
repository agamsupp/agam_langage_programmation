# Guide de Démarrage AGAM

## Installation
```bash
# Cloner le dépôt
git clone https://github.com/agam-lang/agam
cd agam

# Installation
./deploy.gma
```

## Structure d'un Programme AGAM
Tout programme AGAM suit cette structure :

```gma
BASE [NOM_OPERATION]

# Déclarations
STRATEGIE Config {
    MUNITION version = "1.0"
}

# Corps du programme
MISSION Programme {
    ORDRE DE BATAILLE {
        RAPPORT "Programme opérationnel"
    }
}

FIN BASE
```

## Types de Données
- MUNITION : Variables numériques
- FORMATION : Tableaux
- STRATEGIE : Structures
- RAPPORT : Chaînes de caractères

## Contrôle de Flux
- MISSION : Fonctions
- SI CIBLE : Conditions
- MANOEUVRE : Boucles
- ORDRE DE BATAILLE : Blocs d'exécution
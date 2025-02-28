# Extension AGAM pour Visual Studio Code

Cette extension ajoute le support du langage de programmation AGAM à Visual Studio Code.

## Fonctionnalités

- Coloration syntaxique pour le langage AGAM
- Snippets pour accélérer le développement
- Pliage de code pour les structures du langage
- Auto-complétion des structures de contrôle

## Installation

1. Téléchargez le fichier .vsix
2. Dans VS Code, allez dans l'onglet Extensions
3. Cliquez sur "..." puis "Installer depuis un VSIX..."
4. Sélectionnez le fichier téléchargé

## Utilisation

Créez un fichier avec l'extension .agam pour activer automatiquement la coloration syntaxique.

## Exemples

```agam
BASE "Exemple"
    RAPPORT "Programme de démonstration AGAM"
    
    SURVEILLANCE x "Entrez un nombre: "
    SURVEILLANCE y "Entrez un autre nombre: "
    
    MUNITION resultat
    resultat = ASSAUT x y
    
    RAPPORT "La somme est: " FUSION resultat
FIN BASE
```

## Raccourcis et snippets

- `base` - Crée la structure de base d'un programme
- `manoeuvre` - Crée une boucle principale
- `si` - Crée une structure conditionnelle
- `chain` - Crée une structure de choix multiple
- `surveillance` - Lit une entrée utilisateur
- `rapport` - Affiche un message
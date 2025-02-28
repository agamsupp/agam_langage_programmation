#!/bin/bash
# Générer l'extension AGAM

# Se positionner dans le répertoire de l'extension
cd vscode

# Vérifier si vsce est installé
if ! command -v vsce &> /dev/null; then
    echo "Installation de vsce..."
    npm install -g @vscode/vsce
fi

# Générer le package
vsce package

echo "Extension générée! Vous pouvez l'installer dans VS Code."
# bootstrap_agam.py
import time
import random

class EtatGlobal:
    memoire = [0] * 1024
    pointeur_memoire = 0
    pile = []
    registres = [0, 0, 0, 0]  # R0, R1, R2, R3
    compteur_programme = 0
    messages = []
    programme = []
    commande = ""
    variables = {}

def afficher(texte, couleur):
    couleurs = {"ROUGE": "\033[91m", "VERT": "\033[92m", "ROUGE_ROSE": "\033[95m"}
    print(f"{couleurs.get(couleur, '\033[91m')}{texte}\033[0m")
    EtatGlobal.messages.append(texte)
    if len(EtatGlobal.messages) > 25:
        EtatGlobal.messages.pop(0)

def effacer_ecran():
    print("\033[2J\033[H", end="")

def attendre(ms):
    time.sleep(ms / 1000)

def lire_entree():
    return input("> ")

def initialiser_interpreteur():
    EtatGlobal.messages = []
    EtatGlobal.memoire = [0] * 1024
    EtatGlobal.pointeur_memoire = 0
    EtatGlobal.pile = []
    EtatGlobal.registres = [0, 0, 0, 0]
    EtatGlobal.compteur_programme = 0
    EtatGlobal.variables = {}

def charger_fichier_gma(nom_fichier):
    code_cli = (
        "MISSION Initialisation\n"
        "    EXECUTION GuerreGraph.EffetMatrixTactique 3000\n"
        "    EXECUTION GuerreGraph.AfficherTexteStrategique \"SYSTÈME AGAM v1.0\" ROUGE\n"
        "    RAPPORT \"Initialisation...\"\n"
        "    ATTENDRE 1000\n"
        "    RAPPORT \"Prêt. Tapez 'help'.\"\n"
        "FIN MISSION\n"
        "MISSION BouclePrincipale\n"
        "    MANOEUVRE true\n"
        "        MUNITION commande = LIRE_ENTREE\n"
        "        SELON commande\n"
        "            CAS \"help\"\n"
        "                EXECUTION GuerreGraph.AfficherTexteStrategique \"Commandes : help, deploy, run_vm, monitor, recon, status, halt, reset, config, report\" ROUGE\n"
        "            CAS \"deploy\"\n"
        "                RAPPORT \"Déploiement en cours...\"\n"
        "                ATTENDRE 2000\n"
        "                RAPPORT \"Déploiement terminé.\"\n"
        "            CAS \"run_vm\"\n"
        "                MUNITION x = 5\n"
        "                MUNITION y = 3\n"
        "                MUNITION z = ASSAUT x y\n"
        "                RAPPORT \"Résultat dans R2 : \" FUSION z\n"
        "            CAS \"monitor\"\n"
        "                RAPPORT \"Lancement du moniteur...\"\n"
        "            CAS \"recon\"\n"
        "                RAPPORT \"Reconnaissance en cours...\"\n"
        "            CAS \"status\"\n"
        "                EXECUTION GuerreGraph.AfficherTexteStrategique \"Registres : \" FUSION EtatGlobal.registres ROUGE\n"
        "            CAS \"halt\"\n"
        "                RAPPORT \"Arrêt du système...\"\n"
        "            CAS \"reset\"\n"
        "                RAPPORT \"Réinitialisation...\"\n"
        "            CAS \"config\"\n"
        "                RAPPORT \"Configuration simulée\"\n"
        "            CAS \"report\"\n"
        "                RAPPORT \"Rapport simulé\"\n"
        "            DEFAUT\n"
        "                RAPPORT \"Commande inconnue.\"\n"
        "        FIN SELON\n"
        "    FIN MANOEUVRE\n"
        "FIN MISSION"
    )
    EtatGlobal.programme = code_cli.split("\n")

def executer_ligne(ligne):
    tokens = ligne.split()
    if not tokens:
        return
    cmd = tokens[0]
    if cmd == "MISSION":
        return
    elif cmd == "MUNITION":
        if tokens[1] == "commande":
            EtatGlobal.commande = lire_entree()
            executer_ligne(f"SELON {EtatGlobal.commande}")
        elif tokens[1] in ["x", "y", "z"]:
            nom = tokens[1]
            if len(tokens) > 4 and tokens[3] == "ASSAUT":
                x = EtatGlobal.variables.get(tokens[4], 0)
                y = EtatGlobal.variables.get(tokens[5], 0)
                EtatGlobal.variables[nom] = x + y
                EtatGlobal.registres[2] = x + y  # R2 pour z
            else:
                valeur = int(tokens[3])
                EtatGlobal.variables[nom] = valeur
                idx = {"x": 0, "y": 1, "z": 2}.get(nom, 0)
                EtatGlobal.registres[idx] = valeur
    elif cmd == "ASSAUT":
        EtatGlobal.registres[2] = EtatGlobal.registres[0] + EtatGlobal.registres[1]
    elif cmd == "RAPPORT":
        texte = " ".join(tokens[1:]).strip('"')
        if "FUSION" in texte:
            parts = texte.split("FUSION")
            var = parts[1].strip()
            valeur = EtatGlobal.variables.get(var, EtatGlobal.registres[2])
            texte = parts[0] + str(valeur)
        afficher(texte, "ROUGE")
    elif cmd == "EXECUTION":
        sous_cmd = tokens[1]
        if sous_cmd == "GuerreGraph.AfficherTexteStrategique":
            texte = tokens[2].strip('"')
            if "FUSION" in texte:
                texte = texte.replace("FUSION EtatGlobal.registres", str(EtatGlobal.registres))
            couleur = tokens[3]
            afficher(texte, couleur)
        elif sous_cmd == "GuerreGraph.EffetMatrixTactique":
            duree = int(tokens[2])
            afficher("SIMULATION EFFET MATRIX...", "VERT")
            start = time.time()
            while time.time() - start < duree / 1000:
                ligne = ''.join(random.choice("アカサタナABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(20))
                afficher(ligne, "VERT")
                attendre(50)
    elif cmd == "EFFACER_ECRAN":
        effacer_ecran()
    elif cmd == "AFFICHER":
        texte = " ".join(tokens[1:-1]).strip('"')
        couleur = tokens[-1]
        afficher(texte, couleur)
    elif cmd == "ATTENDRE":
        ms = int(tokens[1])
        attendre(ms)
    elif cmd == "TERMINER":
        exit(0)
    elif cmd == "SELON":
        commande = EtatGlobal.commande.strip()
        if commande == "help":
            afficher("Commandes : help, deploy, run_vm, monitor, recon, status, halt, reset, config, report", "ROUGE")
            redessiner()
        elif commande == "deploy":
            afficher("Déploiement en cours...", "ROUGE")
            attendre(2000)
            afficher("Déploiement terminé.", "ROUGE")
            redessiner()
        elif commande == "run_vm":
            afficher(f"Résultat dans R2 : {EtatGlobal.registres[2]}", "ROUGE")
            redessiner()
        elif commande == "monitor":
            afficher("Lancement du moniteur...", "ROUGE")
            while True:
                afficher(f"CPU simulé : {random.randint(10, 95)}%", "ROUGE")
                attendre(50)
                redessiner()
        elif commande == "recon":
            afficher("Reconnaissance en cours...", "ROUGE")
            attendre(1500)
            for i in range(3):
                x, y = random.randint(0, 100), random.randint(0, 100)
                afficher(f"Position {i}: ({x}, {y})", "ROUGE")
            redessiner()
        elif commande == "status":
            afficher(f"Registres : {EtatGlobal.registres}", "ROUGE")
            redessiner()
        elif commande == "halt":
            afficher("Arrêt du système...", "ROUGE")
            attendre(1000)
            exit(0)
        elif commande == "reset":
            afficher("Réinitialisation...", "ROUGE")
            EtatGlobal.registres = [0, 0, 0, 0]
            EtatGlobal.variables = {}
            redessiner()
        elif commande == "config":
            afficher("Configuration simulée", "ROUGE")
            redessiner()
        elif commande == "report":
            afficher("Rapport simulé", "ROUGE")
            redessiner()
        else:
            afficher(f"Commande inconnue : {commande}", "ROUGE")
            redessiner()

def redessiner():
    effacer_ecran()
    for msg in EtatGlobal.messages:
        print(msg)
    print("\033[92m> \033[0m", end="", flush=True)

def boucle_execution():
    initialiser_interpreteur()
    charger_fichier_gma("guerrelang_cli.gma")
    while EtatGlobal.compteur_programme < len(EtatGlobal.programme):
        ligne = EtatGlobal.programme[EtatGlobal.compteur_programme].strip()
        if ligne:
            executer_ligne(ligne)
        EtatGlobal.compteur_programme += 1

boucle_execution()
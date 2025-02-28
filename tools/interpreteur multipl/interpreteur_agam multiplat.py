# interpreteur_agam.py
import time
import random

# État de la VM
vm_state = {
    "registres": [0, 0, 0, 0],
    "compteur_programme": 0,
    "pile": [],
    "memoire": [0] * 1024,
    "drapeau_zero": False,
    "drapeau_negatif": False,
    "programme": [],
    "taille_memoire": 1024,
    "taille_registres": 4
}

# État du runtime
runtime_state = {
    "processus_actifs": [],
    "ressources_systeme": [],
    "gestionnaire_memoire": {
        "heap_debut": 0x1000,
        "heap_taille": 0x100000,
        "segments_libres": [{"adresse": 0x1000, "taille": 0x100000}]
    },
    "table_interruptions": [],
    "processus_en_cours": 0
}

# État du moniteur
moniteur_state = {
    "sondes": [
        {"type": "PERFORMANCES", "metriques": ["CPU", "MEMOIRE", "IO"], "intervalle": 100, "dernier_check": 0, "valeurs": {"CPU": 0, "MEMOIRE": 0, "IO": 0}},
        {"type": "EXECUTION", "metriques": ["INSTRUCTIONS", "CYCLES", "BRANCHES"], "intervalle": 50, "dernier_check": 0, "valeurs": {"INSTRUCTIONS": 0, "CYCLES": 0, "BRANCHES": 0}},
        {"type": "RESSOURCES", "metriques": ["FICHIERS", "THREADS", "SOCKETS"], "intervalle": 200, "dernier_check": 0, "valeurs": {"FICHIERS": 0, "THREADS": 0, "SOCKETS": 0}}
    ],
    "alertes": {
        "seuils": {"cpu_max": 90, "memoire_max": 85, "io_max": 1000},
        "actions": ["LOG", "ALERTE"]
    }
}

# Terminal
terminal_lines = []

def afficher_texte(texte, couleur="ROUGE"):
    print(f"[{couleur}] {texte}")
    terminal_lines.append(f"[{couleur}] {texte}")

def attendre(milliseconds):
    time.sleep(milliseconds / 1000)

# VM
def vm_initialiser():
    vm_state["registres"] = [0, 0, 0, 0]
    vm_state["compteur_programme"] = 0
    vm_state["pile"] = []
    vm_state["memoire"] = [0] * vm_state["taille_memoire"]

def vm_charger_programme(programme):
    vm_state["programme"] = programme

def vm_executer_instruction(instruction):
    opcode = instruction.get("opcode")
    if opcode == "0x01":  # CHARGER
        reg = instruction["registre"]
        val = instruction["valeur"]
        if 0 <= reg < vm_state["taille_registres"]:
            vm_state["registres"][reg] = val
    elif opcode == "0x03":  # ADDITIONNER
        reg1 = instruction["reg1"]
        reg2 = instruction["reg2"]
        regDest = instruction["regDest"]
        if all(0 <= r < vm_state["taille_registres"] for r in [reg1, reg2, regDest]):
            vm_state["registres"][regDest] = vm_state["registres"][reg1] + vm_state["registres"][reg2]
    if not instruction.get("type_saut", False):
        vm_state["compteur_programme"] += 1

def vm_executer_programme(programme):
    vm_initialiser()
    vm_charger_programme(programme)
    cycles = 0
    while vm_state["compteur_programme"] < len(programme):
        vm_executer_instruction(programme[vm_state["compteur_programme"]])
        cycles += 1
    moniteur_state["sondes"][1]["valeurs"]["CYCLES"] = cycles
    moniteur_state["sondes"][1]["valeurs"]["INSTRUCTIONS"] = len(programme)

# Runtime
def runtime_initialiser():
    runtime_state["processus_actifs"] = []
    runtime_state["gestionnaire_memoire"]["segments_libres"] = [{"adresse": 0x1000, "taille": 0x100000}]
    runtime_state["table_interruptions"] = []
    afficher_texte("Runtime initialisé", "ROUGE")

def runtime_allouer_memoire(taille):
    for segment in runtime_state["gestionnaire_memoire"]["segments_libres"]:
        if segment["taille"] >= taille:
            adresse = segment["adresse"]
            segment["adresse"] += taille
            segment["taille"] -= taille
            moniteur_state["sondes"][0]["valeurs"]["MEMOIRE"] += taille / runtime_state["gestionnaire_memoire"]["heap_taille"] * 100
            return adresse
    afficher_texte("ERREUR: Pas assez de mémoire", "ROUGE")
    return -1

def runtime_gerer_processus(commande):
    if "run_vm" in commande:
        programme = [
            {"opcode": "0x01", "registre": 0, "valeur": 5},
            {"opcode": "0x01", "registre": 1, "valeur": 3},
            {"opcode": "0x03", "reg1": 0, "reg2": 1, "regDest": 2}
        ]
        vm_executer_programme(programme)
        afficher_texte(f"Résultat dans R2 : {vm_state['registres'][2]}", "ROUGE")

# Moniteur
def initialiser_sonde(sonde):
    sonde["dernier_check"] = time.time() * 1000
    afficher_texte(f"Sonde {sonde['type']} initialisée", "ROUGE")

def collecter_metriques(sonde):
    current_time = time.time() * 1000
    if current_time - sonde["dernier_check"] >= sonde["intervalle"]:
        if sonde["type"] == "PERFORMANCES":
            sonde["valeurs"]["CPU"] = random.randint(10, 95)
            sonde["valeurs"]["MEMOIRE"] = moniteur_state["sondes"][0]["valeurs"]["MEMOIRE"]
            sonde["valeurs"]["IO"] = random.randint(0, 1200)
        elif sonde["type"] == "EXECUTION":
            sonde["valeurs"]["INSTRUCTIONS"] += random.randint(0, 10)
            sonde["valeurs"]["CYCLES"] += random.randint(0, 20)
            sonde["valeurs"]["BRANCHES"] += random.randint(0, 5)
        elif sonde["type"] == "RESSOURCES":
            sonde["valeurs"]["FICHIERS"] = random.randint(0, 5)
            sonde["valeurs"]["THREADS"] = len(runtime_state["processus_actifs"])
            sonde["valeurs"]["SOCKETS"] = random.randint(0, 3)
        sonde["dernier_check"] = current_time

def depassement_seuil(sonde):
    if sonde["type"] == "PERFORMANCES":
        if sonde["valeurs"]["CPU"] > moniteur_state["alertes"]["seuils"]["cpu_max"]:
            return {"metrique": "CPU", "valeur": sonde["valeurs"]["CPU"], "seuil": moniteur_state["alertes"]["seuils"]["cpu_max"]}
        if sonde["valeurs"]["MEMOIRE"] > moniteur_state["alertes"]["seuils"]["memoire_max"]:
            return {"metrique": "MEMOIRE", "valeur": sonde["valeurs"]["MEMOIRE"], "seuil": moniteur_state["alertes"]["seuils"]["memoire_max"]}
        if sonde["valeurs"]["IO"] > moniteur_state["alertes"]["seuils"]["io_max"]:
            return {"metrique": "IO", "valeur": sonde["valeurs"]["IO"], "seuil": moniteur_state["alertes"]["seuils"]["io_max"]}
    return None

def generer_alerte(sonde, depassement):
    alerte = {
        "timestamp": time.time(),
        "type": sonde["type"],
        "metrique": depassement["metrique"],
        "valeur": depassement["valeur"],
        "seuil": depassement["seuil"]
    }
    for action in moniteur_state["alertes"]["actions"]:
        if action == "LOG":
            afficher_texte(f"Alerte {alerte['type']}: {alerte['metrique']}={alerte['valeur']} > {alerte['seuil']}", "ROUGE_ROSE")
        elif action == "ALERTE":
            afficher_texte(f"ATTENTION : Seuil dépassé pour {alerte['metrique']}", "ROUGE_ROSE")

def surveillance_execution():
    for sonde in moniteur_state["sondes"]:
        initialiser_sonde(sonde)
    while True:
        for sonde in moniteur_state["sondes"]:
            collecter_metriques(sonde)
            depassement = depassement_seuil(sonde)
            if depassement:
                generer_alerte(sonde, depassement)
        attendre(50)

# CLI
def effet_matrix(duree):
    afficher_texte("Simulation effet Matrix...", "VERT")
    for _ in range(int(duree / 50)):
        ligne = "".join(random.choice("アカサタナABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(20))
        afficher_texte(ligne, "VERT")
        attendre(50)

def initialisation():
    runtime_initialiser()
    effet_matrix(3000)
    afficher_texte("SYSTÈME AGAM v1.0", "ROUGE")
    afficher_texte("Initialisation...", "ROUGE")
    attendre(1000)
    afficher_texte("Prêt. Tapez 'help' pour les commandes.", "ROUGE")

def traiter_commande(commande):
    if commande == "help":
        afficher_texte("Commandes : help, deploy, run_vm, monitor", "ROUGE")
    elif commande == "deploy":
        afficher_texte("Déploiement en cours...", "ROUGE")
        adresse = runtime_allouer_memoire(100)
        attendre(2000)
        afficher_texte(f"Déploiement terminé à l'adresse {adresse}", "ROUGE")
    elif commande == "run_vm":
        runtime_gerer_processus("run_vm")
    elif commande == "monitor":
        afficher_texte("Lancement du moniteur...", "ROUGE")
        surveillance_execution()
    else:
        afficher_texte("Commande inconnue.", "ROUGE")

def boucle_principale():
    initialisation()
    while True:
        commande = input("> ")
        traiter_commande(commande)

if __name__ == "__main__":
    boucle_principale()
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <time.h>
#ifdef _WIN32
#include <windows.h>
#include <conio.h>
#ifndef ENABLE_VIRTUAL_TERMINAL_PROCESSING
#define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004
#endif
#else
#include <unistd.h>
#include <termios.h>
#include <sys/select.h>
#endif

#define MAX_LINE 1024
#define MAX_TOKENS 128
#define MAX_MESSAGES 5      // Messages fixes du menu
#define MAX_MATRIX_LINES 10 // Lignes pour l’effet Matrix
#define MEMORY_SIZE 1024
#define MAX_VARS 10         // Nombre maximum de variables utilisateur

typedef struct {
    int memoire[MEMORY_SIZE];
    int pointeur_memoire;
    int registres[4]; // R0, R1, R2, R3
    int pile[MEMORY_SIZE];
    int pile_taille;
    char messages[MAX_MESSAGES][MAX_LINE];  // Messages du menu
    char couleurs[MAX_MESSAGES][16];
    int num_messages;
    char matrix_lines[MAX_MATRIX_LINES][MAX_LINE]; // Lignes de l’effet Matrix
    int num_matrix_lines;
    char var_noms[MAX_VARS][16]; // Noms des variables utilisateur
    int var_valeurs[MAX_VARS];   // Valeurs des variables utilisateur
    int num_vars;                // Nombre de variables définies
    int matrix_speed;            // Vitesse de l’effet Matrix (ms)
} EtatGlobal;

EtatGlobal etat = {{0}, 0, {0}, {0}, 0, {{0}}, {{0}}, 0, {{0}}, 0, {{0}}, {0}, 0, 100};

#ifndef _WIN32
int kbhit(void) {
    struct timeval tv = {0, 0};
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(STDIN_FILENO, &fds);
    return select(STDIN_FILENO + 1, &fds, NULL, NULL, &tv);
}

int getch(void) {
    int ch;
    struct termios old_termios, new_termios;
    tcgetattr(STDIN_FILENO, &old_termios);
    new_termios = old_termios;
    new_termios.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &new_termios);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &old_termios);
    return ch;
}
#endif

void activer_ansi_windows(void) {
#ifdef _WIN32
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwMode = 0;
    GetConsoleMode(hOut, &dwMode);
    dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    SetConsoleMode(hOut, dwMode);
#endif
}

void attendre(int ms) {
#ifdef _WIN32
    Sleep(ms);
#else
    usleep(ms * 1000);
#endif
}

void effacer_ecran(void) {
    printf("\033[2J\033[H");
    fflush(stdout);
}

void afficher(const char *texte, const char *couleur) {
    if (etat.num_messages >= MAX_MESSAGES) {
        for (int i = 0; i < MAX_MESSAGES - 1; i++) {
            strcpy(etat.messages[i], etat.messages[i + 1]);
            strcpy(etat.couleurs[i], etat.couleurs[i + 1]);
        }
        etat.num_messages--;
    }
    strncpy(etat.messages[etat.num_messages], texte, MAX_LINE - 1);
    etat.messages[etat.num_messages][MAX_LINE - 1] = '\0';
    strncpy(etat.couleurs[etat.num_messages], couleur, 15);
    etat.couleurs[etat.num_messages][15] = '\0';
    etat.num_messages++;
}

void ajouter_ligne_matrix(const char *ligne) {
    if (etat.num_matrix_lines >= MAX_MATRIX_LINES) {
        for (int i = 0; i < MAX_MATRIX_LINES - 1; i++) {
            strcpy(etat.matrix_lines[i], etat.matrix_lines[i + 1]);
        }
        etat.num_matrix_lines--;
    }
    strncpy(etat.matrix_lines[etat.num_matrix_lines], ligne, MAX_LINE - 1);
    etat.matrix_lines[etat.num_matrix_lines][MAX_LINE - 1] = '\0';
    etat.num_matrix_lines++;
}

void generer_ligne_matrix(void) {
    char ligne[21];
    for (int i = 0; i < 20; i++) {
        ligne[i] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"[rand() % 36];
    }
    ligne[20] = '\0';
    ajouter_ligne_matrix(ligne);
}

void redessiner(const char *input, bool commande_en_cours) {
    effacer_ecran();
    for (int i = 0; i < etat.num_matrix_lines; i++) {
        printf("\033[92m%s\033[0m\n", etat.matrix_lines[i]);
    }
    for (int i = 0; i < etat.num_messages; i++) {
        const char *couleur_code = "\033[91m";
        if (strcmp(etat.couleurs[i], "VERT") == 0) couleur_code = "\033[92m";
        else if (strcmp(etat.couleurs[i], "ROUGE_ROSE") == 0) couleur_code = "\033[95m";
        printf("%s%s\033[0m\n", couleur_code, etat.messages[i]);
    }
    if (commande_en_cours) {
        printf("\033[92m> %s\033[0m", input);
    } else {
        printf("\033[92m> \033[0m");
    }
    fflush(stdout);
}

void initialiser_interpreteur(void) {
    memset(&etat, 0, sizeof(EtatGlobal));
    etat.matrix_speed = 100; // Vitesse par défaut
}

void executer_ligne(const char *ligne) {
    char ligne_copie[MAX_LINE];
    strncpy(ligne_copie, ligne, MAX_LINE - 1);
    ligne_copie[MAX_LINE - 1] = '\0';

    char tokens[MAX_TOKENS][MAX_LINE];
    int token_count = 0;
    char *token = strtok(ligne_copie, " ");
    while (token && token_count < MAX_TOKENS) {
        strncpy(tokens[token_count], token, MAX_LINE - 1);
        tokens[token_count][MAX_LINE - 1] = '\0';
        token_count++;
        token = strtok(NULL, " ");
    }
    if (token_count == 0) return;

    if (strcmp(tokens[0], "MISSION") == 0) {
        return;
    } else if (strcmp(tokens[0], "EXECUTION") == 0 && token_count >= 2) {
        if (strcmp(tokens[1], "GuerreGraph.EffetMatrixTactique") == 0 && token_count >= 3) {
            int duree = atoi(tokens[2]);
            clock_t start = clock();
            while ((clock() - start) * 1000 / CLOCKS_PER_SEC < duree) {
                generer_ligne_matrix();
                redessiner("", false);
                attendre(100);
            }
        } else if (strcmp(tokens[1], "GuerreGraph.AfficherTexteStrategique") == 0 && token_count >= 4) {
            char texte[MAX_LINE] = {0};
            const char *debut = strchr(ligne, '"');
            if (debut) {
                const char *fin = strchr(debut + 1, '"');
                if (fin) {
                    size_t longueur = fin - debut - 1;
                    if (longueur < MAX_LINE) {
                        strncpy(texte, debut + 1, longueur);
                        texte[longueur] = '\0';
                        afficher(texte, tokens[token_count - 1]);
                    }
                }
            }
        }
    } else if (strcmp(tokens[0], "RAPPORT") == 0) {
        char texte[MAX_LINE] = {0};
        const char *debut = strchr(ligne, '"');
        if (debut) {
            const char *fin = strchr(debut + 1, '"');
            if (fin) {
                size_t longueur = fin - debut - 1;
                if (longueur < MAX_LINE) {
                    strncpy(texte, debut + 1, longueur);
                    texte[longueur] = '\0';
                    afficher(texte, "ROUGE");
                }
            }
        } else {
            const char *debut_texte = ligne + strlen("RAPPORT ");
            while (*debut_texte == ' ') debut_texte++;
            afficher(debut_texte, "ROUGE");
        }
    } else if (strcmp(tokens[0], "ATTENDRE") == 0 && token_count >= 2) {
        attendre(atoi(tokens[1]));
    }
}

void executer_commande(const char *commande) {
    char cmd[32] = {0};
    sscanf(commande, "%31s", cmd);

    if (strcmp(cmd, "help") == 0) {
        afficher("Commandes : help, deploy, status, halt, set, get, add, clear_matrix, matrix_speed, reset_vars, version", "ROUGE");
    } else if (strcmp(cmd, "deploy") == 0) {
        afficher("Déploiement en cours...", "ROUGE");
        attendre(2000);
        afficher("Déploiement terminé.", "ROUGE");
    } else if (strcmp(cmd, "status") == 0) {
        char buffer[128];
        snprintf(buffer, 128, "Registres : [%d, %d, %d, %d]", 
                 etat.registres[0], etat.registres[1], etat.registres[2], etat.registres[3]);
        afficher(buffer, "ROUGE");
    } else if (strcmp(cmd, "halt") == 0) {
        afficher("Arrêt du système...", "ROUGE");
        attendre(1000);
        exit(0);
    } else if (strcmp(cmd, "set") == 0) {
        char nom[16];
        int valeur;
        if (sscanf(commande, "set %15s %d", nom, &valeur) == 2) {
            int idx = -1;
            for (int i = 0; i < etat.num_vars; i++) {
                if (strcmp(etat.var_noms[i], nom) == 0) {
                    idx = i;
                    break;
                }
            }
            if (idx == -1 && etat.num_vars < MAX_VARS) {
                idx = etat.num_vars++;
                strncpy(etat.var_noms[idx], nom, 15);
                etat.var_noms[idx][15] = '\0';
            }
            if (idx != -1) {
                etat.var_valeurs[idx] = valeur;
                char buffer[128];
                snprintf(buffer, 128, "Variable %s définie à %d", nom, valeur);
                afficher(buffer, "ROUGE");
            } else {
                afficher("Erreur : trop de variables", "ROUGE_ROSE");
            }
        } else {
            afficher("Usage : set <nom> <valeur>", "ROUGE_ROSE");
        }
    } else if (strcmp(cmd, "get") == 0) {
        char nom[16];
        if (sscanf(commande, "get %15s", nom) == 1) {
            for (int i = 0; i < etat.num_vars; i++) {
                if (strcmp(etat.var_noms[i], nom) == 0) {
                    char buffer[128];
                    snprintf(buffer, 128, "%s = %d", nom, etat.var_valeurs[i]);
                    afficher(buffer, "ROUGE");
                    return;
                }
            }
            afficher("Variable non trouvée", "ROUGE_ROSE");
        } else {
            afficher("Usage : get <nom>", "ROUGE_ROSE");
        }
    } else if (strcmp(cmd, "add") == 0) {
        char reg[4];
        int valeur;
        if (sscanf(commande, "add %3s %d", reg, &valeur) == 2) {
            int reg_idx = -1;
            if (strcmp(reg, "R0") == 0) reg_idx = 0;
            else if (strcmp(reg, "R1") == 0) reg_idx = 1;
            else if (strcmp(reg, "R2") == 0) reg_idx = 2;
            else if (strcmp(reg, "R3") == 0) reg_idx = 3;
            if (reg_idx != -1) {
                etat.registres[reg_idx] += valeur;
                char buffer[128];
                snprintf(buffer, 128, "%s = %d", reg, etat.registres[reg_idx]);
                afficher(buffer, "ROUGE");
            } else {
                afficher("Registre invalide (R0-R3)", "ROUGE_ROSE");
            }
        } else {
            afficher("Usage : add <reg> <valeur>", "ROUGE_ROSE");
        }
    } else if (strcmp(cmd, "clear_matrix") == 0) {
        etat.num_matrix_lines = 0;
        afficher("Effet Matrix effacé", "ROUGE");
    } else if (strcmp(cmd, "matrix_speed") == 0) {
        int vitesse;
        if (sscanf(commande, "matrix_speed %d", &vitesse) == 1 && vitesse > 0) {
            etat.matrix_speed = vitesse;
            char buffer[128];
            snprintf(buffer, 128, "Vitesse Matrix définie à %d ms", vitesse);
            afficher(buffer, "ROUGE");
        } else {
            afficher("Usage : matrix_speed <ms> (valeur positive)", "ROUGE_ROSE");
        }
    } else if (strcmp(cmd, "reset_vars") == 0) {
        etat.num_vars = 0;
        memset(etat.var_noms, 0, sizeof(etat.var_noms));
        memset(etat.var_valeurs, 0, sizeof(etat.var_valeurs));
        afficher("Variables réinitialisées", "ROUGE");
    } else if (strcmp(cmd, "version") == 0) {
        afficher("AGAM Interpreter v1.0", "ROUGE");
    } else {
        char buffer[128];
        snprintf(buffer, 128, "Commande inconnue : %s", commande);
        afficher(buffer, "ROUGE_ROSE");
    }
}

void boucle_execution(void) {
    initialiser_interpreteur();

    const char *code_cli = 
        "MISSION Initialisation\n"
        "    EXECUTION GuerreGraph.EffetMatrixTactique 3000\n"
        "    EXECUTION GuerreGraph.AfficherTexteStrategique \"SYSTEME AGAM v1.0\" ROUGE\n"
        "    RAPPORT \"Initialisation...\"\n"
        "    ATTENDRE 1000\n"
        "    RAPPORT \"Pret. Tapez 'help'.\"\n"
        "FIN MISSION\n";

    char ligne[MAX_LINE];
    const char *ptr = code_cli;
    while (*ptr) {
        const char *newline = strchr(ptr, '\n');
        if (!newline) {
            strncpy(ligne, ptr, MAX_LINE - 1);
            ligne[MAX_LINE - 1] = '\0';
            executer_ligne(ligne);
            break;
        }
        size_t longueur = newline - ptr;
        if (longueur < MAX_LINE) {
            strncpy(ligne, ptr, longueur);
            ligne[longueur] = '\0';
            executer_ligne(ligne);
            redessiner("", false);
            attendre(100);
        }
        ptr = newline + 1;
    }

    char input[MAX_LINE] = {0};
    int input_pos = 0;
    bool commande_en_cours = false;

    while (true) {
#ifdef _WIN32
        if (_kbhit()) {
#else
        if (kbhit()) {
#endif
            char c;
#ifdef _WIN32
            c = _getch();
#else
            c = getch();
#endif
            if (c == '\n' || c == '\r') {
                input[input_pos] = '\0';
                if (strlen(input) > 0) {
                    executer_commande(input);
                }
                input_pos = 0;
                memset(input, 0, sizeof(input));
                commande_en_cours = false;
            } else if (input_pos < MAX_LINE - 1) {
                input[input_pos++] = c;
                commande_en_cours = true;
            }
            redessiner(input, commande_en_cours);
        } else {
            generer_ligne_matrix();
            redessiner(input, commande_en_cours);
            attendre(etat.matrix_speed);
        }
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    activer_ansi_windows();
    boucle_execution();
    return 0;
}
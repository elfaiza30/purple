def ask_float(prompt, min_val=0, max_val=1000):
    while True:
        try:
            val = float(input(prompt))
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Veuillez entrer une valeur entre {min_val} et {max_val}.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre.")

def band_mtt(value_min, table):
    for upper, score in table:
        if value_min < upper:
            return score
    return table[-1][1]

def get_maturity_label(level):
    labels = {
        0: "Faible",
        1: "Émergent",
        2: "Structurant",
        3: "Stabilisé",
        4: "Piloté",
        5: "Optimisé (exemplarité SOC)"
    }
    return labels.get(level, "Inconnu")

def compute_scores():
    print("=== Entrée des données Purple Teaming ===\n")

    # Couverture
    tech_tested = ask_float("→ Nombre de techniques MITRE testées : ")
    tech_target = ask_float("→ Nombre de techniques cibles définies : ")
    tactics     = ask_float("→ Nombre de tactiques ATT&CK couvertes (max 14) : ", 1, 14)

    # Détection
    events_detected = ask_float("→ Nombre d'événements détectés : ")
    red_actions     = ask_float("→ Nombre total d'actions Red Team : ")
    tp              = ask_float("→ Nombre de true positives (TP) : ")
    fp              = ask_float("→ Nombre de false positives (FP) : ")
    mttd            = ask_float("→ Temps moyen de détection (en secondes) : ")

    # Réponse
    mttr           = ask_float("→ Temps moyen de réponse (en secondes) : ")
    actions_missed = ask_float("→ Nombre d'actions Red non traitées : ", 0, red_actions)

    # Collaboration
    scen_doc   = ask_float("→ Nombre de scénarios documentés : ")
    scen_exec  = ask_float("→ Nombre de scénarios exécutés : ")
    recos_app  = ask_float("→ Nombre de recommandations appliquées : ")
    recos_prop = ask_float("→ Nombre de recommandations proposées : ")

    # Calcul
    C = ((100 * tech_tested / tech_target) + (100 * tactics / 14)) / 2

    D_rate = 100 * events_detected / red_actions
    D_prec = 100 * tp / (tp + fp) if (tp + fp) != 0 else 0
    D_mttd = band_mtt(mttd / 60, [(5, 100), (15, 80), (30, 60), (60, 40), (float('inf'), 20)])
    D = (D_rate + D_prec + D_mttd) / 3

    R_mttr = band_mtt(mttr / 60, [(10, 100), (30, 80), (60, 60), (float('inf'), 40)])
    R_miss = (1 - (actions_missed / red_actions)) * 100
    R = (R_mttr + R_miss) / 2

    Co_doc = 100 * scen_doc / scen_exec
    Co_rec = 100 * recos_app / recos_prop
    Co = (Co_doc + Co_rec) / 2

    score = 0.25 * C + 0.30 * D + 0.25 * R + 0.20 * Co

    if score < 21:
        level = 0
    elif score < 41:
        level = 1
    elif score < 61:
        level = 2
    elif score < 81:
        level = 3
    elif score < 91:
        level = 4
    else:
        level = 5

    label = get_maturity_label(level)

    print("\n=== RÉSULTATS DE MATURITÉ PURPLE TEAMING ===")
    print(f"Score Couverture    : {C:.1f}")
    print(f"Score Détection     : {D:.1f}")
    print(f"Score Réponse       : {R:.1f}")
    print(f"Score Collaboration : {Co:.1f}")
    print(f"Score global Purple : {score:.1f} / 100")
    print(f"Niveau de maturité  : {level} / 5 — {label}")

if __name__ == "__main__":
    compute_scores()

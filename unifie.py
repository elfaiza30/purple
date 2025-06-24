import pandas as pd
from tabulate import tabulate

# === PARAMÈTRES DE LA FORMULE ===
ALPHA = 0.6  # Pondération Gouvernance (SOC)
BETA = 0.4   # Pondération Purple Team

def fusion_score(score_gouv, score_purple, alpha=ALPHA, beta=BETA):
    """
    Applique la formule de fusion :
    Score final = α × Score Gouvernance + β × Score Purple Team
    """
    return alpha * score_gouv + beta * score_purple

def niveau_maturite(score):
    """
    Retourne le niveau de maturité associé à un score global.
    """
    levels = [
        (0, 0.2, 'Niveau 0–1 (Initial)'),
        (0.2, 0.4, 'Niveau 1 (Structurant)'),
        (0.4, 0.6, 'Niveau 2 (Stabilisé)'),
        (0.6, 0.8, 'Niveau 3 (Piloté)'),
        (0.8, 0.9, 'Niveau 4 (Transformant débutant)'),
        (0.9, 1.01, 'Niveau 5 (Transformant avancé)')
    ]
    for low, high, label in levels:
        if low <= score < high:
            return label
    return "Non déterminé"

def demander_score_purple():
    """
    Demande le score Purple Team à l'utilisateur (entre 0 et 1).
    """
    while True:
        try:
            s = float(input("Veuillez entrer le score Purple Team (entre 0 et 1) : ").replace(",", "."))
            if 0 <= s <= 1:
                return s
            else:
                print("Le score doit être compris entre 0 et 1.")
        except Exception:
            print("Entrée non valide. Essayez encore.")

def charger_score_gouvernance(responses_path, weights_path):
    """
    Charge le score global de gouvernance (SOC) depuis les fichiers Excel.
    Nécessite la même logique que le script d'évaluation SOC d'origine.
    """
    # --- Copie minimale du calcul du score SOC global ---
    # (Voir le script de maturité SOC complet pour la version détaillée)
    # Ici, on suppose que le score gouvernance est la première ligne du tableau de résultats.
    # On simplifie pour se concentrer sur la fusion, pas sur l'évaluation détaillée.
    from collections import defaultdict

    responses = pd.read_excel(responses_path)
    weights = pd.read_excel(weights_path, sheet_name="Pondération SOC")
    questions_meta = {}
    response_scale = {
        '1 – Pas du tout présent': 0,
        '2 – Partiellement présent': 0.25,
        '3 – Moyennement présent': 0.5,
        '4 – Presque entièrement présent': 0.75,
        '5 – Totalement mis en place': 1,
        'N/A – Non applicable à notre organisation': None
    }
    proof_quality = {
        'Aucune preuve': 0,
        'Preuve faible ou partielle': 0.33,
        'Preuve adéquate': 0.67,
        'Preuve solide et vérifiable': 1
    }
    for _, row in weights.iterrows():
        qid = row['Code Question']
        if pd.notna(qid):
            questions_meta[qid] = {
                'component': row['Composant'],
                'domain': row['Domaine'],
                'q_weight': row['Pondération question (1.0–1.2)'],
                'c_weight': row['Pondération composant (1.0–1.3)'],
                'critical': str(row['Criticité du composant']).strip().lower() == 'oui'
            }

    # On prend la première évaluation (ligne)
    row = responses.iloc[0]
    c_questions = defaultdict(list)
    for qid, meta in questions_meta.items():
        r_cols = [col for col in row.index if col.startswith(f"{qid} –") and 'preuve' not in col.lower()]
        p_cols = [col for col in row.index if col.startswith(f"{qid} –") and 'preuve' in col.lower()]
        if not r_cols or not p_cols:
            continue
        resp_val = row[r_cols[0]]
        proof_val = row[p_cols[0]]
        if resp_val in (None, 'N/A – Non applicable à notre organisation'):
            continue
        base = response_scale.get(resp_val, 0)
        factor = proof_quality.get(proof_val, 0)
        score = base * (0.7 + 0.3 * factor)
        c_questions[meta['component']].append((score, meta['q_weight']))

    c_scores = {}
    for comp, scores in c_questions.items():
        total = sum(s * w for s, w in scores)
        weight = sum(w for _, w in scores)
        c_scores[comp] = total / weight if weight else 0

    # Calcul domaine
    domain_weights = {'Personnel': 1, 'Technologie': 1, 'Processus': 1, 'Indicateurs': 1}
    d_scores = defaultdict(float)
    d_weights = defaultdict(float)
    for qid, meta in questions_meta.items():
        comp = meta['component']
        dom = meta['domain']
        if comp in c_scores:
            w = meta['c_weight']
            d_scores[dom] += c_scores[comp] * w
            d_weights[dom] += w
    for dom in d_scores:
        d_scores[dom] /= d_weights[dom]

    global_score = sum(d_scores[d] * domain_weights.get(d, 1) for d in d_scores)
    total_dw = sum(domain_weights.get(d, 1) for d in d_scores)
    global_score = global_score / total_dw if total_dw else 0

    return global_score

if __name__ == "__main__":
    print("=== Fusion de Score selon la formule:")
    print("    Score final = α × Score Gouvernance + β × Score Purple Team")
    print(f"    α = {ALPHA} | β = {BETA}\n")

    responses_path = "Formulaire sans titre (réponses).xlsx"
    weights_path = "Tableau_Ponderation_SOC.xlsx"

    # 1. Calcul/Gestion du score gouvernance (SOC)
    score_gouv = charger_score_gouvernance(responses_path, weights_path)
    print(f"Score Gouvernance (SOC): {score_gouv:.2%}")

    # 2. Demande du score Purple Team
    score_purple = demander_score_purple()

    # 3. Fusion
    score_final = fusion_score(score_gouv, score_purple, ALPHA, BETA)
    niveau_final = niveau_maturite(score_final)

    # 4. Présentation synthétique
    print("\n=== RÉSULTAT DE LA FUSION ===")
    print(tabulate([{
        "Score Gouvernance": f"{score_gouv:.2%}",
        "Score Purple Team": f"{score_purple:.2%}",
        "Score final fusionné": f"{score_final:.2%}",
        "Niveau maturité final": niveau_final
    }], headers='keys', tablefmt='fancy_grid'))
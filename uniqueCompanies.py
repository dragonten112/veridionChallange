

import pandas as pd

# Funcție simplă pentru similaritate de nume (exact match la început)
from difflib import SequenceMatcher
def name_similarity(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def deduplicate(df, name_thresh=0.85):
    cluster_id = [-1] * len(df)
    current_cluster = 0

    # Blocking
    blocks = {}

    # Blocking pe domeniu
    if "website_domain" in df.columns:
        for idx, val in df["website_domain"].dropna().items():
            blocks.setdefault(("domain", val), []).append(idx)

    # Blocking pe telefon
    if "primary_phone" in df.columns:
        for idx, val in df["primary_phone"].dropna().items():
            blocks.setdefault(("phone", val), []).append(idx)

    # Blocking pe email
    if "primary_email" in df.columns:
        for idx, val in df["primary_email"].dropna().items():
            blocks.setdefault(("email", val), []).append(idx)

    # Blocking pe nume, tara si oras
    if {"company_name", "main_country", "main_city"}.issubset(df.columns):
        for idx, row in df.iterrows():
            if pd.notna(row["company_name"]) and pd.notna(row["main_country"]) and pd.notna(row["main_city"]):
                key = ("name_loc", str(row["company_name"]).lower(), row["main_country"], row["main_city"])
                blocks.setdefault(key, []).append(idx)

    # Atribuire cluster_id
    for group in blocks.values():
        assigned = [i for i in group if cluster_id[i] != -1]
        if assigned:
            cid = cluster_id[assigned[0]]
        else:
            cid = current_cluster
            current_cluster += 1
        for i in group:
            cluster_id[i] = cid

    
    for i in range(len(df)):
        if cluster_id[i] == -1:
            cluster_id[i] = current_cluster
            current_cluster += 1

    df["cluster_id"] = cluster_id
    return df

def main():
    df = pd.read_excel("C:\\Users\\razva\\Desktop\\Challenge veridion\\coloane_extrase_no_empty_rows.xlsx")
    df_result = deduplicate(df)
    df_result.to_excel("C:\\Users\\razva\\Desktop\\Challenge veridion\\rezultat_final.xlsx", index=False)
    print("✅ Deduplication complete. Saved as companies_deduped.xlsx")

if __name__ == "__main__":
    main()

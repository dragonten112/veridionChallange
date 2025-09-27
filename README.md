# veridionChallenge


# 1. Selectia datelor
Pentru inceput, am analizat in mare dataset-ul, si am ales coloanele relevante pentru identificarea unei companii. Pentru aceasta operatie am folosit un script in python sa putem separa doar coloanele selectate pentru identificare fata de dataset-ul original.

Coloanele selectate din dataset-ul original au fost:
`company_name`, `company_legal_names`, `company_commercial_names`, `main_country`, `main_city`, `main_postcode`,
`main_address_raw_text`, `website_domain`, `all_domains`, `primary_email`, `emails`, `primary_phone`, `phone_numbers`.

## Scriptul folosit pentru extragerea coloanelor: 
```python
import pandas as pd

input_file = "C:\\Users\\razva\\Desktop\\Challenge veridion\\veridion_entity_resolution_challenge.xlsx"


sheet_name = "Sheet1"


cols_minime = [
    "company_name",
    "company_legal_names",
    "company_commercial_names",
    "main_country",
    "main_city",
    "main_postcode",
    "main_address_raw_text",
    "website_domain",
    "all_domains",
    "primary_email",
    "emails",
    "primary_phone",
    "phone_numbers",
]


df = pd.read_excel(input_file, sheet_name=sheet_name, usecols=cols_minime)


output_file = "coloane_extrase.xlsx"
df.to_excel(output_file, index=False)

print(f"Fisierul a fost salvat: {output_file}")
```

# Interpretarea celulelor goale
Pentru celulele goale din `company_legal_names` am interpretat ca, au acelasi nume ca si in coloana cu company_name deoarece mereu se afla nume identice ale companiilor, fiind obligatoriu ca orice companie sa aiba un nume legal oficial.
Pentru celulele goale din `company_commercial_names` am interpretat ca, nu au neaparat un nume neaparat pentru comercializare, nefiind obligatoriu sa ai un nume comercial fata de numele legal.

In cazul coloanelor :
-`primary_email`: nu au sau nu au gasit o adresa de email pentru compania respectiva. 
-`emails`: sunt goale deoarece compania nu are, sau nu s-a gasit un email fata de cel principal al companiei. 
-`website_domain` & `all_domains` sunt ambele celule goale in cadrul unei companii, compania nu are un site existent sau nu s-a gasit un site al companiei.

-`primary_phone`: Nu a fost gasit un numar al companiei de catre LLM

## De mentionat ca am convertit si fisierul `.parquet` in `xlsx` prin script-ul:

```python
import pandas as pd

def main():
    
    input_path = "C:\\Users\\razva\\Desktop\\Challenge veridion\\veridion_entity_resolution_challenge.snappy.parquet"
    output_path = "C:\\Users\\razva\\Desktop\\Challenge veridion\\veridion_entity_resolution_challenge.xlsx"

    print(f"Loading Parquet file: {input_path}")

    
    df = pd.read_parquet(input_path, engine="pyarrow")  # sau "fastparquet"

    print(f"Dataset loaded with shape: {df.shape}")

   
    df.to_excel(output_path, index=False, engine="openpyxl")

    print(f"✅ Excel file saved: {output_path}")

if __name__ == "__main__":
    main()
```
# 2. Curatarea si normalizarea datelor

## Am folosit script-uri necesare pentru curatarea datelor si normalizarea lor.
Am curatat randurile ce erau complet goale pentru ca nu aduc niciun fel de informatie si doar incarca fisierul.


# 3. Gasirea Companiilor Unice

Mai departe pentru a gasirea de "aceeasi companie", am folosit `clusterizarea` si `blocking` pentru a rezolva partea de viteza, sa nu comparam tot cu tot, formand o noua coloana de `cluster_id` in noul Fisier .`xlsx` salvat. Aceste doua metode functioneza bine pe acest dataset, unde exista campuri relevante pentru aceasta problema (ex: domain, email, telefon), perfect pentru fuzzy matching(numele companiilor pot varia), si este rapid si scalabil pentru a lucra pe milioane de randuri ceea ce face o metoda standard pentu "entity resolution".
-Pentru vizualizarea script-urilor, le-am incarcat in repository pentru descarcare
Script-ul in python pentru `blocking` si `clusterizare` este: `uniqueCompanies.py`

# Ce tip de Blocking am folosit:
Rule-based blocking cu reguli simple pe campuri cu valoare foarte puternica, nu am folosit metode avansate de tip LSH, sorted neighborhood, sau canopy clustering, deoarece pe un fisier in jur de 279365 de date (`coloane_extrase`) este suficient si foarte eficient.
Blocking-ul acesta este simplu si scalabil unde fiecare bloc are un criteriu clar, # eficient, unde nu comparam fiecare rand cu fiecare, pentru evitarea timpului indelungat de procesare, ci doar in interiorul blocurilor.
Nu exista scoruri de tip `fuzzy matching`, doar egalitate exacta.


```python
if "website_domain" in df.columns:
    for idx, val in df["website_domain"].dropna().items():
        blocks.setdefault(("domain", str(val).lower()), []).append(idx)

# Blocking pe primary_phone
if "primary_phone" in df.columns:
    for idx, val in df["primary_phone"].dropna().items():
        blocks.setdefault(("phone", str(val)), []).append(idx)

# Blocking pe primary_email
if "primary_email" in df.columns:
    for idx, val in df["primary_email"].dropna().items():
        blocks.setdefault(("email", str(val).lower()), []).append(idx)

# Blocking pe company_name + country + city
if {"company_name", "main_country", "main_city"}.issubset(df.columns):
    for idx, row in df.iterrows():
        if pd.notna(row["company_name"]) and pd.notna(row["main_country"]) and pd.notna(row["main_city"]):
            key = ("name_loc",
                   str(row["company_name"]).lower(),
                   str(row["main_country"]).lower(),
                   str(row["main_city"]).lower())
            blocks.setdefault(key, []).append(idx)

```
Aici, in bucata de cod afisata, fiecare cheie (domain,phone,email) creeaza un grup cu toti indexii de randuri care impart acea valoare.

# Ce tip de Clustering am folosit:
Am folosit o abordare de graph clustering / union-find bazata pe compenentele de :
- Blocking de a construit grupuri de "candidati", de ex: inregistrarile cu acelasi `website_domain`.
- In interiorul feicarui block am legat inregistrarile prin reguli (domain-email-telefon-nume+loc)
- Am cautat componentele conexe ale grafului unde toate nodurile formeaza un cluster iar acel cluster primeste un `cluster_id`.

```python


cluster_id = [-1] * len(df)
current_cluster = 0


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

```
Asta este fix algoritmul union-find components clustering unde:
- Daca doua randuri apar in acelasi loc, primesc acelasi cluster_id
- Daca un rand e conectat printr-un lant A-B-C -> toate ajung la acelasi cluster
- Daca un rand nu are nicio legatura, primeste un cluster unic.


## Am incarcat si fisierele excel pentru vizualizarea acestora in detaliu
De ce am folosit `.xlsx` si nu `.csv`?
R: Deoarece nu exista nicio diferenta in a lucra cu ambele extensii, doar singurul fapt ca `.csv` este mai rapid si mai optim pentru prelucrarea datelor, dar de aceasta data nu a fost nevoie pentru conversia in `.csv`.

## Abordarea a fost gandita sa fie simpla si eficienta cu tehnologiile aferente si potrivite pentru task-ul cerut:
1. Selectarea atributelor cu adeverat relevante din dataset-ul original de tip `.parquet` pentru identificarea companiilor
2. Aplicarea preprocesarii datelor corespunzatoare
3. Folosirea tehnicii Rule-Based Blocking pentru a reduce masiv nr. de comparatii.
4. Aplicarea ## Clusterizarii, obtinand grupuri clare de `deduplicate`.
5. Rezultatul final salvat pentru vizualizarea datelor.


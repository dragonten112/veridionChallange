# veridionChallenge


## 1.Selectia datelor
Pentru inceput, am analizat in mare dataset-ul, si am ales coloanele relevante pentru identificarea unei companii. Pentru aceasta operatie am folosit un script in python sa putem separa doar coloanele selectate pentru identificare fata de dataset-ul original.

Coloanele selectate din dataset-ul original au fost:
`company_name`, `company_legal_names`, `company_commercial_names`, `main_country`, `main_city`, `main_postcode`,
`main_address_raw_text`, `website_domain`, `all_domains`, `primary_email`, `emails`, `primary_phone`, `phone_numbers`.

**Scriptul folosit pentru extragerea coloanelor:**
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

## Interpretarea celulelor goale
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
## 2.Curatarea si normalizarea datelor

**Am folosit script-uri necesare pentru curatarea datelor si normalizarea lor.
Am curatat randurile ce erau complet goale pentru ca nu aduc niciun fel de informatie si doar incarca fisierul.


## 3.Gasirea Companiilor Unice

Mai departe pentru a gasirea de "aceeasi companie", am folosit `clusterizarea` si `blocking` pentru a rezolva partea de viteza, sa nu comparam tot cu tot, formand o noua coloana de `cluster_id` in noul Fisier .`xlsx` salvat. Aceste doua metode functioneza bine pe acest dataset, unde exista campuri relevante pentru aceasta problema (ex: domain, email, telefon), perfect pentru fuzzy matching(numele companiilor pot varia), si este rapid si scalabil pentru a lucra pe milioane de randuri ceea ce face o metoda standard pentu "entity resolution".


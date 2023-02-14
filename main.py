from datetime import date,timedelta
from dotenv import dotenv_values
from lowatt_grdf.api import API

config = dotenv_values(".env")
start = date.today() - timedelta(
    days=10,
)
day1 = timedelta(
    days=1,
)

grdf = API(config["CLIENT_ID"], config["CLIENT_SECRET"])
for releve in grdf.donnees_consos_informatives(
    config["PCE"],
    from_date=(start - day1).isoformat(),
    to_date=(start).isoformat()
):
    conso = releve["consommation"]
    print(conso["date_debut_consommation"], conso["date_fin_consommation"], conso["energie"])

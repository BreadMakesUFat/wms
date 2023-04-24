import pandas as pd 
import sqlite3 

file = "../data/deliveries_export.csv"
db_name = "../booking_test.db"
db = None 

translate_unit = {
    "STÜCK": "Կտոր",
    "KG": "կգ"
}


# TODO: update + remove amount from stock table
# TODO: add remove amount to new_delivery + barcode

if __name__ == "__main__":
    try:
        df = pd.read_csv(file, sep=";", )
        # remove edit row
        df = df.iloc[:, :-1]

        # add additional rows for translations
        df["ArticleDescriptionTranslated"] = None 
        df["UnitTranslated"] = None 
        df["GovernmentCode"] = None 
        

        # connect to db
        db = sqlite3.connect(db_name)

        # find translations for each row
        for i,row in df.iterrows():
            # bon is given
            if not row["BON"] == "None":
                # find article id 
                query = "SELECT ArticleID FROM stock WHERE BON = ?"
                params = (row["BON"], )
                cur = db.cursor()
                cur.execute(query, params)
                articleID = cur.fetchone()[0]
                if articleID:
                    df.at[i, "Article ID"] = articleID
                    unit = translate_unit.get(row["Unit"].upper().strip(), None)
                    df.at[i, "UnitTranslated"] = unit
                    # find translations
                    query = "SELECT ArticleDescription, GovernmentCode FROM articleTranslations WHERE ArticleID = ?"
                    params = (articleID, )
                    cur.execute(query, params)
                    translations = cur.fetchone()
                    if translations:
                        articleDescription = translations[0]
                        governmentCode = translations[1]
                        df.at[i, "ArticleDescriptionTranslated"] = articleDescription 
                        df.at[i, "GovernmentCode"] = governmentCode
            #  only article id is given
            elif not row["Article ID"] == "None":
                # find translations
                articleID = row["Article ID"]
                unit = translate_unit.get(row["Unit"].upper().strip(), None)
                df.at[i, "UnitTranslated"] = unit
                query = "SELECT ArticleDescription, GovernmentCode FROM articleTranslations WHERE ArticleID = ?"
                params = (articleID, )
                cur.execute(query, params)
                translations = cur.fetchone()
                if translations:
                    articleDescription = translations[0]
                    governmentCode = translations[1]
                    df.at[i, "ArticleDescriptionTranslated"] = articleDescription 
                    df.at[i, "GovernmentCode"] = governmentCode

            # invalid entry w/o bon and article id
            else:
                print(f"The current row {i} is invalid: There is no BON and no ArticleID!")

        # adjust schema
        df = df.rename(columns={
            "Article ID": "ArticleID",
            "Article Description": "ArticleDescription",
            "Key": "ID"
        })
        df = df.reset_index(drop=True)
        df = df.replace("None", None)
        df = df[["ID", "BON", "ArticleID", "ArticleDescription", "ArticleDescriptionTranslated", "Destination", "Recipient", "Amount", "Unit", "UnitTranslated", "Date", "GovernmentCode"]]

        # Insert into deliveries table
        df.to_sql(name="deliveries", con=db, if_exists="replace", index=False)

    except Exception as e:
        print("The migration was not successfull: An unexpected error occured! Maybe the stock table is empty.")
        print(e)
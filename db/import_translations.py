import pandas as pd
import sqlite3


file = "data/translations.xlsx"
db_name = "booking_test.db"
db = None 

if __name__ == "__main__":
    try:
        df = pd.read_excel(file, header=None)
        df.columns = ["1" ,"ArticleID", "GovernmentCode", "ArticleDescription", "5", "6", "7"]
        df = df[["ArticleID", "ArticleDescription", "GovernmentCode"]]
        
        keys = pd.unique(df["ArticleID"])
        d = {}
        d["ArticleID"] = keys 
        descriptions = []
        codes = []
        for key in keys:
            description = list(df.loc[df["ArticleID"] == key]["ArticleDescription"])
            code = list(df.loc[df["ArticleID"] == key]["GovernmentCode"])

            description = ", ".join([str(x) for x in description])
            code = ", ".join([str(x) for x in code])

            descriptions.append(description)
            codes.append(code)

        d["ArticleDescription"] = descriptions
        d["GovernmentCode"] = codes 
        data = pd.DataFrame.from_dict(d)

        db = sqlite3.connect(db_name)
        data.to_sql(name="articleTranslations", con=db, if_exists="replace")

    except Exception as e:
        print(e)
        if db is not None:
            db.close()

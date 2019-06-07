import pandas as pd

def aggregateJPMorganScraperData():
    top50df= pd.read_excel(r"JP_Morgan_all pages (1-50).xlsx")
    print("Read done")
    second50df= pd.read_excel(r"JP_Morgan_all pages(51-100).xlsx")
    print("Read done")
    third50df= pd.read_csv(r"JP_Morgan_all pages(100-150).csv")
    print("Read done")
    fourth50df= pd.read_excel(r"JP_Morgan_all pages(150-200).xlsx")
    print("Read done")
    aggregate1= top50df.append(second50df)
    aggregate2 = aggregate1.append(third50df)
    totalaggregate = aggregate2.append(fourth50df)
    print("aggregate done")
    return totalaggregate

if __name__ == "__main__":
    totalaggregate = aggregateJPMorganScraperData()
    totalaggregate.to_csv("totalaggregate_final.csv")
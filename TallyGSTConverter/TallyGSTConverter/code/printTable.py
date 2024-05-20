import tabulate

def printTable(df):
    print(tabulate.tabulate(df, tablefmt='fancy_outline', headers=df.columns.values))

def pretty_print():
    print ()
    print ("================================")
    print ()
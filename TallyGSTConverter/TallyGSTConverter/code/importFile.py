import pandas as pd
import getCompany, printTable

def readFile(company, transactionType):
    filepath = '../files/' + getCompany.clean_company_names(company) + '/' + transactionType + '/DayBook.xlsx'
    mappingFilepath = '../files/' + getCompany.clean_company_names(company) + '/mappings/' + transactionType + '_mappings.xlsx'

    try:
        df = pd.read_excel(filepath)
        df_mappings = pd.read_excel(mappingFilepath)
    except Exception:
        printTable.pretty_print()
        print ("\n[ERROR] Input or mappings file not found.\n")
        exit()

    printTable.pretty_print()
    print ("[INPUT SUCCESS] Input file read successfully. It has " + str(df.shape[0]) + " rows and " + str(df.shape[1]) + " columns.")
    printTable.pretty_print()
    
    return df, df_mappings
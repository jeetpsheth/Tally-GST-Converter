import pandas as pd
import numpy as np
import math, constants, getCompany, printTable, importFile, mappings

def queryDf(df, inputCol, inputVal, outputCol):
    return df.loc[df[inputCol] == inputVal][outputCol]

def verifyTaxrate(taxRate):
    if taxRate not in constants.taxRates and taxRate != 0:
        print ("[ERROR] tax rate of " + taxRate + " does not match standard rates")

def add_metadata(row):
    d = {}
    for key, value in constants.columns_map.items():
        if key in row:
            d[value]= row[key]
    return d

def compute_taxable_value(df, df_mappings, row):
    
    filter_col = []
    for i in df.columns.values:
        if i in df_mappings['Column Name'].values:
            index = np.where(df_mappings == i)[0][0]
            value = df_mappings.loc[index, 'Entry Type']
            if value == 'Taxable':
                filter_col.append(i)    
    taxable_value = row[filter_col].dropna().values.sum()
    taxable_value = 0 if np.isnan(taxable_value) else taxable_value
    
    return taxable_value

#Get all taxable cols from mappings, and filter for the ones in the df
def getLedger(df, dfMappings, row, outputList):
    taxableCols = set(queryDf(dfMappings, 'Entry Type', 'Taxable', 'Column Name'))
    dfCols = set(df.columns.values)
    intersectCols = list(taxableCols.intersection(dfCols))

    if len(outputList) > 1:
        for output in outputList:
            ledgerList = [i for i in intersectCols if str(output[1]) in i]
            output.append(row[ledgerList].idxmax())
    else:
        outputList[0].append(row[intersectCols].idxmax())

    return outputList 

# Gets the columns that are tax rates and filters for the taxType provided (ISGT, SGST, CGST)
# It returns the input row filtered for the above identified columns based on taxType
def getTaxDict(df, dfMappings, row):
    d = {t: 0 for t in constants.taxtypes}
    for taxType in constants.taxtypes:
        taxRateColsFromMappings = set(queryDf(dfMappings, 'Entry Type', 'Tax Rate', 'Column Name').values)
        taxColsFromDf = [col for col in df if col in taxRateColsFromMappings and taxType in col.upper()]

        filteredRow = row[taxColsFromDf].dropna()
        d[taxType] = filteredRow.to_dict()
    return d

# Checks for basic pre-conditions, which if incorrect, the respective records should be noted as errors. 
# Condition 1 -> Skip rows without any tax columns
# Condition1 -> CGST is always equal to SGST, Condition2 -> IGST and CGST/SGST cannot occur together in a single row 
def checkPreConditions(d):
    lenI, lenC, lenS = len(d['IGST']), len(d['CGST']), len(d['SGST'])

    if lenI == lenC == lenS == 0:
        return
    elif lenC != lenS:
        print ("[WARNING] Skipping row since CGST and SGST do not match")
        return
    elif lenI > 0 and lenC > 0:
        print ('[WARNING] Skipping row since IGST and CGST/SGST are together in a single row')
        return
    elif set(d['CGST'].values()) != set(d['SGST'].values()):
        print ("[WARNING] Skipping row since CGST and SGST values are not the same")
        return
    else:
        return True

def computeTaxes(d, taxType, df, row, dfMappings, transactionType):
    outputList = []
    for k, v in d:
        # Stores all 3 tax values in a dict
        tmpD = {t: 0 for t in constants.taxtypes}
        tmpD[taxType] = v
        tmpD['SGST'] = v if taxType == 'CGST' else 0

        # Gets the tax rate from the mappings table for the tax column in key (k)
        # and validates that it is a standard tax rate
        multiplier = 2 if taxType == 'CGST' else 1
        taxRate = int(queryDf(dfMappings, 'Column Name', k, 'Percent Tax').values.sum() * multiplier)
        verifyTaxrate(taxRate)
        
        # Computes the custom coding based on taxType 
        code = 'IS' if taxType == 'IGST' else ''
        GSTCode = transactionType[0].upper() + code + ' ' + str(taxRate) + '%'
      
        # Adds the result in the outputList
        outputList.append([tmpD, taxRate, GSTCode])

    outputList = getLedger(df, dfMappings, row, outputList)

    return outputList

def getTaxes(df, row, dfMappings, transactionType):
    #Gets tax columns in a dict
    taxDict = getTaxDict(df, dfMappings, row)
    
    if checkPreConditions(taxDict) is None:
        return
    elif len(taxDict['IGST']) > 0:
        return computeTaxes(taxDict['IGST'].items(), 'IGST', df, row, dfMappings, transactionType)
    else:
        return computeTaxes(taxDict['CGST'].items(), 'CGST', df, row, dfMappings, transactionType)

def convertData(df, dfMappings, transactionType):
    outputRows, counter = {}, 0
    for index, row in df.iterrows():
        iter = getTaxes(df, row, dfMappings, transactionType)

        if iter is None:
            continue
        else:
            for i in iter:
                tmpRow = {}
                
                taxes, taxRate, GSTCode, ledger = i[0], i[1], i[2], i[3]
                totalTaxes = sum(taxes.values())
                
                tmpRow.update(add_metadata(row))
                tmpRow['Taxable value'] = totalTaxes*100/int(taxRate)
                tmpRow.update(taxes)
                tmpRow['GST Code'] = GSTCode
                tmpRow['Ledger'] = ledger
                
                outputRows[counter] = tmpRow
                counter += 1

    output_df = pd.DataFrame(outputRows).transpose()

    return output_df


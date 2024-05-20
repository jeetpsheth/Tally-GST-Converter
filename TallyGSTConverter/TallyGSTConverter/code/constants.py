output_columns= ["Code", "Invoice Date", "Name of Party", "Invoice No.", "GSTTin No.", "Taxable value", "IGST", "CGST", "SGST", "GST Code",  "Tax Rate", "Diffence", "Ledger"]

columns_map =  {
    'Date': 'Invoice Date',
    'Particulars': 'Name of Party',
    'Voucher No.': 'Invoice No.',
    'GSTIN/UIN': 'GSTTin No.'
}

taxRates = [3, 5, 12, 18, 28]

taxtypes = ['IGST', 'CGST', 'SGST']
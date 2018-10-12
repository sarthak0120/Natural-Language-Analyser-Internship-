def main(username):
    
    ######## LOADING PHASE ########
    
    import pyodbc
    import pandas as pd
    import numpy as np
    
    conn = pyodbc.connect(r'DRIVER={SQL Server};'
                        r'SERVER=54.149.222.178;'
                        r'DATABASE=shrofile_survey_updated;'
                        r'UID=root;'
                        r'PWD=shrofile27')
    
    
    expMathMatrix = pd.read_sql('SELECT * FROM shrofile_survey_updated.SARTHAK_expMathMatrix', conn)
    expMathMatrix = expMathMatrix.get_values()
    
    expandedWordsList = pd.read_sql('SELECT DISTINCT(word) FROM shrofile_survey_updated.SARTHAK_expMathMatrix', conn)
    expandedWordsMap = {}
    for index, row in expandedWordsList.iterrows():
        expandedWordsMap[row[0]] = index
    
    numDims = pd.read_sql('SELECT COUNT(*) FROM shrofile_survey_updated.`SARTHAK_Dimensions List`', conn)
    numDims = numDims.get_values()[0,0]
    
    #### REPLACE WITH ORIGINAL DATABASE OF USERS LOCALLy ON SERVER ####

    data = pd.read_csv(r'C:\Users\Alka\Desktop\Shrofile Internship\userDatabase.csv')
    
    ######## CALCULATION PHASE ########
    
    userVibe = np.zeros((numDims, 2),np.float64)
    wordPower = {}  
    familyPower = {}
    family2Power = {}
    totalPower = {}
    
    wordFreq = {}
    wordCount = 0
    
    for index, row in data.iterrows():
        if (row[0].lower() == username.lower()):
            
            ## WORD FREQUENCIES ##
            wordCount = wordCount + 1
            if (row[2].lower() not in wordFreq.keys()):
                wordFreq[row[2].lower()] = 1
            else:
                wordFreq[row[2].lower()] = wordFreq[row[2].lower()] + 1
            
            ## WORD POWER ##
            if (row[2].lower() not in wordPower.keys()):
                wordPower[row[2].lower()] = row[3]
            else:
                wordPower[row[2].lower()] = wordPower[row[2].lower()] + row[3]            
            
            ## FAMILY POWER ##
            if (row[4].lower() not in familyPower.keys()):
                familyPower[row[4].lower()] = row[3]/2
            else:
                familyPower[row[4].lower()] = familyPower[row[4].lower()] + row[3]/2
            
            ## FAMILY 2 POWER ##    
            if (row[5].lower() not in family2Power.keys()):
                family2Power[row[5].lower()] = row[3]/4
            else:
                family2Power[row[5].lower()] = family2Power[row[5].lower()] + row[3]/4
            

                
    ## WORD CLOUD ##
    for index, row in data.iterrows():
        if (row[0].lower() == username.lower()):
            if (row[2].lower() not in totalPower.keys()):
                totalPower[row[2].lower()] = wordPower[row[2].lower()] + familyPower[row[4].lower()] + family2Power[row[5].lower()]
            else:
                continue
            
    ## VIBE CHART ##
    for key in wordFreq.keys():
        for i in range(numDims):
            userVibe[i,0] = userVibe[i,0] + float(wordFreq[key]/wordCount)*(expMathMatrix[numDims*(expandedWordsMap[key]) + i, 2])
            userVibe[i,1] = userVibe[i,1] + float(wordFreq[key]/wordCount)*(expMathMatrix[numDims*(expandedWordsMap[key]) + i, 3])

    return {'VibeChart': userVibe, 'wordCloud': totalPower}


main('neha')
#%%
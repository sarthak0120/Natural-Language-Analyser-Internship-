import pandas as pd
import numpy as np
import csv
import pyodbc

conn = pyodbc.connect(r'DRIVER={SQL Server};'r'SERVER=54.149.222.178;'r'DATABASE=shrofile_survey_updated;'r'UID=root;'r'PWD=shrofile27')

#%%
pathApp = r'C:\Users\Alka\Desktop\Shrofile Internship\Appraisers.csv' 
appraisers = pd.read_csv(pathApp)
colsToKeep = ['user_id', 'word', 'dim_id', 'score', 'liked']
appraisers = appraisers[colsToKeep]

#pathWords = r'C:\Users\Sarthak\Desktop\Shrofile Internship\Core Words List.csv'
#coreWords = pd.read_csv(pathWords)
coreWords = pd.read_sql('SELECT * FROM shrofile_survey_updated.`SARTHAK_Core Words List`;',conn)

#pathDimensions = r'C:\Users\Sarthak\Desktop\Shrofile Internship\Dimensions List.csv'
#dimensions = pd.read_csv(pathDimensions)
dimensions = pd.read_sql('SELECT * FROM shrofile_survey_updated.`SARTHAK_Dimensions List`;',conn) 

#%%

dimMap = {}
for index, row in dimensions.iterrows():    #maps dimension number to its name
    if index<16:
        dimMap[row[0]] = row[1] + " vs " +  row[2]
    else:
        dimMap[row[0]] = row[1]

wordMap ={}
wordMapInverse = {}

for index, row in coreWords.iterrows():
    wordMap[row[1]] = int(row[0])   #maps every words to its number from file
    wordMapInverse[row[0]] = row[1] #maps number of word to word

Appraisers = set([])
for index, row in appraisers.iterrows():
    if row[4] == 1:
        Appraisers.add(row[0])
        
numAppraisers = max(Appraisers)
numWords = len(wordMap)
numDims = len(dimMap)

#%%    
scoreMatrix = np.zeros((numDims,numAppraisers,numWords), 'int64') #dimensions*appraisers*corewords
for i in range(numAppraisers):
    for j in range(numWords):
        for k in range(numDims):
            scoreMatrix[k,i,j] = -10 #coreMatrix has -10 to imply unentered values
for index, row in appraisers.iterrows():
    if row[4] == 1:
        scoreMatrix[row[2]-1, row[0]-1, wordMap[row[1]]-1]= row[3]
    
#%%

mathMatrix = np.zeros((3,numWords,numDims), np.float64) #Mean in 0, Variance in 1, Count in 2

for i in range(numWords):
    for j in range(numDims):
        user_sum = 0
        user_count = 0
        for k in range(numAppraisers):         #calculates mean over k=98 appraisers
            if scoreMatrix[j,k,i]!= -10:
                user_sum = user_sum + scoreMatrix[j,k,i]        
                user_count = user_count +1
        if user_count!=0:
            mathMatrix[0,i,j] = float(user_sum)/user_count
            mathMatrix[2,i,j] = user_count

for i in range(numWords):
    for j in range(numDims):
        square_diff = 0
        user_count = 0
        for k in range(numAppraisers):     #calculates variance over k=98 appraisers using means from above
            if scoreMatrix[j,k,i]!= -10:
                square_diff = square_diff + (scoreMatrix[j,k,i]-mathMatrix[0,i,j])**2        
                user_count = user_count +1
        if user_count!=0:
            mathMatrix[1,i,j] = float(square_diff)/user_count

#%%

pathExpWords = r'C:\Users\Alka\Desktop\Shrofile Internship\Expanded Words List.csv' #### CHANGE TO SERVER LOCAL ADDRESS ###
expandedWords = pd.read_csv(pathExpWords)
#expandedWords = pd.read_sql('SELECT * FROM shrofile_survey_updated.`SARTHAK_Expanded Words List`',conn)

expandedWordsMap = {}
expandedWordsMapInverse = {}

for index, row in expandedWords.iterrows() :
    expandedWordsMap[row[0]] = index+1
    expandedWordsMapInverse[index +1] = row[0]
    
numExpWords = len(expandedWordsMap)

pathExpWords = r"C:\Users\Sarthak\Desktop\Shrofile Internship\Expanded Words.csv"
expandedWords = pd.read_csv(pathExpWords)
#expandedWords = pd.read_sql("SELECT * FROM shrofile_survey_updated.`SARTHAK_Expanded Words`;",conn)

#%%

####### UNAPPRAISED SECTION ##########

unappraised = pd.read_csv(r'C:\Users\Sarthak\Desktop\Shrofile Internship\Unappraised.csv')
unappraisedMap = {}
for index, row in unappraised.iterrows():
    unappraisedMap[row[0]] = index + 1

numUnappraised = len(unappraisedMap)

for index, row in expandedWords.iterrows():
    if (row[1] in unappraisedMap.keys()):
        continue
    if (row[4] in unappraisedMap.keys()):
        for i in range(numDims):
            mathMatrix[0, wordMap[row[4]] -1, i] = mathMatrix[0,wordMap[row[4]] -1, i] + mathMatrix[0,wordMap[row[1]]-1,i]
            mathMatrix[1, wordMap[row[4]] -1, i] = mathMatrix[1,wordMap[row[4]] -1, i] + mathMatrix[1,wordMap[row[1]]-1,i]
            mathMatrix[2, wordMap[row[4]] -1, i] = mathMatrix[2,wordMap[row[4]] -1, i] + 1
        
for index, row in unappraised.iterrows():
    for i in range (numDims):
        if mathMatrix[2, wordMap[row[0]]-1, i]!=0:
            mathMatrix[0, wordMap[row[0]] -1, i] = mathMatrix[0, wordMap[row[0]] -1, i]/ mathMatrix[2, wordMap[row[0]]-1, i]
            mathMatrix[1, wordMap[row[0]] -1, i] = mathMatrix[1, wordMap[row[0]] -1, i]/ mathMatrix[2, wordMap[row[0]]-1, i]


with open("mathMatrix.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["word", "dim_id", "avg", "var", "count"])
    for word_index in range(numWords):
        for dim_index in range(numDims):
            writer.writerow([wordMapInverse[word_index+1], dim_index +1, mathMatrix[0,word_index, dim_index],mathMatrix[1,word_index, dim_index],mathMatrix[2,word_index, dim_index]])


#%%
expMathMatrix = np.zeros((2, numExpWords, numDims), np.float64)

###########    MEANS    #############

count = np.zeros(numExpWords, dtype=np.float64)

for index, row in expandedWords.iterrows():
    count[expandedWordsMap[row[4]]-1] = count[expandedWordsMap[row[4]]-1] + 1
    for i in range(numDims):
        expMathMatrix[0,expandedWordsMap[row[4]]-1,i] = expMathMatrix[0,expandedWordsMap[row[4]]-1,i] + (row[5]/3)*mathMatrix[0,wordMap[row[1]]-1,i]

for i in range(numExpWords):
    for j in range(numDims):
        expMathMatrix[0,i,j] = expMathMatrix[0,i,j]/count[i]

###########   VARIANCE    #############

square_diff = np.zeros((numExpWords, numDims), np.float64)
user_count = np.zeros((numExpWords),np.float64)

for index, row in expandedWords.iterrows():
    for i in range(numDims):
        for k in range(numAppraisers):     #calculates variance over k=98 appraisers using means from above
            if scoreMatrix[i,k,wordMap[row[1]]-1]!= -10:
                square_diff[expandedWordsMap[row[4]]-1, i] = square_diff[expandedWordsMap[row[4]]-1, i] + (abs(row[5])/3)*(scoreMatrix[i,k,wordMap[row[1]]-1]-expMathMatrix[0,expandedWordsMap[row[4]]-1,i])**2        
                user_count[expandedWordsMap[row[4]]-1] = user_count[expandedWordsMap[row[4]]-1] +1

for i in range(numExpWords):
    if user_count[i]!=0:
        for j in range(numDims):
            expMathMatrix[1,i,j] = square_diff[i,j]/user_count[i]


#%%
######### PRINTING TO CSV ###########
            
with open("expMathMatrix.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["word","dim_id","avg","var"])
    for word_index in range(numExpWords):
        for dim_index in range(numDims):
            writer.writerow([expandedWordsMapInverse[word_index+1],dimMap[dim_index+1],expMathMatrix[0,word_index, dim_index],expMathMatrix[1,word_index, dim_index]])
        

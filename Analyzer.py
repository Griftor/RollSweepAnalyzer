import pandas as pd
from datetime import datetime
from datetime import timedelta
import os
import sys

if len(sys.argv) < 3:
    print("USAGE: %s inputfolder threshold" % (sys.argv[0]))
    sys.exit(1)

input_folder = sys.argv[1]
threshold = sys.argv[2]


def toDateTime(myString):
    return datetime.strptime(myString, '%Y-%m-%d %H:%M:%S.%f')


# Grab the next ten seconds after some event, and return it in a dataframe
def GetTenSeconds(bigdataframe, index):
    ten_sec_dataframe = pd.DataFrame()
    currentTime = toDateTime(str(bigdataframe.iloc[index].get('CT')))
    t_plus_ten = currentTime + timedelta(seconds=10)
    while(currentTime < t_plus_ten):
        thisRow = bigdataframe.iloc[index]
        if(index > bigdataframe.size):
            break
        index += 1
        currentTime = toDateTime(str(thisRow.get('CT')))
        ten_sec_dataframe = ten_sec_dataframe.append(thisRow)

    return ten_sec_dataframe

# Output information from a 10-second dataframe
def PrintFrames(dataframe, num):
    initial_time = toDateTime(dataframe.iloc[0].get('CT'))
    second_trade_time = toDateTime(dataframe.iloc[1].get('CT'))
    reaction_time = second_trade_time - initial_time
    initial_size = (dataframe.iloc[0].get('Size'))
    initial_price = (dataframe.iloc[0].get('Price'))

    end_price = dataframe.iloc[-1].get('Price')

    print("Trade at ", str(initial_time))
    print('\tSize: ', initial_size)
    print('\tReaction Time: ', str(reaction_time))
    print('\tPrice: ', initial_price)
    print('\tEnd Price: ', str(end_price))
    print('\tNumber of Trades (10s): ', str(dataframe.size))
    print('\n\n')

# START OF MAIN()
pd.set_option('display.expand_frame_repr', False)
fulldf = pd.DataFrame()

# Read in all the files, stick them in one big dataframe
for csv_file in os.listdir(input_folder):
    df = pd.read_csv(input_folder + "\\" + csv_file, header=None, names=['CT', 'ST', 'Seq', 'Type', 'Market',
                                                                                  'Price', 'Size', 'Feed_Type', 'Side'])
    tradedf = df[df['Type'] == 'T']
    fulldf = fulldf.append(tradedf)


fulldf = fulldf.drop(labels=['ST', 'Seq', 'Type', 'Side', 'Market', 'Feed_Type'], axis=1)
print('Read in the Data')
fulldf = fulldf.reset_index()

# So now find the instances where trading volume exceeded the threshold
for index, row in fulldf.iterrows():
    vol_of_trade = row.get('Size')
    if(int(vol_of_trade) > int(threshold)):
        # Gonna want to make a function to show the next ten minutes, I'd say
        PrintFrames(GetTenSeconds(fulldf, index), index)

#Looks for leap weeks for a regular week calendar based on the
#proximity of mid-year from North solstices.
#We want a regular patter of the form a/b: (a*year+delta) % b < a 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ephem
import calendar
from dateutil.easter import *
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


#calendar.prmonth(2016,2)
#calendar.prcal(2016)



year0 = 1382 #first in this cycle
yeare = 2750 #not in this cycle
length = yeare-year0 #length of the cycle

#franction a/b for the regular patern
#a = 71
#b = 400

#convergents
#a = 36
#b = 203

#a = 47
#b = 265

#a = 58
#b = 327

#a = 69
#b = 389

a = 127
b = 716



#s = ephem.next_winter_solstice('2016')
#print(s)
#s % 7

#ephem.date('2016-03-03') % 7

#length of the period of astronomical calculations
solsticeday =  np.zeros(length+1)
solsticewday =  np.zeros(length+1)
leapyear = np.zeros(length, dtype=bool)
year = np.arange(year0,year0+length, dtype=int)

for i in range(length+1):
    
    s = ephem.next_summer_solstice(str(year0+i))
    solsticeday[i] = s.tuple()[2]
    solsticewday[i] = s % 7


#ephem.date is 0.5 on Monday 0H and 4 on Thursday 12H
for i in range(length):   
    if solsticewday[i+1]>=4 and solsticewday[i]<4:
        leapyear[i]='True'
        
    
    
WSleapweeks = pd.concat([pd.DataFrame(year),
                         pd.DataFrame(leapyear),
                         pd.DataFrame(solsticewday[0:length]),
                         pd.DataFrame(solsticewday[1:]),
                         pd.DataFrame(solsticeday[0:length]),
                         pd.DataFrame(solsticeday[1:])],axis=1)
                         
WSleapweeks.columns = ['year',
                       'leapyear',
                       'prevSolsticeWday',
                       'postSolsticeWday',
                       'prevSolstice',
                       'postSolstice']

leaplist = WSleapweeks[WSleapweeks.leapyear==True].year



#search for a regular pattern for this data

difftopattern = np.zeros(b, dtype=int)

for delta in range(b):
  
     pattern = (a*(np.arange(0,length)+year0)+delta) % b < a 
     difftopattern[delta] = sum(WSleapweeks.leapyear != pattern)



#plt.hist(difftopattern, bins=25)
mindiff = min(difftopattern)
print(mindiff)
delta = np.argmin(difftopattern)
print(delta)
#for 127/716 and delta = 160 1382-2749




pattern = (a*(np.arange(0,length)+year0)+delta) % b < a
sum(pattern != WSleapweeks.leapyear)
difftopatternbool = WSleapweeks.leapyear != pattern
WSleapweeks.year[WSleapweeks.leapyear != pattern]


#test
(a*y+delta) % b < a

y = np.arange(0,33,dtype=int)
(a*y + 0) % b < a


#date converter

imputdate = (2016,3,17)

def datetoWeekcal(imputdate):

    a = 127
    b = 716
    
    delta = 160
    
    pattern = (a*np.arange(1382,2750)+delta) % b < a

    imputfromEpoch = ( ephem.Date(imputdate)-ephem.Date((1381,12,16)) ) % 261513
    #16 dec 1381, mon post-near to solstice   
    #ephem.next_summer_solstice(str(1382))%7 = 5.2324 ; 13 jun-> mon 16 jun - 182d 
    
    cycles = ( ephem.Date(imputdate)-ephem.Date((1381,12,16)) ) // 261513

    weeksfromEpoch = imputfromEpoch // 7
    weekday = imputfromEpoch % 7 + 1

    accumleaps = np.append(0,np.cumsum(pattern+52))

    yearWcalincycle = np.argmax(accumleaps>weeksfromEpoch) - 1

    weeknWcal = weeksfromEpoch - accumleaps[yearWcalincycle]


    if pattern[yearWcalincycle]==False:
        seasonWcal=np.argmax(np.array([13,26,39,52])>weeknWcal)
        weekWcal = weeknWcal-np.array([0,13,26,39])[seasonWcal]
        weekWcal = weekWcal+1
    else:
        seasonWcal=np.argmax(np.array([13,26,40,53])>weeknWcal) 
        weekWcal = weeknWcal-np.array([0,13,26,40])[seasonWcal]
        if seasonWcal!=2:
            weekWcal = weekWcal+1 #Season 3 starts with week 0, the rest in 1

   
    date = (int(yearWcalincycle + 1382 + cycles * 716),
            seasonWcal+1,
            int(weekWcal),
            int(weekday))
            
    print "%s-S%sW%s-%s" % (date[0],date[1],date[2],date[3])

    return(date)




datetoWeekcal((2016,3,17))

#easter date to week calendar
easterweek = np.zeros(b, dtype=int)
for i in range(b):
    easterweek[i] = datetoWeekcal(easter(2000+i))[2]
    if easterweek[i]==13: easterweek[i]=0


fig = plt.figure(figsize=(50,2), dpi=480)
ax = fig.add_subplot(111)
majorLocator   = MultipleLocator(10)
majorFormatter = FormatStrFormatter('%03d')
minorLocator   = MultipleLocator(1)
ax.xaxis.set_major_locator(majorLocator)
ax.xaxis.set_major_formatter(majorFormatter)
ax.xaxis.set_minor_locator(minorLocator)
ax.plot(easterweek, ',', c='black')
ax.axes.set_ylim([-0.5,5.4])
plt.show()


plt.hist(easterweek, bins=20)

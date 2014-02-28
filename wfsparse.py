import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib.dates as md
import datetime

def colsplit(l, cols):
    rows = len(l) / cols
    if len(l) % cols:
        rows += 1
    m = []
    for i in range(rows):
        m.append(l[i::rows])
    return m

def split_seq(seq, numpieces):
    seqlen = len(seq)
    d, m = divmod(seqlen, numpieces)
    rlist = range(0, ((d + 1) * (m + 1)), (d + 1))
    if d != 0: rlist += range(rlist[-1] + d, seqlen, d) + [seqlen]

    newseq = []
    for i in range(len(rlist) - 1):
        newseq.append(seq[rlist[i]:rlist[i + 1]])

    newseq += [[]] * max(0, (numpieces - seqlen))
    return newseq
    
def date_range(start, end):
    r = (end+datetime.timedelta(minutes=10)-start).days
    return [start+datetime.timedelta(days=i) for i in range(r)]
#########

#xmlfile = raw_input("Enter file name: ")
xmldata = ET.parse('wfs.xml')

root = xmldata.getroot()

starttime = root[0][0][0][0][0].text
endtime = root[0][0][0][0][1].text
analysistime = root[0][0][1][0][0].text

starttime = datetime.datetime.strptime(starttime, "%Y-%m-%dT%H:%M:%SZ")+datetime.timedelta(hours=2)
endtime = datetime.datetime.strptime(endtime, "%Y-%m-%dT%H:%M:%SZ")+datetime.timedelta(hours=2)
#timeList = date_range(starttime, endtime)

location = root[0][0][5][0][0][0][0][0][1].text
geoid = root[0][0][5][0][0][0][0][0][0].text
latlon = root[0][0][5][0][1][0][0][0][1].text

times = root[0][0][6][0][0][0][0].text
data = root[0][0][6][0][1][0][1].text
times = [float(x) for x in times.split()]
data=[float(x) for x in data.split()]

al=len(times)/3

dt = np.asarray(split_seq(times,al))
d = np.asarray(split_seq(data,al))

utime = dt[:,2]
ttime = np.array([datetime.datetime.fromtimestamp(utime[i]) for i in xrange(len(utime))])+datetime.timedelta(hours=2)

geop, temp, pressure, hum, winddir, windspd, windu, windv, \
maxwind, windgust, dew, cloud, weather, lowcloud, medcloud, highcloud, \
preciph, precipt, radlw, radg, radnet = zip(*d)

fig = plt.figure()
fig.set_size_inches(11.7, 8.3)
ax1 = plt.subplot2grid((6, 1), (0, 0))
days = md.DayLocator()
hours = md.HourLocator(byhour=range(4,24,4))
plt.subplots_adjust(top=0.75)

daysfmt = md.DateFormatter('%a %d \n %B \n %H:00')
hourfmt = md.DateFormatter('%H:00')
ax1.xaxis.set_major_locator(days)
ax1.xaxis.set_minor_locator(hours)
ax1.xaxis.set_major_formatter(daysfmt)
ax1.xaxis.set_minor_formatter(hourfmt)
ax1.spines['bottom'].set_visible(False)
ax1.xaxis.set_ticks_position('top')
ax1.xaxis.grid(True)
#ax1.set_title('Weather Forecast \n Location: '+ location + ' at ' + analysistime + ' \n \n \n')
plt.text(0.5, 2.5, 'Weather Forecast \n Location: '+ location + ' issued at ' + analysistime + \
         '\n All times are EET (local) unless specified', 
         horizontalalignment='center',
         fontsize=12,
         transform = ax1.transAxes)
#plt.text(0.5, 1, figure_title, horizontalalignment='center', 
#        fontsize=20, transform = ax1.transAxes)


#Plot cloud
plt.subplots_adjust(hspace=0.3)
ax1.fill_between(ttime, np.array(lowcloud)/200+1, -np.array(lowcloud)/200+1, 
                 color='grey',interpolate=True,edgecolor='none')
ax1.fill_between(ttime, np.array(medcloud)/200+2, -np.array(medcloud)/200+2, 
                color='darkgrey',interpolate=True,edgecolor='none')
ax1.fill_between(ttime, np.array(highcloud)/200+3, -np.array(highcloud)/200+3, 
                 color='lightgrey',interpolate=True, edgecolor='none')
labels = [1, 2, 3]
y = [1,2,3]
ax1.set_ylabel('Cloud')
ax1.set_yticks((1,2,3))
ax1.set_yticklabels(('Low','Medium','High'))
ax1.xaxis.grid(b=True, which='major', color='k', linestyle='-')
ax1.xaxis.grid(b=True, which='minor', color='k', linestyle='--')


#Plot temperature
ax2 = plt.subplot2grid((6, 1), (1, 0), rowspan=2)
ax2.set_xlim(starttime, endtime)
ax2.set_ylim(-40,5)
wind_chill = 13.12 + 0.6215*np.array(temp) - (11.37*(3.6*np.array(windspd))**0.16) \
              + 0.3965*np.array(temp)*((3.6*np.array(windspd)))**0.16
temp = ax2.plot(ttime, temp, linewidth=2, label='True Temp')
windchl = ax2.plot(ttime, wind_chill, 'b-.', linewidth=2,label='Apparent Temp')
ax2.legend(loc=0,prop={'size':8})
ax2.set_ylabel('Temperature (oC)')
ax2.xaxis.set_major_locator(days)
ax2.xaxis.set_minor_locator(hours)
ax2.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.set_xticklabels([])
ax2.xaxis.grid(b=True, which='major', color='k', linestyle='-')
ax2.xaxis.grid(b=True, which='minor', color='k', linestyle='--')

#Plot humidity
hum_ax=ax2.twinx()
hum_ax.plot(ttime, hum, linewidth=2, color='r', label='Humidity')
hum_ax.set_ylim(0,100)
hum_ax.text(1.05,0.5, 'Humidity (%)',
        horizontalalignment='center',
        verticalalignment='center',
        rotation='vertical',
        transform=hum_ax.transAxes)

hum_ax.legend(loc=4,prop={'size':8})

#4th axis, plot wind
ax4 = plt.subplot2grid((6,1),(3,0),rowspan=2)
ax4.spines['bottom'].set_visible(False)
ax4.spines['top'].set_visible(False)
ax4.xaxis.set_major_locator(days)
ax4.xaxis.set_minor_locator(hours)
ax4.set_xticklabels([])
ax4.set_ylabel('Wind (m/s)')
ax4.stackplot(ttime, windspd, maxwind)
p1 = plt.Rectangle((0, 0), 1, 1, fc="green")
p2 = plt.Rectangle((0, 0), 1, 1, fc="blue")
plt.legend([p1, p2], ['Max Wind', 'Wind'],loc=0,prop={'size':8})
ax4.set_ylim(bottom=0)
ax4.xaxis.grid(b=True, which='major', color='k', linestyle='-')
ax4.xaxis.grid(b=True, which='minor', color='k', linestyle='--')


wind_ax = ax4.twiny()
y_loc=np.ones(len(ttime))+3
wind_ax.quiver(utime[1::6],y_loc[1::6],windu[1::6],windv[1::6],pivot='middle',width=0.005, color='white')
wind_ax.set_xlim(min(utime),max(utime))
wind_ax.set_xticklabels([])
wind_ax.set_ylim(bottom=0)
wind_ax.xaxis.set_major_locator(days)
wind_ax.xaxis.set_minor_locator(hours)

#3rd axis
daysfmtb = md.DateFormatter('%H:00 \n %a %d \n %B ')
ax3 = plt.subplot2grid((6, 1), (5, 0),rowspan=1)
ax3.xaxis.set_major_locator(days)
ax3.xaxis.set_minor_locator(hours)
ax3.xaxis.set_major_formatter(daysfmtb)
ax3.xaxis.set_minor_formatter(hourfmt)
ax3.spines['top'].set_visible(False)
ax3.xaxis.grid(b=True, which='major', color='k', linestyle='-')
ax3.xaxis.grid(b=True, which='minor', color='k', linestyle='--')

#Plot precipitation
plt.bar(ttime, preciph, width=0.1, bottom=0, color='cornflowerblue',edgecolor='cornflowerblue')
ax3.set_xlim(starttime, endtime)
ax3.set_ylabel("Precip.\n(mm/hr)")
ax3.set_ylim(0,4)
ax3.set_yticks((0,2,4))


#plt.tight_layout()
#plt.show()
savename = raw_input("Specify Location, Hetta(H) or Valimaa (V):")
if (savename=='H'):
    plt.savefig('../Dropbox/Cape Lapland/Hetta_Forecast.pdf')
else:
    plt.savefig('Valimaa_Forecast.pdf')


        
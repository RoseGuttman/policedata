
from sodapy import Socrata
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from flask import request, redirect
import webbrowser, operator, jinja2, os, cgi, webapp2, logging
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Information at https://dev.socrata.com/foundry/data.seattle.gov/xurz-654a
# time stamp info https://dev.socrata.com/docs/datatypes/floating_timestamp.html#,

#This program creates content for the Neighborhood Crime Dashboard
#Data created:
#   1. Graph for number of crimes per year
#   2. Graph for Types of Crimes/Frequency
#   3. Graph for Crimes Numbers per month - 2018
#   4. Graph of Type of Crime for 2018
#   5. The most common crime in that neighborhood
#   6. Most common crime that year


test = "CENTRAL AREA/SQUIRE PARK"
import info


#Get crimes over the years
def plotCrime(data):
    timeDict = {}
    for dict in data:
        year = dict['occ_datetime'][0:4]
        if year not in timeDict.keys():
            timeDict[year] = 0
        timeDict[year] += 1
    return timeDict



#Get a dictionary of types of crimes and their frequencies
def plotTypes(data):
    typedict = {}
    for dict in data:
        if "crime_subcategory" in dict.keys(): #some dicts don't include a subcategory, these crimes are not included
            cat = dict["crime_subcategory"]
            if cat not in typedict.keys():
                typedict[cat] = 0
            typedict[cat] += 1
    return typedict



#Get most frequent crime from plotTypes
def mostCrime(dict):
    name = ""
    highest = 0
    for item in dict.keys():
        num = dict[item]
        if num > highest:
            name = item
            highest = num
    return name



#Get a list of the dictionaries of the crimes for a certain year
def yearList(data, year):
    list = []
    for dict in data:
        dictyear = dict['occ_datetime'][0:4]
        if dictyear == year:
            list.append(dict)
    return list


#Dictionary of months and number of crimes for that month
def yearDetails(data):
    yearDict = {"01": 0, "02": 0, "03": 0, "04": 0, "05": 0, "06": 0, "07": 0,
                "08": 0, "09": 0, "10": 0, "11": 0, "12": 0}
    for dict in data:
        date = dict["occ_datetime"][5:7]
        yearDict[date] += 1
    return  yearDict



#Create a bar graph from a dictionary
def barGraph(dict_data, label, title, fig):
    topic_nums = ()
    topic_names = ()
    for item in dict_data.keys():
        topic_nums = topic_nums + (dict_data[item],)
        topic_names = topic_names + (item,)

    y_pos = np.arange(len(topic_names))

    plt.barh(y_pos, topic_nums, align='center', alpha=0.5)
    plt.yticks(y_pos, topic_names, fontsize=8)
    plt.xlabel('Number of Crimes')
    plt.ylabel(label)
    plt.title(title)

    plt.savefig(fig)
    #plt.show()
    plt.close()




class MainHandler(webapp2.RequestHandler):
    def get(self):
        #print statements don't work well
        #print "In MainHandler"
        return

class GetData(webapp2.RequestHandler):
    def post(self):
        vals = {}
        vals['page_title'] = "Dashboard"
        name = self.request.get('neighborhood')
        sub = self.request.get('submit')
        logging.info(name)
        logging.info(sub)
        
        input = name.capatalize()
        
        client = Socrata('data.seattle.gov',app_token = info.token,username=info.username, password=info.password)
        results = client.get("xurz-654a", neighborhood = input, limit=100000000)

        # -1-
        yearlist = plotCrime(results)
        barGraph(yearlist, "Year", "Number of Crimes per Year", "all.png")

        # -2-
        crimelist = plotTypes(results)
        barGraph(crimelist, "Type", "Different Types of Crimes", "type.png")

        # -3-
        twenty_eighteen = yearList(results, "2018")
        yeardict = yearDetails(twenty_eighteen)
        barGraph(yeardict, "Month", "Number of Crimes per Month 2018", "18all.png")

        # -4-
        crime18dict = plotTypes(twenty_eighteen)
        barGraph(crime18dict, "Type", "Types of Crime in 2018", "18type.png")

        # -5-
        all = mostCrime(crimelist)

        # -6-
        now = mostCrime(crime18dict)

        crime = {"neighborhood": neighborhood, "allTime": all, "thisYear": now}

        file = open("dashboard.html", "w")
        template = JINJA_ENVIRONMENT.get_template('dashboardtemplate.html')
        file.write(template.render(crime))
        file.close()




application = webapp2.WSGIApplication([
                                      ('/getData', GetData),
                                      ('/.*', MainHandler)
                                      ],
                                     debug=True)

#encoding="utf-8"

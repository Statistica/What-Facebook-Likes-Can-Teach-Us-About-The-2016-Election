# Written by Jonathan Saewitz, released March 21st, 2016 for Statisti.ca
# Released under the MIT License (https://opensource.org/licenses/MIT)
# This code is far from perfect. I am sure that many changes can be made
# to make it more efficient. Feel free to create pull requests.

import requests, time, plotly.plotly as plotly, plotly.graph_objs as go, sys
from datetime import date, datetime, timedelta

########################
#        Config        #
########################

access_token="" #your facebook access token (obtain from https://developers.facebook.com/tools/explorer/)
facebookId="" #id of the facebook page you wish to analyze (e.g. 138691142964027)
name="" #name of the facebook page you wish to analyze (e.g. Ben Carson)

party="" #Democratic or Republican

num_days_to_analyze=0 #number of days to analyze (e.g. 30 analyzes the last 30 days of posts)

graph_title="" #title of the graph (e.g. "Ben Carson Facebook Likes Over Time")

x_axis_title="" #the x-axis title of the graph, e.g. "Date"
y_axis_title="" #the y-axis title of the graph, e.g. "Number of likes"

########################
#      End Config      #
########################

traces=[] #create a list of traces

if party.lower()=="democratic":
	polls=requests.get('http://elections.huffingtonpost.com/pollster/api/charts/2016-national-democratic-primary').json()['estimates_by_date']
elif party.lower()=="republican":
	polls=requests.get('http://elections.huffingtonpost.com/pollster/api/charts/2016-national-gop-primary').json()['estimates_by_date']
else:
	print "Party \"%s\" not found (party must be either \"Democratic\" or \"Republican\"), exiting..." % party
	sys.exit()

scoresList=[]
date_today=date.today() #get the current date
print "Currently analyzing %s..." % name
likesList=[] #create an empty list of likes
datesList=[] #create an empty list of dates

last_name=name.split(" ")[1]

for daysBehind in range(num_days_to_analyze): #begin looping for num_days_to_analyze
	active_date=date_today-timedelta(daysBehind) #the current date we're analyzing
												 #(today's date minus the number of days the loop has gone through)

	datesList.append(datetime.strftime(active_date, '%m/%d/%y')) #add the day we're currently analyzing to
																 #the dateslist and format it as 01/01/2000

	epoch_active_time=time.mktime(active_date.timetuple()) #get the epoch time of the active date
														   #because that's what facebook requires for
														   #obtaining posts by date

	active_time_behind=date_today-timedelta(daysBehind-1) #get the time of one day before the
														  #current time we're searching (so we're searching
														  #a one-day period)

	epoch_active_time_behind=time.mktime(active_time_behind.timetuple()) #convert the active_time_behind to epoch time

	#get the posts by page_id during the one-day-period we're searching:
	posts=requests.get('https://graph.facebook.com/v2.5/%s/posts?fields=id&since=%s&until=%s&access_token=%s' % (facebookId, epoch_active_time, epoch_active_time_behind, access_token)).json()['data']
	#the following code gets the total number of likes for page_id's posts that day
	#and averages them by the number of posts made by page_id that day:

	#initialize totalLikes and numPosts to 0:
	totalLikes=0
	for post in posts: #loop through every post
		#get the total likes of the post and add it to totalLikes
		totalLikes+=requests.get('https://graph.facebook.com/v2.5/%s/likes?summary=true&access_token=%s' % (post['id'], access_token)).json()['summary']['total_count']
	
	if len(posts)==0: #if there are 0 posts, the average number of likes is 0
					  #this prevents dividing by 0 to get the average
		average_likes=0
	else: #if there aren't 0 posts:
		average_likes=totalLikes/len(posts) #get the average number of likes

	#add the average number of likes to likesList
	likesList.append(average_likes)
	dataAvailable=False

	#get polling data for current date
	for poll in polls: #there is most certainly a better way to do this
		estimates=poll['estimates']
		for estimate in estimates:
			if estimate['choice']==last_name:
				if(poll['date']==datetime.strftime(active_date, '%Y-%m-%d')):
					dataAvailable=True
					scoresList.append(estimate['value'])
					# print estimate['value']
	if not dataAvailable:
		scoresList.append(None)

	if daysBehind%20==0: #counter so we can keep track of how many posts we've analyzed so far
						 #(updates us every 20 posts)
		print "Done %s days..." % daysBehind

traces.append(go.Scatter(x=datesList, y=likesList, name=name)) #append the current analysis to traces
traces.append(go.Scatter(x=datesList, y=scoresList, name="Polling average")) #append the current analysis to traces

#create the graph's layout
layout=go.Layout(
	title=graph_title,
	xaxis=dict(
		title=x_axis_title,
		titlefont=dict(
			family='Courier New, monospace',
			size=18,
			color='#7f7f7f'
		),
		autorange='reversed'
	),
	yaxis=dict(
		title=y_axis_title,
		titlefont=dict(
			family='Courier New, monospace',
			size=18,
			color='#7f7f7f'
		)
	)
)

data=go.Data(traces)
fig=go.Figure(data=data, layout=layout) #create the figure
plotly.plot(fig) #create the graph!

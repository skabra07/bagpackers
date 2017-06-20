from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import googlemaps
import requests
import datetime
import json
import time
import sys

def index(request):
    context = {'name': 'index'}
    return render(request, "index.html", context)

def search(request):
    # Get the data
    origin = request.GET['origin']
    destination = request.GET['destination']
    mode = request.GET['mode']
    intervalType = request.GET['criteria']
    interval = int(request.GET['interval'])
    date_string = request.GET['date']
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    currency = "EUR"

    # ==========================================================================
    # Google Map API
    # Search for the directions and divide it by steps
    # ==========================================================================
    GOOGLE_API_KEY = 'AIzaSyCLrrpO2bvQQcjOr13zBbAfX4fYU8q2MME'

    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    '''
    the following inputs are required from the user as the format and type stated
        string mode = string "walking" or "driving"
        string intervalType = string "time" or "distance"

        string origin is input from user. It is the name of a city
        string destination is input from user. It is the name of a city
    '''

    departureTime = datetime.datetime.now()

    res = requests.get("https://maps.googleapis.com/maps/api/directions/json?origin="+origin+"&destination="+destination+"&mode="+mode+"&key="+GOOGLE_API_KEY)
    jsonOfRes = res.json()

    waypoints = []
    waypointCoords = []

    # if they want to split by distance
    if intervalType == "distance":
        distanceFromWaypoint = 0

        # distance is measured in metres
        distanceInterval = interval * 1000

        # add waypoints after every interval of distance
        for step in range(len(jsonOfRes[u'routes'][0][u'legs'][0][u'steps'])):
            distanceFromWaypoint += jsonOfRes[u'routes'][0][u'legs'][0][u'steps'][step][u'distance'][u'value']

            if distanceFromWaypoint >= distanceInterval:
                waypoints.append(jsonOfRes[u'routes'][0][u'legs'][0][u'steps'][step+1])
                distanceFromWaypoint = 0

    # if they want to split by time
    if intervalType == "time":
        timeFromWaypoint = 0

        # time is measured in seconds
        timeInterval = interval * 3600

        # add waypoints after every interval of distance
        for step in range(len(jsonOfRes[u'routes'][0][u'legs'][0][u'steps'])):
            timeFromWaypoint += jsonOfRes[u'routes'][0][u'legs'][0][u'steps'][step][u'duration'][u'value']

            if timeFromWaypoint >= timeInterval:
                waypoints.append(jsonOfRes[u'routes'][0][u'legs'][0][u'steps'][step+1])
                timeFromWaypoint = 0

    # store coordinates of each waypoint
    for point in range(len(waypoints)):
        coordinates = {} #to hold latitude and longitude
        coordinates['lat'] = waypoints[point][u'start_location'][u'lat']
        coordinates['long'] = waypoints[point][u'start_location'][u'lng']
        coordinates['time'] = waypoints[point][u'duration'][u'value']
        # Get stop name from Google Api
        res1 = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(waypoints[point][u'start_location'][u'lat'])+","+str(waypoints[point][u'start_location'][u'lng'])+"&key="+GOOGLE_API_KEY)
        jsonOfRes1 = res1.json()
        coordinates['name'] = jsonOfRes1[u'results'][1][u'formatted_address']

        waypointCoords.append(coordinates)

    # convert coordinates to json
    jsonCoords = json.dumps({"waypoints":waypointCoords})

    # get coordinates back from json file
    jsonOfCoords = json.loads(jsonCoords)

    parsedWaypoints = []

    for waypoint in range(len(jsonOfCoords['waypoints'])):
        parsedWaypoints.append(jsonOfCoords['waypoints'][waypoint])

    # return HttpResponse(str(jsonOfCoords['waypoints']))

    # ==========================================================================
    # Skyscanner API
    # Search for flight
    # ==========================================================================
    API = "ha348334469154725681039185711735"
    url = "http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/GB/{}/EN/?query={}&apikey={}"

    start = origin
    dest = destination
    depature_date = date_string
    end_date = date + datetime.timedelta(days=1)
    arrival_date = end_date.strftime("%Y-%m-%d")
    cur = currency

    # location_start = json.loads(requests.get(url.format(cur,start, API)).text)
    # location_id_start = location_start["Places"][0]['CityId']
    #
    # location_dest = json.loads(requests.get(url.format(cur,dest, API)).text)
    # location_id_dest = location_dest["Places"][0]['CityId']
    # #print ("LOCATIONS")
    # #print (json.dumps(locations,indent = 4))
    #
    # url_2 = "http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/GB/{}/en-GP/{}/{}/{}/{}?apiKey={}"
    # prices = json.loads(requests.get(url_2.format(cur,location_id_start, location_id_dest, depature_date, arrival_date, API)).text)
    #
    # msg = ""
    # mincost = []
    # for x in range(0,len(prices["Quotes"])):
    #     mincost.append([x,prices["Quotes"][x]['MinPrice']])
    # if not mincost:
    #     msg = "No flights found"
    #
    # car = []
    # for x in range(0,len(prices["Carriers"])):
    #     car.append(prices["Carriers"][x]['CarrierId'])
    #     car.append(prices["Carriers"][x]['Name'])
    #
    # info = input('For more info on the flight enter the reference number of the price: ')
    # if 'OutboundLeg' in prices["Quotes"][int(info)]:
    #     p = prices["Quotes"][int(info)]['OutboundLeg']['CarrierIds']
    # else:
    #     p = prices["Quotes"][int(info)]['InboundLeg']['CarrierIds']
    #
    # carrier_find = car.index(p[0])
    # carrier = car[carrier_find+1]

    #print(json.dumps(prices["Quotes"][int(info)],indent = 4))
    # print ("\nMore information for flight from %s to %s:" % (start, dest))
    # print("Depature Date: %s"%(depature_date))
    # print("Return Date: %s"%(arrival_date))
    # print("Direct: %s"%(prices["Quotes"][int(info)]['Direct']))
    # print("Price: %s %s "%(cur, mincost[int(info)][1]))
    # print("Airlines: %s"%carrier)

    # flight_direct = prices["Quotes"][int(info)]['Direct']
    # flight_price = mincost[int(info)][1] + cur
    # flight_airlines = carrier

    # ==========================================================================
    # Skyscanner API
    # Search for hotels in each step of the trip
    # ==========================================================================
    # hotels = {}

    hotels = []
    stops = []
    counter = 0
    for point in range(len(parsedWaypoints)):

        lat = ("%.2f" % parsedWaypoints[point][u'lat'])
        lng = ("%.2f" % parsedWaypoints[point][u'long'])
        time = ("%d" % parsedWaypoints[point][u'time'])
        name = parsedWaypoints[point][u'name']

        entityid=lat+","+lng+"-latlong"
        checkindate= date + datetime.timedelta(days=counter)
        checkoutdate= checkindate + datetime.timedelta(days=1)
        counter += 1
        guests = 1
        rooms = 1

        URL= "http://partners.api.skyscanner.net/apiservices/hotels/liveprices/v2/UK/{}/en-GB/{}/{}/{}/{}/{}?apiKey={}&pageSize=20"
        res = requests.get(URL.format(cur, entityid, checkindate, checkoutdate, guests, rooms, API))

        session = "http://partners.api.skyscanner.net" + res.headers['location']

        filt = requests.get(session + "&price={}".format("0-200")).json()
        hs = filt["hotels"]

        hotels_hash = []
        cheapestHotel = {}

        for hotel in hs:
            hotel_id = hotel['hotel_id']
            hotel_name = hotel['name']
            hotel_lat = hotel['latitude']
            hotel_lng = hotel['longitude']
            hotel_address = hotel['address']
            hotel_image = hotel['images'];

            # search for cheapest price
            hotel_prices = filt["hotels_prices"]

            for price in hotel_prices:
                id = price["id"]
                if id == hotel_id:
                    hotel_price = price["agent_prices"][0]["price_total"]
                    break
            h = {
                "id": hotel_id,
                "name": hotel_name,
                "lat": hotel_lat,
                "lng": hotel_lng,
                "price": hotel_price,
                "address": hotel_address,
                "image": hotel_image
            }

            hotels_hash.append(h);

            if not cheapestHotel:
                cheapestHotel = h
            elif hotel_price < cheapestHotel['price']:
                cheapestHotel = h

        stops.append({
            "stopId": str(lat)+str(lng),
            "name": name,
            "lat": lat,
            "lng": lng,
            "time": time,
            "nbHotels": len(hotels_hash),
            "cheapestHotel": cheapestHotel
        })

        hotels.extend(hotels_hash)
        # URL= "http://partners.api.skyscanner.net/apiservices/hotels/liveprices/v2/UK/GBP/en-GB/{}/{}/{}/{}/{}?apiKey={}&pageSize=20"
        # res = requests.get(URL.format(entityid,checkindate,checkoutdate,guests,rooms,API))
        #
        # session = "http://partners.api.skyscanner.net" + res.headers['location']
        #
        # filt = requests.get(session + "&price={}".format("0-200")).json()
        # agents = filt["agents"]
        # match = []
        #
        # available = filt["total_available_hotels"]
        # hotel_hash = {} # hash table
        #
        # for agent in agents:
        #     hotel_hash[agent["id"]] = agent["name"]
        #
        # hotel_prices = filt["hotels_prices"]
        #
        # new_prices = {}
        #
        # for price in hotel_prices:
        #     id = price["agent_prices"][0]["id"]
        #     if hotel_hash[id] in new_prices:
        #         new_prices[hotel_hash[id]].append(price["agent_prices"][0]["price_total"])
        #     else:
        #         new_prices[hotel_hash[id]] = [price["agent_prices"][0]["price_total"]]

        # hotels.append(new_prices)

    # ==========================================================================
    # Return the response
    # ==========================================================================
    hotels = json.dumps(hotels)
    points = stops
    stops = json.dumps(stops)

    context = {
        'name': 'search',
        'origin': origin,
        'destination': destination,
        'mode': mode,
        'criteria': intervalType,
        'currency': cur,
        'interval': interval,
        'currency': cur,
        'stops': stops,
        'points': points,
        # 'flight_direct': flight_direct,
        # 'flight_price': flight_price,
        # 'flight_airlines': flight_airlines,
        'hotels': hotels
    }
    return render(request, "search.html", context)

def flight(request):
    context = {'name': 'flight'}
    return render(request, "flight.html",context)

def flightSearch(request):
    # Get the data
    start = request.GET['origin']
    end = request.GET['destination']
    date_depature_string = request.GET['dateDepature']
    date_arrival_string = request.GET['dateArrival']
    curr = request.GET['currency'] # "GBP" #or "EUR" or "GBP"
    # ==========================================================================
    # Skyscanner API
    # Search for flight
    # ==========================================================================
    api = "ha348334469154725681039185711735"
    location_url = "http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/GB/{}/EN/?query={}&apikey={}"

    location_start = json.loads(requests.get(location_url.format(curr,start, api)).text)
    location_id_start = location_start["Places"][0]['CityId']

    location_dest = json.loads(requests.get(location_url.format(curr,end, api)).text)
    location_id_dest = location_dest["Places"][0]['CityId']



    flight_query = {'cabinclass':'Economy','country':'UK','currency':'GBP','locale':'en-GB','locationSchema':'iata','originplace':location_id_start,'destinationplace':location_id_dest,'outbounddate':date_depature_string,'inbounddate':date_arrival_string,'adults':'1','children':'0','infants':'0','apikey':api}
    flight_headers = {'content-type': 'application/x-www-form-urlencoded'}
    session_url = "http://partners.api.skyscanner.net/apiservices/pricing/v1.0"
    response = requests.post(session_url,data=flight_query,headers=flight_headers)
    print(response)
    session_key = response.headers['Location']
    session_key = session_key + '?apiKey=' + api
    while True:
        try:
            res = requests.get(session_key,headers={'accept':'application/json'})
            data = res.json()
        except Exception:
            time.sleep(2)
            continue
        else:
            break

    while data["Status"] == "UpdatesPending":
        try:
            res = requests.get(session_key,headers={'accept':'application/json'})
            data = res.json()
        except Exception:
            time.sleep(0.5)
            continue
        else:
            break

    results = []
    count = 0

    for itinerary in data["Itineraries"]:
        travel = {"id":count,"outbound":[],"inbound":[],"prices":[]}

        out_id = itinerary["OutboundLegId"]
        in_id = itinerary["InboundLegId"]
        out_check = False
        in_check = False
        for leg in data["Legs"]:
            if leg["Id"] == out_id:
                for x in range(0,len(leg["SegmentIds"])):
                    segmentId = leg["SegmentIds"][x]
                    flightInfo = data["Segments"][segmentId]
                    origin = flightInfo["OriginStation"]
                    dest = flightInfo["DestinationStation"]
                    check_one = False
                    check_two = False
                    for place in data["Places"]:
                        if place["Id"] == origin:
                            out_from = place["Name"] + " (" +  place["Code"] + ")"
                            check_one = True
                        if place["Id"] == dest:
                            out_to = place["Name"] + " (" +  place["Code"] + ")"
                            check_two = True
                        if check_one and check_two:
                            break
                    out_depature_date= flightInfo["DepartureDateTime"][:10]
                    out_depature_time= flightInfo["DepartureDateTime"][11:]
                    out_arrival_date= flightInfo["ArrivalDateTime"][:10]
                    out_arrival_time= flightInfo["ArrivalDateTime"][11:]
                    out_duration= flightInfo["Duration"]
                    out_duration = '{:02d}:{:02d}'.format(*divmod(int(out_duration), 60))

                    flightId = flightInfo["Carrier"]
                    for carrier in data["Carriers"]:
                        if carrier["Id"] == flightId:
                            out_flight_name = carrier["Name"]
                            out_flight_number= carrier["Code"] + " " + flightInfo["FlightNumber"]
                            out_flight_imageUrl= carrier["ImageUrl"]
                            break
                    tmpout = {"from":out_from,"to":out_to,"depature_date":out_depature_date,"depature_time":out_depature_time,"arrival_date":out_arrival_date,"arrival_time":out_arrival_time,"duration":out_duration,"flight_name":out_flight_name,"flight_number":out_flight_number,"flight_imageUrl":out_flight_imageUrl}
                    travel["outbound"].append(tmpout)
                out_check = True

            if leg["Id"] == in_id:
                for x in range(0,len(leg["SegmentIds"])):
                    segmentId = leg["SegmentIds"][x]
                    flightInfo = data["Segments"][segmentId]
                    origin = flightInfo["OriginStation"]
                    dest = flightInfo["DestinationStation"]
                    check_one = False
                    check_two = False
                    for place in data["Places"]:
                        if place["Id"] == origin:
                            in_from = place["Name"] + " (" +  place["Code"] + ")"
                            check_one = True
                        if place["Id"] == dest:
                            in_to = place["Name"] + " (" +  place["Code"] + ")"
                            check_two = True
                        if check_one and check_two:
                            break
                    in_depature_date= flightInfo["DepartureDateTime"][:10]
                    in_depature_time= flightInfo["DepartureDateTime"][11:]
                    in_arrival_date= flightInfo["ArrivalDateTime"][:10]
                    in_arrival_time= flightInfo["ArrivalDateTime"][11:]
                    in_duration= flightInfo["Duration"]
                    in_duration = '{:02d}:{:02d}'.format(*divmod(int(in_duration), 60))

                    flightId = flightInfo["Carrier"]
                    for carrier in data["Carriers"]:
                        if carrier["Id"] == flightId:
                            in_flight_name = carrier["Name"]
                            in_flight_number= carrier["Code"] + " " + flightInfo["FlightNumber"]
                            in_flight_imageUrl= carrier["ImageUrl"]
                            break
                    tmpin = {"from":in_from,"to":in_to,"depature_date":in_depature_date,"depature_time":in_depature_time,"arrival_date":in_arrival_date,"arrival_time":in_arrival_time,"duration":in_duration,"flight_name":in_flight_name,"flight_number":in_flight_number,"flight_imageUrl":in_flight_imageUrl}
                    travel["inbound"].append(tmpin)
                in_check = True

            if in_check and out_check:
                break

        for booking in itinerary["PricingOptions"]:
            agent_id = booking["Agents"][0]
            for agent in data["Agents"]:
                if agent["Id"] == agent_id:
                    agent_name= agent["Name"]
                    ageny_imgUrl= agent["ImageUrl"]
                    agent_type= agent["Type"]
                    break
            cost= curr + " " + str(booking["Price"])
            booking_url= booking["DeeplinkUrl"]
            tempbook = {"agent_name":agent_name,"agent_imgUrl":ageny_imgUrl,"agent_type":agent_type,"cost":cost,"booking_url":booking_url}
            travel["prices"].append(tempbook)

        results.append(travel)
        count += 1

    return render(request,'flightSearch.html',{
        'flights': results,
        'origin': start,
        'destination': end,
        'currency': curr,
        'depatureDate' : date_depature_string ,
        'arrivalDate' : date_arrival_string ,
    })

def hotel(request):
    return render(request, "hotel.html")

def hotelSearch(request):
    # Get the data
    api = 'ha348334469154725681039185711735'
    location = request.GET['location']
    checkindate = request.GET['checkindate']
    checkoutdate = request.GET['checkoutdate']
    guests = request.GET['guests']
    rooms = request.GET['rooms']
    currency = request.GET['currency']
    currency = currency.upper()

    location_id_url = "http://partners.api.skyscanner.net/apiservices/hotels/autosuggest/v2/UK/{}/en-GB/{}?apikey={}"
    location_id_response = json.loads(requests.get(location_id_url.format(currency,location, api)).text)
    location_id = location_id_response["results"][0]["individual_id"]

    hotel_session_url = "http://partners.api.skyscanner.net/apiservices/hotels/liveprices/v2/UK/{}/en-GB/{}/{}/{}/{}/{}?apiKey={}&imageLimit=5"
    hotel_session_response =requests.get(hotel_session_url.format(currency,location_id,checkindate,checkoutdate,guests,rooms,api))
    hotel_session_key = hotel_session_response.headers['Location']
    hotel_session_key = "http://partners.api.skyscanner.net" + hotel_session_key + "&sortColumn=price&sortOrder=asc&imageLimit=5&pageSize=50"
    # for price range call the following session key
    # hotel_session_key = "http://partners.api.skyscanner.net" + hotel_session_key + "&sortColumn=price&sortOrder=asc&pageSize&price=" + minCost + "-" + maxCost

    while True:
        try:
            hotels_response= requests.get(hotel_session_key)
            hotels = hotels_response.json()
        except Exception:
            time.sleep(2)
            continue
        else:
            break

    while hotels["status"] == "PENDING":
        time.sleep(0.5)
        hotels_response= requests.get(hotel_session_key)
        hotels = hotels_response.json()

    # fi2 = open("tes.json","w+")
    # json.dump(hotels,fi2,indent=4)
    results = []
    count = 0

    ids = ""
    for hotel_id in hotels["hotels"]:
        ids = ids + str(hotel_id["hotel_id"]) + ","

    booking_res = requests.get(url="http://partners.api.skyscanner.net"+hotels["urls"]["hotel_details"] + "&hotelIds={}".format(ids[:-1]))
    booking_session_key = booking_res.headers['Location']
    booking_session_key = "http://partners.api.skyscanner.net" + booking_session_key
    while True:
        try:
            data_response= requests.get(booking_session_key)
            data = data_response.json()
        except Exception:
            time.sleep(2)
            continue
        else:
            break

    time_count  = 0
    while data["status"] == "PENDING":
        if time_count<10:
            time.sleep(0.5)
        elif time_count<20:
            time.sleep(1)
        elif time_count<30:
            time.sleep(1.5)
        elif time_count<40:
            time.sleep(2)
        else:
            time.sleep(3)
        data_response= requests.get(booking_session_key)
        data = data_response.json()
        print(time_count)
        time_count += 1


    number_of_hotels = len(hotels["hotels"])
    base_img_url = "http://"+ data["image_host_url"]
    # hotels["hotels"][x]
    # data["hotels"][x]
    for x in range(0,number_of_hotels):
        name = data["hotels"][x]["name"]
        type = hotels["hotels"][x]["types"][0]
        address = data["hotels"][x]["address"]
        try:
            popularity = data["hotels"][x]["popularity_desc"]
            popularity_score = data["hotels"][x]["popularity"]
        except KeyError:
            popularity = "Not Available"
            popularity_score = 0
        star_rating = data["hotels"][x]["star_rating"]
        description = data["hotels"][x]["description"]
        latitude = data["hotels"][x]["latitude"]
        longitude = data["hotels"][x]["longitude"]
        amenities = []
        for id in hotels["hotels"][x]["amenities"]:
            for amenity in hotels["amenities"]:
                if id == amenity["id"]:
                    amenities.append(amenity["name"])
                    break
        images = []
        img_urls = list(data["hotels"][x]["images"])
        c = 0
        for img_url in img_urls:
            imgs = list(data["hotels"][x]["images"][img_url])
            i_url = base_img_url+img_url+"morig.jpg"
            images.append(i_url)
            c += 1
            if c>5:
                break

        prices = []
        price_id = data["hotels"][x]["hotel_id"]
        for price in data["hotels_prices"]:
            minOverallCost = sys.maxsize
            if price["id"] == price_id:
                for agent in price["agent_prices"]:
                    cost_total = currency + " " + str(agent["price_total"])
                    cost_per_night = currency + " " + str(agent["price_per_room_night"])
                    booking_url = agent["booking_deeplink"]
                    agent_id = agent["id"]
                    for age in data["agents"]:
                        if agent_id == age["id"]:
                            agent_name = age["name"]
                            agent_url = age["image_url"]
                            break
                    priceInfo = {"cost_per_night":cost_per_night,"cost_total":cost_total,"agent_name":agent_name,"agent_url":agent_url,"booking_url":booking_url}
                    prices.append(priceInfo)

                    if agent["price_total"] < minOverallCost:
                        minOverallCost = agent["price_total"]
                break

        hotelInfo= {"id":count,"name":name,"type":type,"popularity":popularity,"popularity_score":popularity_score,"amenities":amenities,"images":images,"prices":prices,"address":address,"star_rating":star_rating,"lowestPrice":minOverallCost,"latitude":latitude,"longitude":longitude,"description":description}
        results.append(hotelInfo)
        count += 1

    hotelResults = sorted(results, key=lambda k: (k['lowestPrice'],k['popularity_score']))
    # fi = open("res.json","r")
    # hotelResults = fi.read()
    # fi.close()
    # print("done")
    return render(request, "hotelSearch.html",{
        "hotels":hotelResults,
    })

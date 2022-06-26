import requests

#Convert address into coordinates from mapquest api 

def coordinates(add):
    # api Secret Key
    key='Um5CCI8IPTS2XHZFL6l1nVJeSdTIDzKz'
    url='http://www.mapquestapi.com/geocoding/v1/address?key='
    loc=add
    main_url=url + key + '&location=' + loc
    data=requests.get(main_url).json()
    data=data['results'][0]
    location=data['locations'][0]
    lat=location['latLng']['lat']
    lon=location['latLng']['lng']
    url=location['mapUrl']
    
    return (lat,lon,url)


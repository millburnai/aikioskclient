import requests

class returnObj:
	def __init__(self, works, names, leaving, failed=False, withInfo=False):
		self.works = works
		self.names = names
		print(names)
		self.leaving = leaving
		self.failed=failed
		self.withInfo = withInfo

def makeRec(userID):
	iniFile = open("/home/pi/aikioskclient/ini.txt", "r")
	rURL = iniFile.readline().rstrip()
	kNum = int(iniFile.readline().rstrip())

	# furl = "http://72.79.54.70:55622/acceptedID/" + userID + "/" + str(kiosk)
	try:
		r = requests.get(url = rURL, params = {"id":str(userID), "kiosk":str(kNum)})
		print("finished")
		rdata = r.json()
		print(rdata)
	except:
		print("Server Error")
		return returnObj(False, "REE", False, failed = True)

	if rdata['id'] == str(-1):
		return returnObj(rdata['seniorPriv'], rdata["name"], not rdata['in'])
	else:
		return returnObj(rdata['seniorPriv'], rdata["name"], not rdata['in'], withInfo=True)

if __name__ == '__main__':
	print(makeRec("19422"))


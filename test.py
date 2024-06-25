from algolab import API
from secretconfig import *

client = API(MY_API_KEY, MY_USERNAME, MY_PASSWORD)

print(client.GetInstantPosition())

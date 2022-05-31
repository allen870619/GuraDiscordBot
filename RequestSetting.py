
class RequestSetting:

    def __init__(self):
        # Default
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        }

    def setHeaders(self, addHeaders=None):
        """_summary_

        Args:
            addHeaders (dict, optional)
        """

        # if parameter headers are not "None", and type is dict, then merge it.
        if(addHeaders != None and type(addHeaders) == dict):
            self.headers.update(addHeaders)

    def getHeaders(self):
        """_summary_

        Returns:
            dict: return headers
        """
        return self.headers

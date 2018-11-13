from defusedxml.minidom import parseString


class MyXMLError(Exception):
    pass


def myXMLParseString(text):
    try:
        return parseString(text)
    except Exception as e:
        raise MyXMLError(str(e))

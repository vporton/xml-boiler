from defusedxml.minidom import parseString


class MyXMLError(Exception):
    pass


# class MyXMLErrorForInputDocument(MyXMLError):
#     pass
#
#
# class MyXMLErrorForIntermediaryDocument(MyXMLError):
#     pass


def myXMLParseString(text):
    try:
        return parseString(text)
    except Exception as e:
        raise MyXMLError(str(e))

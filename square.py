from squarespace import Squarespace
from simple_salesforce import Salesforce
import os

def createContact(_firstname,_lastname,_email):
    result = sf.Contact.create({'FirstName':_firstname,'LastName':_lastname,'Email':_email,'RecordTypeId':'0125A0000013RldQAE'})
    print("### created contact")
    print(result)
    return result

def lookupContact(_order):
    soql_string = "SELECT Id, AccountId, Email FROM Contact WHERE Email = '{}'".format(_order['customerEmail'])
    
    _accountId = None
    _contactId = None
    try:
        result = sf.query(soql_string)
        if result['totalSize'] == 0:
            contactResult = createContact(_order['shippingAddress']['firstName'],_order['shippingAddress']['lastName'],_order['customerEmail'])
            soql_string = "SELECT Id, AccountId, Email FROM Contact WHERE Email = '{}'".format(_order['customerEmail'])
            result = sf.query(soql_string)
            
        _accountId = result['records'][0]['AccountId']
        _contactId = result['records'][0]['Id']
        updateSalesforce(_order,_accountId,_contactId)
    except IndexError as e:
        print("lookup/create error")

# add address to contact from squarespace? - Wait
# add phone number
# add contact / account creation
# multiple line item orders
# product name data formating 
def updateSalesforce(_order,_accountId,_contactId):
    _orderdesc = ''
    if len(_order['lineItems']) > 1:
        _orderdesc = 'Multiple line items'

    result = sf.Opportunity.create({'AccountId':_accountId,
                        'RecordTypeId':'0125A000001AnfqQAC',
                        'npsp__Primary_Contact__c':_contactId,
                        'StageName':'Awarded/Closed',
                        'CloseDate':_order['modifiedOn'],
                        'Product_Name__c':_order['lineItems'][0]['productName'],
                        'Name':"Product Order ID {}".format(_order['orderNumber']),
                        'Amount':_order['lineItems'][0]['unitPricePaid']['value'],
                        'Squarespace_Order_ID__c':_order['orderNumber'],
                        'Billing_City__c':_order['billingAddress']['city'],
                        'Billing_Country__c':_order['billingAddress']['countryCode'],
                        'Billing_State_Province__c':_order['billingAddress']['state'],
                        'Billing_Street__c':str(_order['billingAddress']['address1'])+' '+str(_order['billingAddress']['address2']),
                        'Billing_Zip_Postal_Code__c':_order['billingAddress']['postalCode'],
                        'Shipping_City__c':_order['shippingAddress']['city'],
                        'Shipping_Country__c':_order['shippingAddress']['countryCode'],
                        'Shipping_Recipient_Name__c':_order['shippingAddress']['firstName']+' '+_order['shippingAddress']['lastName'],
                        'Shipping_State_Province__c':_order['shippingAddress']['state'],
                        'Shipping_Street__c':str(_order['shippingAddress']['address1'])+' '+str(_order['shippingAddress']['address2']),
                        'Description':_orderdesc,
                        'Shipping_Zip_Postal_Code__c':_order['shippingAddress']['postalCode']})
    print("### create Opportunity")
    print(result)

def processOrders():
    # Iterate through pending Squarespace orders and send new orders to Salesforce    
    for order in store.orders(fulfillmentStatus='FULFILLED'): # Iterate through 20 orders
        if (float(order['orderNumber']) > max_id): 
            lookupContact(order)
            print("### squarespace order")
            print(order['orderNumber'])
            print(order['modifiedOn'])
            print(order['fulfillmentStatus'])
    try:
        while store.next_page() is not None:
            for order in store.next_page(): # Iterate through another 20 orders
                print(order['orderNumber'])
    except Exception as e:
        print(e)


print("### running square.py --")
# Get the ID of the last Squarespace order in Salesforce
soql_string = "select max(Squarespace_Order_ID__c) , max(CloseDate)  from Opportunity where Squarespace_Order_ID__c != null"
sf = Salesforce(username=os.environ.get('SFUSERNAME'), password=os.environ.get('SFPASSWORD'), security_token=os.environ.get('SFTOKEN'))
result = sf.query(soql_string)
max_id = result['records'][0]['expr0']

store = Squarespace(os.environ.get('SQUARESPACETOKEN'))
processOrders()
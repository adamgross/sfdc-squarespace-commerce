from squarespace import Squarespace
from simple_salesforce import Salesforce
import os 

# Get the ID of the last Squarespace order in Salesforce
soql_string = "select max(Squarespace_Order_ID__c) , max(CloseDate)  from Opportunity where Squarespace_Order_ID__c != null"
sf = Salesforce(username=os.environ.get('SFUSERNAME'), password=os.environ.get('SFPASSWORD'), security_token=os.environ.get('SFTOKEN'))
result = sf.query(soql_string)
max_id = result['records'][0]['expr0']

store = Squarespace(os.environ.get('SQUARESPACETOKEN'))


def updateSalesforce(_order):
    soql_string = "SELECT Id, AccountId, Email FROM Contact WHERE Email = '{}'".format(_order['customerEmail'])
    
    _accountId = None
    _contactId = None
    try:
        result = sf.query(soql_string)
        _accountId = result['records'][0]['AccountId']
        _contactId = result['records'][0]['Id']
    except IndexError as e:
        _accountId = 'new'
    print(_accountId)

    result = sf.Opportunity.create({'AccountId':_accountId,
                        'RecordTypeId':'0125A000001AnfqQAC',
                        'npsp__Primary_Contact__c':_contactId,
                        'StageName':'Pending',
                        'CloseDate':_order['modifiedOn'],
                        'Product_Name__c':_order['lineItems'][0]['productName'],
                        'Name':"Product Order ID {}".format(_order['orderNumber']),
                        'Amount':_order['lineItems'][0]['unitPricePaid']['value'],
                        'Squarespace_Order_ID__c':_order['orderNumber'],
                        'Billing_City__c':_order['billingAddress']['city'],
                        'Billing_Country__c':order['billingAddress']['countryCode'],
                        'Billing_State_Province__c':order['billingAddress']['state'],
                        'Billing_Street__c':str(_order['billingAddress']['address1'])+' '+str(order['billingAddress']['address2']),
                        'Billing_Zip_Postal_Code__c':order['billingAddress']['postalCode'],
                        'Shipping_City__c':_order['shippingAddress']['city'],
                        'Shipping_Country__c':_order['shippingAddress']['countryCode'],
                        'Shipping_Recipient_Name__c':_order['shippingAddress']['firstName']+' '+_order['shippingAddress']['lastName'],
                        'Shipping_State_Province__c':_order['shippingAddress']['state'],
                        'Shipping_Street__c':str(_order['shippingAddress']['address1'])+' '+str(_order['shippingAddress']['address2']),
                        'Shipping_Zip_Postal_Code__c':_order['shippingAddress']['postalCode']})


    print(result)

# Iterate through pending Squarespace orders and send new orders to Salesforce    
for order in store.orders(fulfillmentStatus='PENDING'): # Iterate through 20 orders
    if (float(order['orderNumber']) > max_id): 
        updateSalesforce(order)
        print(order['order-Number'])
        print(order['modifiedOn'])
        print(order['fulfillmentStatus'])
try:
    while store.next_page is not None:
        for order in store.next_page(): # Iterate through another 20 orders
            print(order['orderNumber'])
except Exception as e:
    print(e)
    

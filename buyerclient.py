import Pyro4
import Pyro4.errors
import ssl
import datetime
from prettytable import PrettyTable


Pyro4.config.SSL_CACERTS = "../cert/server_cert.pem"    # to make ssl accept the self-signed server cert
Pyro4.config.SSL_CLIENTCERT = "../cert/client_cert.pem"
Pyro4.config.SSL_CLIENTKEY = "../cert/buyer_key.pem"  

try:
    ns = Pyro4.locateNS()
    uri = ns.lookup('auction_server')
except Pyro4.errors.NamingError as e:
     print(f"{e}: NameServer could not be found")

# Pryo4 proxy object is created using the uri
auction_server = Pyro4.Proxy(uri)


def verify_cert(cert):
    if not cert:
        raise Pyro4.errors.CommunicationError("cert missing")
   
    if cert["serialNumber"] != "4675491CD0E90E06F095C495D240917A0A7F96CE":
        raise Pyro4.errors.CommunicationError("cert serial number incorrect")
    issuer = dict(p[0] for p in cert["issuer"])
    subject = dict(p[0] for p in cert["subject"])
    if issuer["organizationName"] != "LUG":
        # issuer is not often relevant I guess, but just to show that you have the data
        raise Pyro4.errors.CommunicationError("cert not issued by LUG")
    if subject["countryName"] != "GH":
        raise Pyro4.errors.CommunicationError("cert not for country GH")
    if subject["organizationName"] != "LUG":
        raise Pyro4.errors.CommunicationError("cert not for LUG")
    print("(SSL server cert is ok: serial={ser}, subject={subj})"
          .format(ser=cert["serialNumber"], subj=subject["organizationName"]))
    


# to make Pyro verify the certificate on new connections, use the handshake mechanism:
class CertCheckingProxy(Pyro4.core.Proxy):
    def _pyroValidateHandshake(self, response):
        cert = self._pyroConnection.getpeercert()
        




while True:
    print('Hi Buyer. Welcome to BuySell Auctioning System.')
    print('1. Create Account')
    print('2. Login')
    print("")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        try:
            # Register as a buyer
            buyer_id = 0
            buyer_name = input("Enter your name: ")
            buyer_number = input("Enter your number: ")

            password_match = False
            while not password_match:
                password1 = input("Enter your password:")
                password2 = input("Confirm your password:")
                if password1 == password2:
                    buyer_password = password2
                    password_match = True
                else: 
                    print("Password does not match. Please try again.")

            result = auction_server.create_buyer(buyer_id, buyer_name, buyer_number, buyer_password)
            print(result)
            print("")
            # Ask user if they want to continue
            another_action = input("Do you want to perform another action? (y/n): ")
            if another_action.lower() != 'y':
                print('Goodbye!')        
                break
        except Exception as e:
            print("An error occured: ", e)

    elif choice == 2:
        try:
            # Sign In
            buyer_name = input("Enter your registered name: ")
            buyer_password = input("Enter your password: ")
            result = auction_server.signin_buyer(buyer_name, buyer_password)
            print(" ")
            print("Login Successful!")
            print('ID:', result)
            if result != 'Login Failed. Incorrect Name or Password!':
                buyer_id = result
                while True:
                    print("")
                    print('1. View all the auctions on BuySell')
                    print('2. Place a bid')
                    print('3. Notifications')
                    print(" ")
                    choice = int(input("Enter your choice: "))
                    if choice == 1:
                        try:
                            auctions = auction_server.getAuctions()
                        # create a copy of the dictionary and remove the 'reservationPrice' key
                            keys = auctions[0].keys()
                            keys = list(keys)
                            keys.remove('reservationPrice')
                            keys.remove('winner_id') 
                            # create a prettytable object with the headers as the keys of the dictionaries
                            table3 = PrettyTable()
                            table3.field_names = keys
                            # add the rows to the table
                            for auction in auctions:
                                row = [auction[key] for key in keys]
                                table3.add_row(row)
                            # print the table
                            print(table3)
                            print("")
                        except IndexError:
                            print("No Auction on Buy Sell")
                            print("")
                        # Ask user if they want to continue
                        another_action = input("Do you want to perform another action? (y/n): ")
                        if another_action.lower() != 'y':        
                            print('Goodbye!')
                            break      
                            
                    elif choice == 2:
                        try:
                            auctions = auction_server.getActiveAuctions()
                            # create a copy of the dictionary and remove the 'reservationPrice' key
                            keys = auctions[0].keys()
                            keys = list(keys)
                            keys.remove('reservationPrice')
                            keys.remove('winner_id') 
                            # create a prettytable object with the headers as the keys of the dictionaries
                            table4 = PrettyTable()
                            table4.field_names = keys
                            # add the rows to the table
                            for auction in auctions:
                                row = [auction[key] for key in keys]
                                table4.add_row(row)
                            # print the table
                            print(table4)
                            print("")
                        except IndexError:
                            print("No Active Auctions on BuySell")
                            print("")
                    
                        auction_id = input("Enter AuctionID: ")
                        bid_amount = input("Enter bid amount: ")
                        try:
                            result = auction_server.place_bid(auction_id, buyer_id, bid_amount)
                            print(result)
                        except KeyError:
                            print('ID does not exist')
                        # Ask user if they want to continue
                        another_action = input("Do you want to perform another action? (y/n): ")
                        if another_action.lower() != 'y':  
                            print('Goodbye!')      
                            break
                    elif choice == 3:
                        try:
                            auctions = auction_server.getWinnerForBuyer(buyer_id)
                            # create a copy of the dictionary and remove the 'reservationPrice' key
                            keys = auctions[0].keys()
                            keys = list(keys)
                            keys.remove('reservationPrice')                         
                            # create a prettytable object with the headers as the keys of the dictionaries
                            table4 = PrettyTable()
                            table4.field_names = keys
                            # add the rows to the table
                            for auction in auctions:
                                row = [auction[key] for key in keys]
                                table4.add_row(row)
                            # print the table
                            print(table4)
                            print("")
                        except IndexError:
                            print("No Closed Auctions on BuySell")
                            print("")
                    
                    
                        # Ask user if they want to continue
                        another_action = input("Do you want to perform another action? (y/n): ")
                        if another_action.lower() != 'y':  
                            print('Goodbye!')      
                            break
                    else:
                        print('Wrong input. Try Again.')
            break    
        except Exception as e:
            print("An error occured: ", e)
    else:
        print('Wrong input. Try Again.')




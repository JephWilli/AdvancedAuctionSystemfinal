import Pyro4
import Pyro4.errors
import os
import csv
import random
import datetime
import threading
import time
import pandas as pd
import hashlib
import math
import secrets
import string

from cryptography.fernet import Fernet

# Generate a key to use for encryption and decryption
key = Fernet.generate_key()
cipher = Fernet(key)

Pyro4.config.SSL_SERVERCERT = "../cert/server_cert.pem"
Pyro4.config.SSL_SERVERKEY = "../cert/server_key.pem"
Pyro4.config.SSL_CACERTS = "../cert/client_cert.pem"    # to make ssl accept the self-signed client cert
print("SSL enabled (2-way).")


# Define the AuctionServer class
# Define the remote object interface
@Pyro4.expose # Exposes the class and its methods to remote object via Pyro4
class AuctionServer:   
    

    def __init__(self):
        self.lock = threading.Lock()
        self.auctionColumns = ['id','itemName', 'startingPrice', 'reservationPrice', 'seller_id', 'status', 'closing_date','winner_id','bid', 'bidders']
        self.startClosingDatesThread()    
    
    def createAuction(self,itemName,startingPrice, reservationPrice,  seller_id, closing_date):
        with self.lock:
            # acquire the lock to ensure only one thread can write to the file at a time
                try:
                    path = 'auctions.csv'
                    csv_file = ''
                    if not os.path.isfile(path):
                        csv_file = open(path,mode='w', newline='')
                        writer = csv.DictWriter(csv_file, fieldnames=self.auctionColumns)
                        writer.writeheader()
                        
                    else:            
                        csv_file = open(path, mode = 'a')

                    alphabet = string.ascii_letters + string.digits
                    aid = ''.join(secrets.choice(alphabet) for i in range(6))
                    auction={'id':aid, 'itemName':itemName, 'startingPrice':startingPrice, 'reservationPrice':reservationPrice, 'seller_id':seller_id, 'status':'active', 'closing_date':closing_date, 'winner_id':0,'bid':'0', 'bidders':'None'}
                    writer = csv.writer(csv_file)
                    writer.writerow(auction.values())
                    
                    csv_file.close()  

                    return 'Auction Created Successfully!'
                except: FileNotFoundError, PermissionError, csv.Error, UnicodeEncodeError
        


            
            
   
    def getAuctions(self):
        try:
            path = 'auctions.csv' 
            csv_file = open(path)
            reader = csv.DictReader(csv_file)             
            auctions = [row for row in reader]        
            # print(auctions)      
            return auctions
        except: FileNotFoundError, PermissionError, csv.Error, UnicodeDecodeError
    
    def getActiveAuctions(self):
        try:
            path = 'auctions.csv' 
            csv_file = open(path)
            reader = csv.DictReader(csv_file) 
            auctions = [row for row in reader if row['status'] == 'active']        
            # print(auctions)      
            return auctions
        except: FileNotFoundError, PermissionError, csv.Error, KeyError
    
    
    def getSellerAuctions(self, seller_id):
        try:
            path = 'auctions.csv' 
            csv_file = open(path)
            reader = csv.DictReader(csv_file) 
            auctions = [row for row in reader if row['seller_id'] == seller_id]        
            # print(auctions)      
            return auctions
        except: FileNotFoundError, PermissionError, csv.Error, KeyError
    
    def getSellerActiveAuctions(self, seller_id):
        try:
            path = 'auctions.csv' 
            csv_file = open(path)
            reader = csv.DictReader(csv_file) 
            auctions = [row for row in reader if row['status'] == 'active' and row['seller_id'] == seller_id]        
            # print(auctions)      
            return auctions
        except: FileNotFoundError, PermissionError, csv.Error, KeyError

    def checkClosingDates(self):
        try:
            while True:
                if os.path.isfile('auctions.csv'):
                    now = datetime.datetime.now()
                    with open('auctions.csv', mode='r', newline='') as csv_file:
                        reader = csv.DictReader(csv_file)
                        auctions = []
                        for row in reader:
                            closing_date = datetime.datetime.strptime(row['closing_date'], '%Y-%m-%dT%H:%M:%S.%f')
                            if now >= closing_date and row['status'] == 'active':
                                row['status'] = 'closed'
                                print(f"Auction {row['id']} closed.")
                                auctions.append(row)
                                
                    for auction in auctions:
                        df = pd.read_csv('auctions.csv')
                        idx = df.index[df['id'] == auction['id']]
                        df.loc[idx, 'status'] = 'closed'
                        df.to_csv('auctions.csv', index=False)
        
                time.sleep(30)
        except: FileNotFoundError, PermissionError, csv.Error, ValueError
            
    def startClosingDatesThread(self):
        print('started thread')
        thread = threading.Thread(target=self.checkClosingDates)
        try:
            thread.start()
        except: RuntimeError, KeyboardInterrupt


    def getWinnerForSeller(self, seller_id):
        try:
            path = 'auctions.csv' 
            csv_file = open(path)
            reader = csv.DictReader(csv_file) 
            auctions = [row for row in reader if row['status'] == 'closed' and row['seller_id'] == seller_id and row['winner_id'] !='0']         
            # print(auctions)      
            return auctions
        except: FileNotFoundError, PermissionError, csv.Error, KeyError
    
    def getWinnerForBuyer(self, buyer_id):
        try:
            path = 'auctions.csv' 
            csv_file = open(path)
            reader = csv.DictReader(csv_file, ) 
            auctions = [row for row in reader if row['status'] == 'closed' and row['winner_id'] !=buyer_id]  
            # and row['winner_id'] ==buyer_id       
            # print(auctions)      
            return auctions
        except: FileNotFoundError, PermissionError, csv.Error, KeyError

    def create_seller(self, seller_id, seller_name, seller_number, seller_password):
        with self.lock:
            # acquire the lock to ensure only one thread can write to the file at a time
                try:
                    # TO DO: MEthods for this 
                    # create the cryptogrpahicaly secure unique identifier 
                    alphabet = string.ascii_letters + string.digits
                    seller_id = ''.join(secrets.choice(alphabet) for i in range(6))
                    sellers = [[seller_id, seller_name, seller_number, seller_password]]
                    file_exists = os.path.isfile("Sellers.csv")
                    with open("Sellers.csv", "a", newline="") as file:
                        fieldnames = ["seller_id", "seller_name", "seller_number", "seller_password"]
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        if not file_exists:
                            writer.writeheader()
                        for row in sellers:
                            writer.writerow({"seller_id": row[0], "seller_name": row[1], "seller_number": row[2], "seller_password": row[3]})

                    return "Seller Account created successfully!"
                except: TypeError, ValueError, csv.Error, FileNotFoundError, PermissionError, IOError
    
    def signin_seller(self, seller_name, seller_password):
        try:
            with open('Sellers.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip header row
                for row in reader:
                    if row[1] == seller_name and row[3] == seller_password:
                        return row[0]
                return 'Login Failed. Incorrect Name or Password!'
        except: FileNotFoundError, IndexError, ValueError, PermissionError
    
    def create_buyer(self, buyer_id, buyer_name, buyer_number, buyer_password):
        with self.lock:
            # acquire the lock to ensure only one thread can write to the file at a time
            try:
                # get the current date and time
                now = datetime.datetime.now()
                day = now.day
                month = now.month
                year = now.year
                buyer_id = random.randint(100, 999)
                # create the unique identifier by concatenating the counter and current date
                buyer_id = str(buyer_id).zfill(3) + str('-') + str(day).zfill(2) + str(month).zfill(2) + str(year)
                buyers = [[buyer_id, buyer_name, buyer_number, buyer_password]]
                file_exists = os.path.isfile("Buyers.csv")
                with open("Buyers.csv", "a", newline="") as file:
                    fieldnames = ["buyer_id", "buyer_name", "buyer_number", "buyer_password"]
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    if not file_exists:
                        writer.writeheader()
                    for row in buyers:
                        writer.writerow({"buyer_id": row[0], "buyer_name": row[1], "buyer_number": row[2], "buyer_password": row[3]})
    
                return "Buyer Account created successfully!"
            except: FileNotFoundError, TypeError, PermissionError, ValueError, AttributeError
    
    def signin_buyer(self, buyer_name, buyer_password):
        try:
            with open('Buyers.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip header row
                for row in reader:
                    if row[1] == buyer_name and row[3] == buyer_password:
                        return row[0]
                return 'Login Failed. Incorrect Name or Password!'
        except: FileNotFoundError, TypeError, IndexError, UnicodeDecodeError, PermissionError
    

    def place_bid(self, auction_id, buyer_id, bid_amount):
        with self.lock:
            # acquire the lock to ensure only one thread can write to the file at a time
            try:
                if os.path.isfile('auctions.csv'):
                    df = pd.read_csv('auctions.csv', index_col='id')
                    auction = df.loc[auction_id]

                    bidders_array = df.loc[auction_id, 'bidders']

                    all_bidders  = []

                    if bidders_array != "None":
                        bidders_array = self.to_array(bidders_array)
                        for bidder in bidders_array:
                            all_bidders.append(bidder)

                    all_bidders.append(buyer_id)                
                    df.at[auction_id, 'bidders'] = all_bidders

                    if pd.isna(auction['bid']) or int(bid_amount) > auction['bid']:
                        df.at[auction_id, 'bid'] = bid_amount
                        df.at[auction_id, 'winner_id'] = buyer_id
                        df.to_csv('auctions.csv', index_label='id')
                        return "Bid successful"
                    else:
                        df.to_csv('auctions.csv', index_label='id')
                        return "Bid amount is lower than current bid"
                else: 
                  return "No auctions currently exist"  

            except (FileNotFoundError, PermissionError, pd.errors.EmptyDataError, KeyError, ValueError) as e:
                return str(e)
        
    def to_array(self,string):
        newstring = string.replace("[","").replace("]","").replace("'","").replace(" ","")
        array = newstring.split(",")
        print(array)
        return array

class CertValidatingDaemon(Pyro4.core.Daemon):
    def validateHandshake(self, conn, data):
        cert = conn.getpeercert()
        if not cert:
            raise Pyro4.errors.CommunicationError("client cert missing")
      
        if cert["serialNumber"] != "9BFD9872D96F066C":
            raise Pyro4.errors.CommunicationError("cert serial number incorrect")
        issuer = dict(p[0] for p in cert["issuer"])
        subject = dict(p[0] for p in cert["subject"])
        if issuer["organizationName"] != "LUG":
            # issuer is not often relevant I guess, but just to show that you have the data
            raise Pyro4.errors.CommunicationError("cert not issued by LUG")
        if subject["countryName"] != "GH":
            raise Pyro4.errors.CommunicationError("cert not for country GH")
        if subject["organizationName"] != "Razorvine.net":
            raise Pyro4.errors.CommunicationError("cert not for LUG")
        print("(SSL client cert is ok: serial={ser}, subject={subj})"
              .format(ser=cert["serialNumber"], subj=subject["organizationName"]))
        return super(CertValidatingDaemon, self).validateHandshake(conn, data)


# Start the Pyro4 server and register the AuctionServer object
if __name__ == "__main__":
    try:
        daemon = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        uri = daemon.register(AuctionServer)
        ns.register("auction_server", uri)
        print("Auction server ready.")
        daemon.requestLoop()
    except: Exception, FileNotFoundError, Pyro4.errors

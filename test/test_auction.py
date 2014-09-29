#!/usr/bin/env python
#
# This library is free software, distributed under the terms of
# the GNU Lesser General Public License Version 3, or any later version.
# See the COPYING file included in this archive
#
# The docstrings in this module contain epytext markup; API documentation
# may be created by processing this file with epydoc: http://epydoc.sf.net
import os
import sys
import unittest

# Add root directory of the project to our path in order to import db_store
dir_of_executable = os.path.dirname(__file__)
path_to_project_root = os.path.abspath(os.path.join(dir_of_executable, '..'))
sys.path.insert(0, path_to_project_root)
from node.db_store import Obdb
#from node.setup_db import setup_db
from pysqlcipher import dbapi2 as sqlite

TEST_DB_PATH = "auction_ob.db"

def setup_db(db_path, disable_sqlite_crypt=False):
    """ Create table auction
        Additional Information: http://www.sqlite.org/datatype3.html

            Column     |           Type           |                          Modifiers
        ---------------+--------------------------+-------------------------------------------------------------
         listingid     | integer                  | not null default nextval('auction_listingid_seq'::regclass)
         vendorid      | integer                  | default 0
         playerid      | integer                  | default 0
         batchid       | integer                  | default 0
         uploaditem    | integer                  |
         title         | text                     |
         ctgid         | integer[]                | default '{0}'::integer[]
         bid           | numeric(32,2)            | default 0.00
         bidder        | integer                  |
         bidcnt        | integer                  | default 0
         nickname      | character varying(80)    | default 'vendor'::character varying
         reservprice   | numeric(32,2)            |
         listingtype   | character(1)             | default 'O'::bpchar
         start         | timestamp with time zone |
         stop          | timestamp with time zone |
         registered    | timestamp with time zone | default ('now'::text)::timestamp with time zone
         start_epoch   | integer                  |
         start_180     | integer                  |
         stop_epoch    | integer                  |
         stop_3600     | integer                  |
         featured      | boolean                  |
         giftcert      | character(1)             | default 'N'::bpchar
         image         | text                     |
         title_idx     | text                     |
         currency      | character(3)             | default 'USD'::bpchar
         quantity      | numeric(32,2)            |
         paytype       | character(1)             | default 'N'::bpchar
         shippaymethod | character(1)             |
         ship1         | numeric(32,2)            |
         ship2         | numeric(32,2)            |
         shipdest      | character(1)             | default 'I'::bpchar
         moneyorder    | character(1)             | default 'N'::bpchar
         cod           | character(1)             | default 'N'::bpchar
         perchck       | character(1)             | default 'N'::bpchar
         visa_mc       | character(1)             | default 'N'::bpchar
         paypal        | character(1)             | default 'N'::bpchar
         sku           | character varying(20)    | default 'N'::character varying
         taxable       | character(1)             | default 'N'::bpchar
         url_thumbnail | text                     |
    """

    if not os.path.isfile(db_path):
        con = sqlite.connect(db_path)
        print 'Created database file'
        with con:
            cur = con.cursor()

            if not disable_sqlite_crypt:
                # Use PRAGMA key to encrypt / decrypt database.
                cur.execute("PRAGMA key = 'passphrase';")

            cur.execute("CREATE TABLE auction("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                        "market_id INT, "
                        "listingid INT NOT NULL, "
                        "vendorid INT DEFAULT 0, "
                        "playerid INT DEFAULT 0, "
                        "batchid INT DEFAULT 0, "
                        "uploaditem INT, "
                        "title TEXT, "
                        "ctgid INT, "
                        "bid DECIMAL(32,2) DEFAULT 0.00, "
                        "bidder INT, "
                        "bidcnt INT DEFAULT 0, "
                        "nickname VARYING CHARACTER(255) DEFAULT 'vendor', "
                        "reservprice DECIMAL(32,2), "
                        "listingtype CHARACTER(1) DEFAULT 'O', "
                        "start TIMESTAMP,"
                        "stop TIMESTAMP,"
                        "registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
                        "start_epoch INT, "
                        "start_180 INT, "
                        "stop_epoch INT, "
                        "stop_3600 INT, "
                        "featured BOOLEAN, "
                        "giftcert CHARACTER(1) DEFAULT 'N', "
                        "image TEXT, "
                        "title_idx TEXT, "
                        "currency CHARACTER(3) DEFAULT 'BTC', "
                        "quantity DECIMAL(32,2), "
                        "paytype CHARACTER(1) DEFAULT 'N', "
                        "shippaymethod CHARACTER(1), "
                        "ship1 DECIMAL(32,2), "
                        "ship2 DECIMAL(32,2), "
                        "shipdest CHARACTER(1) DEFAULT 'I', "
                        "moneyorder CHARACTER(1) DEFAULT 'N', "
                        "cod CHARACTER(1) DEFAULT 'N', "
                        "perchck CHARACTER(1) DEFAULT 'N', "
                        "visa_mc CHARACTER(1) DEFAULT 'N', "
                        "paypal CHARACTER(1) DEFAULT 'N', "
                        "sku VARYING CHARACTER(20) DEFAULT 'N', "
                        "taxable CHARACTER(1) DEFAULT 'N', "
                        "url_thumbnail TEXT, "
                        "FOREIGN KEY(market_id) REFERENCES markets(id))")

def setUpModule():
    # Create a test db.
    if not os.path.isfile(TEST_DB_PATH):
        print "Creating auction db: %s" % TEST_DB_PATH
        setup_db(TEST_DB_PATH)


def tearDownModule():
    # Cleanup.
    print "Cleaning up."
    os.remove(TEST_DB_PATH)


class TestDbOperations(unittest.TestCase):
    def test_insert_select_operations(self):
        # Initialize our db instance
        db = Obdb(TEST_DB_PATH)

        # Create a dictionary of a random auction
        auction_to_store = {"listingid": 1,
                           "vendorid": 2,
                           "playerid": 3,
                           "title": "A book",
                           "giftcert": "Y",
                           "title_idx": "Very happy book",
                           "bid": 10.4}

        # Use the insert operation to add it to the db
        db.insertEntry("auction", auction_to_store)

        # Try to retrieve the record we just added based on the playerid
        retrieved_auction = db.selectEntries("auction", {"playerid": 3})

        # The above statement will return a list with all the
        # retrieved records as dictionaries
        self.assertEqual(len(retrieved_auction), 1)
        retrieved_auction = retrieved_auction[0]

        # Is the retrieved record the same as the one we added before?
        self.assertEqual(
            auction_to_store["listingid"],
            retrieved_auction["listingid"],
        )
        self.assertEqual(
            auction_to_store["vendorid"],
            retrieved_auction["vendorid"],
        )
        self.assertEqual(
            auction_to_store["playerid"],
            retrieved_auction["playerid"],
        )
        self.assertEqual(
            auction_to_store["title"],
            retrieved_auction["title"],
        )
        self.assertEqual(
            auction_to_store["giftcert"],
            retrieved_auction["giftcert"],
        )

        # Let's do it again with a malicious auction.
        auction_to_store = {"listingid": 4,
                           "vendorid": 5,
                           "playerid": 6,
                           "title": "Devil''''s auction",
                           "giftcert": "N",
                           "title_idx": 'Very """"happy"""""" book',
                           "bid": 20.04}


        # Use the insert operation to add it to the db
        db.insertEntry("auction", auction_to_store)

        # Try to retrieve the record we just added based on the pubkey
        retrieved_auction = db.selectEntries("auction", {"listingid": 4})

        # The above statement will return a list with all the
        # retrieved records as dictionaries
        self.assertEqual(len(retrieved_auction), 1)
        retrieved_auction = retrieved_auction[0]

        # Is the retrieved record the same as the one we added before?
        self.assertEqual(
            auction_to_store["listingid"],
            retrieved_auction["listingid"],
        )
        self.assertEqual(
            auction_to_store["vendorid"],
            retrieved_auction["vendorid"],
        )
        self.assertEqual(
            auction_to_store["playerid"],
            retrieved_auction["playerid"],
        )
        self.assertEqual(
            auction_to_store["title"],
            retrieved_auction["title"],
        )
        self.assertEqual(
            auction_to_store["giftcert"],
            retrieved_auction["giftcert"],
        )

        # By ommiting the second parameter, we are retrieving all auction
        all_auction = db.selectEntries("auction")
        self.assertEqual(len(all_auction), 2)

        # Use the <> operator. This should return the auction with listingid 4.
#        retrieved_auction = db.selectEntries(
#            "auction",
#            {"listingid": {"value": 4, "sign": "<>"}}
#        )
#        self.assertEqual(len(retrieved_auction), 1)
#        retrieved_auction = retrieved_auction[0]
#        self.assertEqual(
#            retrieved_auction["listingid"],
#            4
#        )

    def test_update_operation(self):

        # Initialize our db instance
        db = Obdb(TEST_DB_PATH)

        # Retrieve the record with listingid equal to 4
        retrieved_auction = db.selectEntries("auction", {"listingid": 4})[0]

        # Check that the bid is still 20.04 as expected
        self.assertEqual(retrieved_auction["bid"], 20.04)

        # Update the record with listingid equal to 1
        # and lower its rating to 9
        db.updateEntries("auction", {"listingid": 1}, {"bid": 20.07})

        # Retrieve the same record again
        retrieved_auction = db.selectEntries("auction", {"listingid": 1})[0]

        # Test that the bid has been updated succesfully
        self.assertEqual(retrieved_auction["bid"], 20.07)

    def test_delete_operation(self):

        # Initialize our db instance
        db = Obdb(TEST_DB_PATH)

        # Delete the entry with listingid equal to 1
        db.deleteEntries("auction", {"listingid": 1})

        # Looking for this record with will bring nothing
        retrieved_auction = db.selectEntries("auction", {"listingid": 1})
        self.assertEqual(len(retrieved_auction), 0)

if __name__ == '__main__':
    unittest.main()

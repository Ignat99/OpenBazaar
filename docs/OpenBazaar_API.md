![0](https://blog.openbazaar.org/wp-content/uploads/2014/07/logo.png)

# OpenBazaar API

## Separation line OpenBazaar for the client and server

We have to change in that files and functions in OB:

https://github.com/OpenBazaar/OpenBazaar/blob/develop/node/multisig.py
1. class Multisig(object): def __init__(self, client, number_required, pubkeys):
2. def build_output_info_list(unspent_rows):
3. .... any
...
21. def finished_msig(tx):

https://github.com/OpenBazaar/OpenBazaar/blob/develop/node/connection.py
1. def create_zmq_socket(self):
2. def send_raw(self, serialized, callback=lambda msg: None):
3. def generate_sin(guid):
4. def send(self, data, callback=lambda msg: None): (Just check, may
be not need change)


https://github.com/OpenBazaar/OpenBazaar/blob/develop/node/transport.py
1. def build_output_info_list(unspent_rows):
2. def _generate_new_keypair(self):
3. def respond_pubkey_if_mine(self, nickname, ident_pubkey):
4. def _setup_settings(self):
5. def start_listener(self):
6. def add_callbacks(self, callbacks):
7. def add_callback(self, section, callback):
8. def trigger_callbacks(self, section, *data):
9. def send(self, data, send_to=None, callback=lambda msg: None):
10. def broadcast_goodbye(self):
11. def _on_message(self, msg):
12. def _on_raw_message(self, msg):
13. def _connect_to_bitmessage(self, bm_user, bm_pass, bm_port):
14. def _setup_settings(self):
15. def pubkey_exists(self, pub):
16. def send(self, data, send_to=None, callback=lambda msg: None):


https://github.com/OpenBazaar/OpenBazaar/blob/develop/node/ws.py
1. def reputation_pledge_retrieved(amount, page):
2. def found_unspent(amount):
3. def on_listing_results(self, msg):
4. def on_no_listing_result(self, msg):
5. def on_listing_result(self, msg):
6. def client_add_trusted_notary(self, socket_handler, msg):
7. def client_remove_trusted_notary(self, socket_handler, msg):
8. def client_get_notaries(self, socket_handler, msg):
9. def client_clear_dht_data(self, socket_handler, msg): (need check)
10. def client_undo_remove_contract(self, socket_handler, msg):
11. def client_check_order_count(self, socket_handler, msg):
12. def client_query_orders(self, socket_handler=None, msg=None):
13. def client_query_contracts(self, socket_handler, msg):
14. def client_query_messages(self, socket_handler, msg):
15. def client_send_message(self, socket_handler, msg):
16. def client_republish_contracts(self, socket_handler, msg): (check
in market.py interface)
17. def client_query_order(self, socket_handler, msg):  (check in market.py)
18. def client_update_settings(self, socket_handler, msg):
19. def client_create_contract(self, socket_handler, contract): (check
in market.py interface)
20. def client_remove_contract(self, socket_handler, msg): (check in
market.py interface)
21. def client_pay_order(self, socket_handler, msg): (check in
market.py interface)
22. def client_ship_order(self, socket_handler, msg): (check in
market.py interface)
23. def client_refund_order(self, socket_handler, msg):
24. def get_history():  sub-method
25. def client_release_payment(self, socket_handler, msg):
26. def get_history(): sub-method
27. def on_release_funds_tx(self, msg):
28. def get_history(): sub-method
29. def client_generate_secret(self, socket_handler, msg): (check)
30. def client_order(self, socket_handler, msg): (check in market.py interface)
31. def client_review(self, socket_handler, msg): (check in market.py interface)
32. def client_search(self, socket_handler, msg):
33. def client_query_network_for_products(self, socket_handler, msg):
34. def client_query_store_products(self, socket_handler, msg):
35. def on_find_products_by_store(self, results):
36. def on_find_products(self, results):
37. def client_shout(self, socket_handler, msg):
38. def on_node_search_value(self, results, key): (need check)
39. def on_global_search_value(self, results, key): (need check)
40. def on_node_search_results (self, results):
41. def on_node_message(self, *args):
42. def send_to_client(self, error, result):
43. def get_peers(self): (need check)

## Terms & Conventions

The upper part is the client (the background and the frontend)
The lower part is the server (or demons as local and remote)
At this stage, we assume Counterpart code is The lower part.
OpenBazaar is The upper part.

## Tests

Upon completion of the project for all 84 functions (maybe more) will be made by the unit tests. 
Which will prove the compatibility of the basic version OpenBazaar and modifications.
Tests to respond quickly to changes in the OpenBazaar code on the one hand and on the other Counterpart code.

## API Changes

Version 0.0.1


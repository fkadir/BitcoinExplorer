# BitcoinExplorer

**Project**

The aim of this project was to develop a working Bitcoin blockchain viewer application. This is similar to existing viewers such as the Blockchain Explorer, although the scope and complexity is much smaller. The application displays blocks as they are mined by the Bitcoin system. For each block, it displays:

• The date and time that the block was added to the blockchain, formatted in a human
readable form

• Number of transactions in the block

• The nonce that was used to successfully hash the block, and the difficulty level

• Verify that that hash does indeed match the hash included in the block!

Additionally, it displays the message header of all other messages send over the network.

**Instructions**

You can run this bitcoin explorer by cloning the repo and:

• running the file through with any IDE or

• typing python bitcoinexplorer.py in the command line (where the file is saved)

The program has no additional dependencies such as interpreters/compilers/runtimes!

warning: sometimes the connection to the bitcoin node can't be established right away. The comman line shows an time out error in this case. Run the program again and it shoul work.

**Internal architecture overview**

functions:

• transform_var_int(value)

transform the var_int format to the integer value

• create_var_int(value)

transform the integer value to the var_int format

• create_sub_version()

create user agent field for the version message

• create_network_address(ip_address, port)

given the ip_address and port, create the network address format

• create_message(magic, command, payload)

given the magic number, command and payload, construct the message to be send to the bitcoin node

• create_payload_version(node_ip_address)

create the payload for the version message

• create_message_verrack()

create specific verrack message

• create_payload_getdata(count, block_hash)

create the payload for the getdata message

• unpack_header(response)

retrieve the information from the message header of a received message

• parse_inv_payload(payload)

retrieve the information from the inv message

• parse_block_payload(payload)

retrieve the information from the block message

• display_block(timestamp, nonce, difficulty, send_hash, rec_hash, n_tx)

display the information on the command line.

• main

Connection to a bitcoin node (ip_address hard coded)is established. Message headers and mined bitcoin blocks are displayed continuously.

I recently had to fiddle with GPG on the command line. After reading man pages and some Google results, this is a succint summary of commands I think necessary to get started:

# listing keys
`gpg --list-keys`

`gpg --list-secret-keys`

# generating a key
`gpg --gen-key`

remember to save the key password!

# encrypt a message into text file
`gpg --armor --encrypt --recipient <recipient1> --recipient <recipient2> message_to_encrypt.txt`

which produces file `message_to_encrypt.txt.asc`

# decrypt file
`gpg --decrypt message_to_encrypt.txt.asc`

# export public key into text file
`gpg --export --armor <email, or other identifier in key listing entry> > my_public_key.asc`

# import some public key
`gpg --import some_pkey.asc`
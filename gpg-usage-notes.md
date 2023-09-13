I recently had to fiddle with GPG on the command line. After reading man pages & Google results, this is a succint summary of commands I think necessary to get started:

# listing keys
`gpg --list-keys --with-subkey-fingerprint`

`gpg --list-secret-keys`

# generating a key
`gpg --gen-key`

remember to save the key password somewhere!

# deleting a key

if you have both the corresponding private & public key, delete the private key first:

`gpg --delete-secret-keys <key-id>`

then delete the public key:

`gpg --delete-keys <key-id>`

# encrypt a message & sign into text file
`gpg --recipient <recipient-key-id> --local-user <your-signing-key-id> --sign --encrypt --armor --output "encrypted.txt" file-to-encrypt.txt`

which produces a file `encrypted.txt`

# decrypt file
`gpg --decrypt encrypted.txt`

# export public key into text file
`gpg --export --armor <key-id> > my-public-key.txt`

# export private key into text file
`gpg --export-secret-key --armor <key-id> > my-private-key.txt` 

> **Warning**
> Take care in saving this file safely.

# import some public key
`gpg --import some-key.asc`
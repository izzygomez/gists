# Listing keys

`gpg --list-keys --with-subkey-fingerprint`

`gpg --list-secret-keys`

# Generating a key

`gpg --full-gen-key`

Remember to save the key password somewhere safe!

# Deleting a key

If your keychain has both private & public keys, delete the private key first:

`gpg --delete-secret-keys <key-id>`

Then delete the public key:

`gpg --delete-keys <key-id>`

# Encrypt & (optionally) sign a message into text file

For encrypting & signing:

`gpg --recipient <recipient-key-id> --recipient <your-key-id> --local-user <your-key-id> --sign --encrypt --armor --output encrypted.txt file-to-encrypt.txt`

For encrypting:

`gpg --recipient <recipient-key-id> --recipient <your-key-id> --encrypt --armor --output encrypted.txt file-to-encrypt.txt`

Which produces a file `encrypted.txt`. Per `man gpg`, note that `--local-user` specifies what key to use for signing. You add yourself as a recipient as well, optionally, in order to also be able to decrypt the encrypted message; got this idea from [here](https://www.youtube.com/watch?v=mE8fL5Fu8x8&t=866s). Think of the use case where you want to be able to read the encrypted emails you've sent.

# Decrypt file
`gpg --decrypt encrypted.txt`

# Export public key into text file
`gpg --export --armor <key-id> > my-public-key.txt`

# Export private key into text file
`gpg --export-secret-key --armor <key-id> > my-private-key.txt` 

> **Warning**
> Take care in saving this file safely.

# Import some public key
`gpg --import some-key.asc`
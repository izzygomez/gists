I recently had to fiddle with GPG on the command line. After reading man pages & Google results, this is a succint summary of commands I think necessary to get started:

# Listing keys
`gpg --list-keys --with-subkey-fingerprint`

`gpg --list-secret-keys`

# Generating a key
`gpg --gen-key`

Remember to save the key password somewhere!

# Deleting a key

If you have both the corresponding private & public key, delete the private key first:

`gpg --delete-secret-keys <key-id>`

Then delete the public key:

`gpg --delete-keys <key-id>`

# Encrypt a message & sign into text file
`gpg --recipient <recipient-key-id> --recipient <your-key-id> --local-user <your-signing-key-id> --sign --encrypt --armor --output "encrypted.txt" file-to-encrypt.txt`

Which produces a file `encrypted.txt`. You add yourself as a recipient as well (optionally) in order to also be able to decrypt the encrypted message; got this idea from [here](https://www.youtube.com/watch?v=mE8fL5Fu8x8&t=866s). Think of the use case where you want to be able to read the encrypted emails you've sent.

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
# GPG Usage Notes

## Listing keys

`gpg --list-keys --with-subkey-fingerprint`

`gpg --list-secret-keys`

## Generating a key

`gpg --full-gen-key`

Remember to save the key password somewhere safe!

## Deleting a key

If your keychain has both private & public keys, delete the private key first:

`gpg --delete-secret-keys <key-id>`

Then delete the public key:

`gpg --delete-keys <key-id>`

## Encrypt and/or sign a message

For encrypting & signing, run the following to produce `encrypted-and-signed.txt`:

`gpg --recipient <recipient-key-id> --recipient <your-key-id> --local-user <your-key-id> --sign --encrypt --armor --output encrypted-and-signed.txt message.txt`

For just encrypting, run the following to produce `encrypted.txt`:

`gpg --recipient <recipient-key-id> --recipient <your-key-id> --local-user <your-key-id> --encrypt --armor --output encrypted.txt message.txt`

For just signing, run the following to produce `signed.txt`:

`gpg --local-user <your-key-id> --sign --armor --output signed.txt message.txt`

Per `man gpg`, note that `--local-user` specifies what key to use for signing. You add yourself as a recipient as well, optionally, in order to also be able to decrypt the encrypted message; got this idea from [here](https://www.youtube.com/watch?v=mE8fL5Fu8x8&t=866s). Think of the use case where you want to be able to read the encrypted emails you've sent.

## Decrypt file
`gpg --decrypt encrypted.txt`

## Export public key into text file
`gpg --export --armor <key-id> > my-public-key.txt`

## Export private key into text file
`gpg --export-secret-key --armor <key-id> > my-private-key.txt` 

> **Warning**
> Take care in saving this file safely.

# Import some public or private key
`gpg --import some-key.asc`

## Comparing Keys

If you have two GPG key files (e.g. an old backup & a fresh export) & want to verify they represent the same key, **do not use `diff`** or similar tools. Exported private keys often include metadata like timestamps, export versions, or subkey ordering, so the file contents may differ even if the key material is the same.

Instead, compare their **fingerprints**, which uniquely identify the cryptographic key.

To safely display the fingerprint of a key file *without importing it*:

```sh
gpg --import-options show-only --with-fingerprint --import <key-file>
```

> `--import-options show-only` tells GPG to parse & display the key’s metadata without actually adding it to your keyring.

Run this for both key files:

```sh
gpg --import-options show-only --with-fingerprint --import current-key.asc
gpg --import-options show-only --with-fingerprint --import old-key.asc
```

If the fingerprints match, the keys are functionally identical and can be safely treated as the same.
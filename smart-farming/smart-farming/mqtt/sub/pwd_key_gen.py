from cryptography.fernet import Fernet

def keygen():
    key = Fernet.generate_key()
    print(key)
def encrypt_password():
    key = "js_Va5FJJBNEC8fAlxSLpGaijmA_p8TYaTUfx3B-8gY="
    cipher_suite = Fernet(key)
    ciphered_text = cipher_suite.encrypt(b'mqttpwd')
    print(ciphered_text)
    with open('smart-famrming.bin','wb') as file_object: file_object.write(ciphered_text)

#pwd = raw_input("Insert a password to cipher: ")
encrypt_password()

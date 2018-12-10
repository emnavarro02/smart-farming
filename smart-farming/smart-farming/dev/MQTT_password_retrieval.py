from cryptography.fernet import Fernet

def get_pass():
    key = "js_Va5FJJBNEC8fAlxSLpGaijmA_p8TYaTUfx3B-8gY="
    cipher_suite = Fernet(key)
    with open('smart-farming.bin', 'rb') as file_object:
        for line in file_object:
            encryptedpwd = line
    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
    MQTT_pass = bytes(uncipher_text).decode("utf-8")
    return MQTT_pass

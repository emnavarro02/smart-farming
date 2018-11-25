from firebase import firebase


try:
    firebase = firebase.FirebaseApplication('https://smartgarden-fe7b3.firebase.io')
    print firebase
except:
     print("Connection failed.")



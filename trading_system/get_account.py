from webull import webull


wb = webull()
wb._did = "83o2rekrvxrpwgiqg92omut1taye7wc1"

username = input("Enter your Webull username/email: ")
password = input("Enter your Webull password: ")

print("Attempting to login...")

# Login to Webull
# Note: Some accounts may require additional verification (SMS, email, etc.)
login_result = wb.login(username, password)
wb._set_did("83o2rekrvxrpwgiqg92omut1taye7wc1")

account = wb.get_account()
print(account)

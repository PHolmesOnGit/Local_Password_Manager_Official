from tkinter import messagebox, ttk
from tkinter import *
from random import *
import pyotp
from Crypto.Cipher import AES
import sys
import json


# ---------------------------- MAIN WINDOW ------------------------------- #
def main_ui():
    # ---------------------------- PASSWORD GENERATOR ------------------------------- #
    def generate_pw():
        # feel to change the amount in each of the "nr_XXXXXXX" lines to lengthen/shorten generated passwords
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                   'u', 'v',
                   'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                   'Q', 'R',
                   'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

        nr_letters = randint(8, 10)
        nr_symbols = randint(2, 4)
        nr_numbers = randint(2, 4)

        char_list = [choice(letters) for _ in range(nr_letters)]
        sym_list = [choice(symbols) for _ in range(nr_symbols)]
        num_list = [choice(numbers) for _ in range(nr_numbers)]

        password_list = char_list + sym_list + num_list
        shuffle(password_list)

        password = "".join(password_list)
        password_entry.delete(0, END)
        password_entry.insert(0, password)

    # ---------------------------- SAVE PASSWORD ------------------------------- #
    def store_password():
        # Takes the data in the input fields and encrypts it into a .bin file

        website = website_entry.get().title()
        email = email_entry.get()
        password = password_entry.get()

        if len(website) == 0 or len(password) == 0:
            messagebox.showinfo(title="Oops", message="Please make sure you haven't left any fields empty.")
        else:
            encrypted_password = f'Email: {email} \nPassword: {password}'.encode()
            cipher = AES.new(AES_KEY, AES.MODE_OCB)
            ciphertext, tag = cipher.encrypt_and_digest(encrypted_password)
            assert len(cipher.nonce) == 15

            with open(f"LPMData/{website}.bin", "wb") as encrypted_file:
                encrypted_file.write(tag)
                encrypted_file.write(cipher.nonce)
                encrypted_file.write(ciphertext)

            website_entry.delete(0, END)
            password_entry.delete(0, END)

    # ---------------------------- FIND PASSWORD ------------------------------- #
    def find_password():
        # Pulls the data from the website field and uses the AES Key to decrypt the correlating .bin file
        website = website_entry.get().title()

        try:
            with open(f"LPMData/{website}.bin", "rb") as decrypted_file:
                tag = decrypted_file.read(16)
                nonce = decrypted_file.read(15)
                ciphertext = decrypted_file.read()
                cipher = AES.new(AES_KEY, AES.MODE_OCB, nonce=nonce)

                try:
                    message = cipher.decrypt_and_verify(ciphertext, tag)
                except ValueError:
                    print("The message was modified!")
                    sys.exit(1)

                messagebox.showinfo(title=website, message=message.decode())
        except FileNotFoundError:
            messagebox.showinfo(title="Error",
                                message="No data file found.\nPlease add an entry to create the data file.")

    # ---------------------------- MAIN TKINTER UI ------------------------------- #

    window = Tk()
    window.title("Local Password Manager")
    window.config(padx=20, pady=20)

    # Logo setup
    img = PhotoImage(file="logo.png")
    canvas = Canvas(width=200, height=200)
    canvas.create_image(100, 100, image=img)
    canvas.grid(row=0, column=1)

    # Widget Setup
    website_label = ttk.Label(text="Website:")
    website_label.grid(row=1, column=0)

    website_entry = ttk.Entry(width=20)
    website_entry.grid(row=1, column=1)

    email_label = ttk.Label(text="Email/Username:")
    email_label.grid(row=2, column=0)

    email_entry = ttk.Entry(width=40)
    email_entry.grid(row=2, column=1, columnspan=2)

    password_label = ttk.Label(text="Password:")
    password_label.grid(row=3, column=0)

    password_entry = ttk.Entry(width=20)
    password_entry.grid(row=3, column=1)

    password_button = ttk.Button(text="Generate Password", command=generate_pw)
    password_button.grid(row=3, column=2)

    add_button = ttk.Button(text="Add", width=20, command=store_password)
    add_button.grid(row=4, column=1)

    search_button = ttk.Button(text="Search", command=find_password)
    search_button.grid(row=2, column=3)

    exit_button = ttk.Button(text="Exit", command=window.destroy)
    exit_button.grid(row=5, column=1)

    window.mainloop()


# ---------------------------- LOGIN WINDOW ------------------------------- #
def login_ui():
    # ---------------------------- AUTHENTICATE OTP ------------------------------- #
    def authenticate_otp_code():
        # Authenticates 6 digit google auth code
        totp = pyotp.TOTP(SECRET_KEY)
        otp_code = otp_entry.get()
        if otp_code == totp.now():
            login_window.destroy()
            main_ui()
        else:
            messagebox.showinfo(title="Error", message="Wrong code")

    # ---------------------------- LOGIN TKINTER UI ------------------------------- #

    login_window = Tk()
    login_window.title("Local Password Manager")
    login_window.config(padx=20, pady=20)

    # Widget Setup
    otp_label = ttk.Label(text="Please Input your 6 digit auth code below")
    otp_label.grid(row=0, column=0)

    otp_entry = ttk.Entry(width=20)
    otp_entry.grid(row=1, column=0)

    otp_button = ttk.Button(text="Login", command=authenticate_otp_code)
    otp_button.grid(row=2, column=0)

    login_window.mainloop()


f = open("Data/keys.json")
data = json.load(f)
AES_KEY = bytes(data['keys'][0], 'utf-8')
SECRET_KEY = data['keys'][1]
login_ui()

from password_manager import PasswordManager

def main():
    password = {
        "email": "987654",
        "facebook": "fb123",
        "youtube": "yt123",
        "something": "newPass@123"
    }

    pm = PasswordManager()

    print("""What do you want to do?
          1. Create a new key
          2. Load an existing key
          3. Create new password file
          4. Load existing password file
          5. Add a new password
          6. Get a password
          (q) to Quit
          """)
    
    done = False

    while not done:

        choice = input("Enter your choice:\n")

        if choice == "1":
            path = input("Enter the path: ")
            pm.createKey(path)
        elif choice == "2":
            path = input("Enter path: ")
            pm.loadKey(path)
        elif choice == "3":
            path = input("Enter path: ")
            pm.createPasswordFile(path, password)
        elif choice == "4":
            path = input("Enter path: ")
            pm.loadPasswordFile(path)
        elif choice == "5":
            site = input("Enter the site: ")
            password = input("Enter the password: ")
            pm.addPassword(site, password)
        elif choice == "6":
            site = input("For which site do you want the password: ")
            print(f"Password for {site} is {pm.getPassword(site)}")
        elif choice == "q":
            done = True
            print("Have a nice day!")
        else:
            print("Invalid Input")

if __name__ == "__main__":
    main()

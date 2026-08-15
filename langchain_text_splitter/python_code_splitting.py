from langchain_text_splitters import RecursiveCharacterTextSplitter,Language

text=""" 
class Customer:
    def __init__(self, customer_id, name, email, phone):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def show_details(self):
        print("\n---------- CUSTOMER DETAILS ----------")
        print(f"Customer ID : {self.customer_id}")
        print(f"Name        : {self.name}")
        print(f"Email       : {self.email}")
        print(f"Phone       : {self.phone}")

        print("\nAccounts:")
        for account in self.accounts:
            print(
                f"  Account No: {account.account_number} "
                f"| Balance: ₹{account.balance:.2f}"
            )"""
splitter=RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=100,
    chunk_overlap=0,
    
)
result=splitter.split_text(text)
print(result)
print(len(result))
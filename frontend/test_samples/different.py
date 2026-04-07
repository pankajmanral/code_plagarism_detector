class UserList:
    def __init__(self):
        self.users = []
        
    def add_user(self, name, age):
        self.users.append({"name": name, "age": age})
        
    def get_average_age(self):
        if not self.users:
            return 0
            
        total_age = sum([user["age"] for user in self.users])
        return total_age / len(self.users)

if __name__ == "__main__":
    ul = UserList()
    ul.add_user("Alice", 25)
    ul.add_user("Bob", 30)
    print("Average age:", ul.get_average_age())

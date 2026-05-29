class User:
	nick: str
	ip_addr: str
	udp_port: int

class Message:
	type: str
	user: User
	userlist: list[User]
	broadcasting_user: User
	msg: str
	
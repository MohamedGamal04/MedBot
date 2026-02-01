from sqlalchemy import Column, String, text , create_engine , Integer , Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base , sessionmaker
from email_validator import validate_email, EmailNotValidError
import bcrypt

DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "test"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column("identifier",Text, unique=True, nullable=False)
    meta_data = Column(
        "metadata", 
        JSONB, 
        nullable=False, 
        server_default=text("'{}'")
    )
    created_at = Column("createdAt", Text, server_default=text("CURRENT_TIMESTAMP"))
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer)
    _password = Column("password", String, nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, plain_text_password):
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
        self._password = hashed_bytes.decode('utf-8')

    def check_password(self, plain_text_password):
        return bcrypt.checkpw(
            plain_text_password.encode('utf-8'), 
            self._password.encode('utf-8')
        )
    
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def login_user(username, plain_text_password):
    user = session.query(User).filter_by(username=username.lower()).first()
    if user and user.check_password(plain_text_password):
        return user
    return False

def register_user(first_name, last_name, username, email, age, plain_text_password):
    try:
        valid = validate_email(email.lower())
        email = valid.email
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email address: {e}")

    if session.query(User).filter_by(username=username.lower()).first():
        raise ValueError("Username already exists.")
    if session.query(User).filter_by(email=email.lower()).first():
        raise ValueError("Email already registered.")

    new_user = User(
        first_name=first_name.lower(),
        last_name=last_name.lower(),
        username=username.lower(),
        email=email.lower(),
        age=age,
        meta_data={"email": email.lower(), "first_name": first_name.lower(), "last_name": last_name.lower(), "age": age},
    )
    new_user.password = plain_text_password
    
    session.add(new_user)
    session.commit()
    return new_user

if __name__ == "__main__":
    # Example usage
    try:
        user = register_user("John", "Doe", "johndoe", "john.doe@gmail.com", 30, "securepassword123")
        print(f"User {user.username} registered successfully.")
    except ValueError as ve:
        print(ve)
    
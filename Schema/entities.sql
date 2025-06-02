CREATE TABLE Users (
    User_ID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Bank_Balance DECIMAL(15,2) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Transaction (
    Transaction_ID SERIAL PRIMARY KEY,
    User_ID INT NOT NULL,
    Account_ID INT,
    Amount DECIMAL(15,2) NOT NULL,
    Type VARCHAR(50) CHECK (Type IN ('Deposit', 'Withdrawal')),
    Description TEXT,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE,
    FOREIGN KEY (Account_ID) REFERENCES Savings_Account(Account_ID) ON DELETE CASCADE
);

CREATE TABLE Savings_Rule (
    Rule_ID SERIAL PRIMARY KEY,
    Account_ID INT NOT NULL,
    Rule_Type VARCHAR(50) CHECK (Rule_Type IN ('Round-Up', 'Fixed', 'Percentage')) NOT NULL,
    Rule_Condition TEXT NOT NULL,
    Active BOOLEAN DEFAULT TRUE,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Account_ID) REFERENCES Savings_Account(Account_ID) ON DELETE CASCADE
);

CREATE TABLE Savings_Account (
    Account_ID SERIAL PRIMARY KEY,
    User_ID INT NOT NULL,
    Balance NUMERIC(15,2) DEFAULT 0 NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
);

CREATE TABLE Savings_Goal (
    Goal_ID SERIAL PRIMARY KEY,
    User_ID INT NOT NULL,
    Goal_Name VARCHAR(255) NOT NULL,
    Target_Amount NUMERIC(15,2) NOT NULL,
	Saved_Amount NUMERIC(15,2) DEFAULT 0 NOT NULL,
    Status VARCHAR(50) CHECK (Status IN ('Active', 'Completed', 'Cancelled')),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
);

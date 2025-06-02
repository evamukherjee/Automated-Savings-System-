----Trigger for Updating User Bank Balance After Transaction

CREATE OR REPLACE FUNCTION update_user_bank_balance_after_transaction()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.Type = 'Deposit' THEN
        UPDATE Users
        SET Bank_Balance = Bank_Balance + NEW.Amount
        WHERE User_ID = NEW.User_ID;
    ELSIF NEW.Type = 'Withdrawal' THEN
        UPDATE Users
        SET Bank_Balance = Bank_Balance - NEW.Amount
        WHERE User_ID = NEW.User_ID;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_bank_balance_after_transaction
AFTER INSERT ON Transaction
FOR EACH ROW
EXECUTE FUNCTION update_user_bank_balance_after_transaction();

-- Trigger to apply rules after a transaction is created
CREATE OR REPLACE FUNCTION apply_savings_rules_after_transaction()
RETURNS TRIGGER AS $$
DECLARE
    rule RECORD;
    saved_amount DECIMAL(15,2);
BEGIN
    -- Check all active savings rules for the user of the transaction
    FOR rule IN
        SELECT Rule_ID, Rule_Type, Rule_Condition
        FROM Savings_Rule
        WHERE Account_ID = NEW.Account_ID AND Active = TRUE
    LOOP
        -- Apply the rule based on the rule type
        IF rule.Rule_Type = 'Round-Up' THEN
            -- Round-Up logic: round the transaction amount to the nearest whole number
            saved_amount := CEIL(NEW.Amount) - NEW.Amount;
        
        ELSIF rule.Rule_Type = 'Percentage' THEN
            -- Percentage logic: apply the percentage to the transaction amount
            saved_amount := NEW.Amount * (CAST(rule.Rule_Condition AS DECIMAL) / 100);
        
        ELSIF rule.Rule_Type = 'Fixed' THEN
            -- Fixed savings: apply a fixed amount (as defined in the rule)
            saved_amount := CAST(rule.Rule_Condition AS DECIMAL);
        END IF;
        
        -- Add the saved amount to the user's Savings Account
        UPDATE Savings_Account
        SET Balance = Balance + saved_amount
        WHERE Account_ID = NEW.Account_ID;
    END LOOP;
    
    -- Return the NEW transaction data
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach the trigger to the Transaction table
CREATE TRIGGER trigger_apply_savings_rules_after_transaction
AFTER INSERT ON Transaction
FOR EACH ROW
EXECUTE FUNCTION apply_savings_rules_after_transaction();







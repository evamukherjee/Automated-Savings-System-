CREATE OR REPLACE FUNCTION distribute_savings_to_goals()
RETURNS TRIGGER AS $$
DECLARE
    active_goal RECORD;
    active_goal_count INT;
    amount_per_goal DECIMAL(15,2);
    added_amount DECIMAL(15,2);
BEGIN
    -- Only proceed if balance increased
    IF NEW.Balance > OLD.Balance THEN
        added_amount := NEW.Balance - OLD.Balance;

        -- Count user's active goals
        SELECT COUNT(*) INTO active_goal_count
        FROM Savings_Goal
        WHERE User_ID = NEW.User_ID AND Status = 'Active';

        -- Only proceed if there are active goals
        IF active_goal_count > 0 THEN
            amount_per_goal := added_amount / active_goal_count;

            -- Loop through all active goals and update Saved_Amount
            FOR active_goal IN
                SELECT Goal_ID
                FROM Savings_Goal
                WHERE User_ID = NEW.User_ID AND Status = 'Active'
            LOOP
                UPDATE Savings_Goal
                SET Saved_Amount = Saved_Amount + amount_per_goal
                WHERE Goal_ID = active_goal.Goal_ID;

                -- Optionally: Immediately mark as completed if target met
                UPDATE Savings_Goal
                SET Status = 'Completed'
                WHERE Goal_ID = active_goal.Goal_ID
                  AND Saved_Amount >= Target_Amount
                  AND Status = 'Active';
            END LOOP;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_distribute_savings_to_goals
AFTER UPDATE ON Savings_Account
FOR EACH ROW
EXECUTE FUNCTION distribute_savings_to_goals();

DROP TRIGGER update_goal_status_when_target_met on Savings_Goal;
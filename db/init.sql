CREATE TABLE resources (
    r_id SERIAL PRIMARY KEY,
    r_name TEXT NOT NULL,
    r_cat TEXT
);

CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE bookings (
    b_id SERIAL PRIMARY KEY,
    b_r_id INT NOT NULL REFERENCES resources(r_id),
    b_user_id INT NOT NULL,
    b_time TSTZRANGE NOT NULL,
    b_status TEXT NOT NULL DEFAULT 'active',
    EXCLUDE USING gist (b_r_id WITH =, b_time WITH &&) WHERE (b_status = 'active')
);

CREATE TABLE status_history (
    st_id SERIAL PRIMARY KEY,
    st_b_id INT NOT NULL REFERENCES bookings(b_id),
    st_status_old TEXT,
    st_status_new TEXT,
    st_time TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE waitlist (
    w_id SERIAL PRIMARY KEY,
    w_r_id INT NOT NULL REFERENCES resources(r_id),
    w_user_id INT NOT NULL,
    w_time TSTZRANGE NOT NULL
);
--create TRIGGER auto_update_status_history
--select case
--when
--on insert or update on bookings b
--where new.b_staus != old.b_status
--then insert into status_history(b.b_id,old.b_status,new.b_status)
--end;

CREATE OR REPLACE FUNCTION log_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.b_status IS DISTINCT FROM OLD.b_status THEN
        INSERT INTO status_history (st_b_id, st_status_old, st_status_new)
        VALUES (NEW.b_id, OLD.b_status, NEW.b_status);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--
--CREATE TRIGGER trg_log_status_change
--AFTER UPDATE ON bookings
--FOR EACH ROW
--EXECUTE FUNCTION log_status_change();


--CREATE OR REPLACE FUNCTION log_status_change()
--RETURNS TRIGGER AS '
--BEGIN
--    IF NEW.b_status IS DISTINCT FROM OLD.b_status THEN
--        INSERT INTO status_history (st_b_id, st_status_old, st_status_new)
--        VALUES (NEW.b_id, OLD.b_status, NEW.b_status);
--    END IF;
--    RETURN NEW;
--END;
--' LANGUAGE plpgsql;

-- ============================================
-- POSTGRES TRIGGER + $$ + RETURN — QUICK NOTES
-- ============================================

-- $$ ... $$ : dollar-quoting, just an alternative to '...'
--   avoids escaping quotes inside long function bodies
--   (can tag it like $tag$...$tag$ to nest if needed)

-- LANGUAGE plpgsql : tells Postgres how to interpret the $$ string (as PL/pgSQL code)

-- RETURN is MANDATORY because function type = TRIGGER (PL/pgSQL enforces a return)

-- BEFORE trigger: return value = row that ACTUALLY gets written. It has real effect:
--   RETURN NEW;            -> save row as-is
--   RETURN NEW; (modified) -> whatever you changed in NEW gets saved instead (e.g. NEW.email := lower(NEW.email))
--   RETURN NULL;           -> cancels the INSERT/UPDATE entirely, nothing saved, no error
--   RETURN OLD;            -> discards the incoming change, keeps old row as-is

-- AFTER trigger (our case): row is ALREADY saved before trigger runs
--   whatever you RETURN is IGNORED by Postgres — pure syntax requirement, no real effect
--   only the actual logic inside (e.g. INSERT INTO status_history) does real work

-- HOW RETURN LINKS TO THE TRIGGER:
--   Postgres internally calls your function per row, auto-passing OLD/NEW
--   your RETURN value is the ONLY feedback channel back to Postgres's trigger engine
--   BEFORE: that feedback decides what gets written / whether to abort
--   AFTER:  feedback has nowhere to go (write already happened) -> discarded

-- FOR EACH ROW: trigger fires once per affected row (vs FOR EACH STATEMENT = once total)


CREATE TRIGGER trg_log_status_change
AFTER UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION log_status_change();




CREATE OR REPLACE FUNCTION promote()
RETURNS TRIGGER AS $$

DECLARE
    next_w RECORD;
BEGIN
    IF NEW.b_status IS DISTINCT FROM OLD.b_status AND NEW.b_status = 'cancelled' THEN

        SELECT * INTO next_w
        FROM waitlist
        WHERE w_r_id = OLD.b_r_id AND w_time = OLD.b_time
        ORDER BY w_id ASC
        LIMIT 1;

        IF FOUND THEN
            INSERT INTO bookings (b_r_id, b_user_id, b_time, b_status)
            VALUES (next_w.w_r_id, next_w.w_user_id, next_w.w_time, 'active');

            DELETE FROM waitlist WHERE w_id = next_w.w_id;
        END IF;

    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER wt_promotion
AFTER UPDATE on bookings
FOR EACH ROW
EXECUTE FUNCTION promote();

-- ============================================================
-- TEST DATA for Library System
-- ============================================================

-- ========================
-- USERS (password for all = "1234")
-- SHA256 of "1234" = 03ac67...
-- ========================
INSERT INTO users (first_name, last_name, email, password, negative_score, is_banned, last_login) VALUES
('Alice',   'Johnson',  'alice@test.com',   '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 0,  false, NOW()),
('Bob',     'Smith',    'bob@test.com',     '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 3,  false, NOW() - INTERVAL '2 hours'),
('Carol',   'Williams', 'carol@test.com',   '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 12, true,  NOW() - INTERVAL '1 day'),
('David',   'Brown',    'david@test.com',   '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 0,  false, NOW() - INTERVAL '10 minutes'),
('Emma',    'Davis',    'emma@test.com',    '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 0,  false, NOW() - INTERVAL '5 days');

-- NOTE: The hashed password above is a placeholder.
-- To get the real hash, run this in Python:
--   import hashlib; print(hashlib.sha256("1234".encode()).hexdigest())
-- Then replace all password values with the output.


-- ========================
-- BOOKS
-- ========================
INSERT INTO books (title, author, publisher, genre, publish_date, status, donor) VALUES
('The Great Gatsby',        'F. Scott Fitzgerald',  'Scribner',         'Fiction',     '1925', 'available', NULL),
('To Kill a Mockingbird',   'Harper Lee',           'J.B. Lippincott',  'Fiction',     '1960', 'available', NULL),
('1984',                    'George Orwell',         'Secker & Warburg', 'Dystopia',    '1949', 'borrowed',  NULL),
('Thinking Fast and Slow',  'Daniel Kahneman',      'Farrar Straus',    'Psychology',  '2011', 'available', 'alice@test.com'),
('The Power of Habit',      'Charles Duhigg',       'Random House',     'Psychology',  '2012', 'borrowed',  'alice@test.com'),
('Sapiens',                 'Yuval Noah Harari',    'Harper Collins',   'History',     '2011', 'available', 'david@test.com'),
('Clean Code',              'Robert C. Martin',     'Prentice Hall',    'Technology',  '2008', 'available', NULL),
('The Pragmatic Programmer','Andrew Hunt',           'Addison-Wesley',   'Technology',  '1999', 'available', NULL),
('Atomic Habits',           'James Clear',          'Avery Publishing', 'Self-Help',   '2018', 'available', 'alice@test.com'),
('Dune',                    'Frank Herbert',        'Chilton Books',    'Sci-Fi',      '1965', 'borrowed',  NULL);


-- ========================
-- BORROWS
-- (active borrows matching books with status='borrowed')
-- ========================
INSERT INTO borrows (user_email, book_title, return_deadline, status) VALUES
-- On time
('bob@test.com',   '1984',               NOW() + INTERVAL '1 minute',  'active'),
-- Overdue (to test late return penalty)
('david@test.com', 'The Power of Habit', NOW() - INTERVAL '3 minutes', 'active'),
-- Already returned (historical records for reports)
('alice@test.com', 'Sapiens',            NOW() - INTERVAL '1 day',     'returned'),
('bob@test.com',   'Atomic Habits',      NOW() - INTERVAL '2 days',    'returned'),
('emma@test.com',  'Clean Code',         NOW() - INTERVAL '3 days',    'returned'),
-- Borrow for the Dune book
('alice@test.com', 'Dune',               NOW() + INTERVAL '1 minute',  'active');


-- ========================
-- WAITING LIST
-- (someone waiting for a borrowed book)
-- ========================
INSERT INTO waiting_lists (user_email, book_title, joined_at) VALUES
('emma@test.com',  '1984',               NOW() - INTERVAL '5 minutes'),
('alice@test.com', 'The Power of Habit', NOW() - INTERVAL '2 minutes');


-- ========================
-- EXTRA BORROW HISTORY (to trigger reports)
-- Adds enough borrows to make Psychology genre hit 20+
-- and populate top books report
-- ========================
DO $$
DECLARE
    i INT;
    emails TEXT[] := ARRAY['alice@test.com','bob@test.com','david@test.com','emma@test.com'];
    psychology_books TEXT[] := ARRAY['Thinking Fast and Slow','The Power of Habit'];
    book TEXT;
    usr TEXT;
BEGIN
    FOR i IN 1..20 LOOP
        book := psychology_books[1 + (i % 2)];
        usr  := emails[1 + (i % 4)];
        INSERT INTO borrows (user_email, book_title, return_deadline, borrowed_at, returned_at, status)
        VALUES (usr, book, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '2 hours', NOW() - INTERVAL '30 minutes', 'returned');
    END LOOP;
END $$;
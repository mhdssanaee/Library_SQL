-- CREATE DATABASE library_db


-- CREATE TABLE IF NOT EXISTS public.books
-- (
--     title character varying(255) COLLATE pg_catalog."default" NOT NULL,
--     author character varying(255) COLLATE pg_catalog."default",
--     publisher character varying(255) COLLATE pg_catalog."default",
--     genre character varying(100) COLLATE pg_catalog."default",
--     publish_date character varying(50) COLLATE pg_catalog."default",
--     status character varying(50) COLLATE pg_catalog."default" DEFAULT 'available'::character varying,
--     donor character varying(255) COLLATE pg_catalog."default",
--     CONSTRAINT books_pkey PRIMARY KEY (title)
-- )



-- CREATE TABLE IF NOT EXISTS public.borrows
-- (
--     id integer NOT NULL DEFAULT nextval('borrows_id_seq'::regclass),
--     user_email character varying(255) COLLATE pg_catalog."default" NOT NULL,
--     book_title character varying(255) COLLATE pg_catalog."default" NOT NULL,
--     borrowed_at timestamp without time zone DEFAULT now(),
--     return_deadline timestamp without time zone NOT NULL,
--     returned_at timestamp without time zone,
--     status character varying(20) COLLATE pg_catalog."default" DEFAULT 'active'::character varying,
--     CONSTRAINT borrows_pkey PRIMARY KEY (id),
--     CONSTRAINT fk_book FOREIGN KEY (book_title)
--         REFERENCES public.books (title) MATCH SIMPLE
--         ON UPDATE NO ACTION
--         ON DELETE CASCADE,
--     CONSTRAINT fk_user FOREIGN KEY (user_email)
--         REFERENCES public.users (email) MATCH SIMPLE
--         ON UPDATE NO ACTION
--         ON DELETE CASCADE
-- )



-- CREATE TABLE IF NOT EXISTS public.users
-- (
--     email character varying(255) COLLATE pg_catalog."default" NOT NULL,
--     first_name character varying(100) COLLATE pg_catalog."default",
--     last_name character varying(100) COLLATE pg_catalog."default",
--     password character varying(255) COLLATE pg_catalog."default",
--     negative_score integer DEFAULT 0,
--     is_banned boolean DEFAULT false,
--     last_login timestamp without time zone DEFAULT now(),
--     CONSTRAINT users_pkey PRIMARY KEY (email)
-- )




-- CREATE TABLE IF NOT EXISTS public.waiting_lists
-- (
--     id integer NOT NULL DEFAULT nextval('waiting_lists_id_seq'::regclass),
--     book_title character varying(255) COLLATE pg_catalog."default" NOT NULL,
--     user_email character varying(255) COLLATE pg_catalog."default" NOT NULL,
--     joined_at timestamp without time zone DEFAULT now(),
--     CONSTRAINT waiting_lists_pkey PRIMARY KEY (id),
--     CONSTRAINT fk_wait_book FOREIGN KEY (book_title)
--         REFERENCES public.books (title) MATCH SIMPLE
--         ON UPDATE NO ACTION
--         ON DELETE CASCADE,
--     CONSTRAINT fk_wait_user FOREIGN KEY (user_email)
--         REFERENCES public.users (email) MATCH SIMPLE
--         ON UPDATE NO ACTION
--         ON DELETE CASCADE
-- )


--Скрипт обновления и первичного наполения БД
SELECT (
   			SELECT count(1)
   			FROM   information_schema.tables 
   			WHERE  table_schema = 'public'
   			AND    table_name = 'version'
)=0 as table_exists;
\gset
\if :table_exists
	\i 'create.sql'
	\echo 'DB schema created'
\endif

-- --Мигарция 1
-- SELECT (select count(*) from public.version)=0 as migrate
-- \gset
-- \if :migrate
-- 	BEGIN;
-- 		--здесь сама миграция
		
-- 		--обновляем номер версии на следующий
-- 		INSERT INTO public.version(version) VALUES(1);
-- 	COMMIT;
-- 	\echo 'Migration 1 done'
-- \endif

-- --Мигарция 2
-- SELECT (select version from public.version)=1 as migrate 
-- \gset
-- \if :migrate
-- 	BEGIN;
-- 		--здесь сама миграция

-- 		--обновляем номер версии на следующий
-- 		UPDATE public.version SET version=2;
-- 	COMMIT;
-- 	\echo 'Migration 2 done'
-- \endif

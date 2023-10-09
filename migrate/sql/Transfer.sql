with stg1 as (
	select
	distinct careunit as careunit
	from mimiciv.transfers
	where careunit is not null
)
select
-- uuid_generate_v4() as id,
('LOC' || LPAD((row_number() OVER ())::text, 3, '0')) as id,
careunit as careunit
from
stg1

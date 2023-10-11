select
(case when per.person_id::text like '-%' then 'm' || substr(per.person_id::text, 2) else 'p' || per.person_id end) as id,
lower(con.concept_name) as gender
from
omop_test_20220817.person per
inner join omop_test_20220817.concept con
on con.concept_id = per.gender_concept_id
inner join omop_test_20220817.micro_cohort coh
on coh.person_id = per.person_id
;

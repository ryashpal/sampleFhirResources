select
(case when vo.visit_occurrence_id::text like '-%' then 'm' || substr(vo.visit_occurrence_id::text, 2) else 'p' || vo.visit_occurrence_id end) as id,
(
    case when vo.admitting_source_concept_id is null then 'outpatient' else 
    (
        case when vo.admitting_source_concept_id = 0 then 'outpatient' else 'inpatient' end
    ) end
) as code,
'Patient/' || (case when vo.person_id::text like '-%' then 'm' || substr(vo.person_id::text, 2) else 'p' || vo.person_id end) as person_id,
to_char(vo.visit_start_datetime, 'DD-MM-YYYY') || 'T' || to_char(vo.visit_start_datetime, 'HH24:MI:SS') as visit_start_datetime,
to_char(vo.visit_end_datetime, 'DD-MM-YYYY') || 'T' || to_char(vo.visit_end_datetime, 'HH24:MI:SS') as visit_end_datetime
from
omop_test_20220817.visit_occurrence vo
inner join omop_test_20220817.micro_cohort coh
on coh.visit_occurrence_id = vo.visit_occurrence_id
limit 5
;

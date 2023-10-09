select
trn.careunit,
to_char(trn.intime, 'DD-MM-YYYY') || 'T' || to_char(trn.intime, 'HH24:MI:SS') as intime,
to_char(trn.outtime, 'DD-MM-YYYY') || 'T' || to_char(trn.outtime, 'HH24:MI:SS') as outtime
from
omop_test_20220817.visit_occurrence vo
inner join mimiciv.admissions adm
on adm.hadm_id::text = split_part(vo.visit_source_value, '|', 2)
inner join mimiciv.transfers trn
on trn.hadm_id = adm.hadm_id
where vo.visit_occurrence_id='{}' and trn.careunit is not null
;

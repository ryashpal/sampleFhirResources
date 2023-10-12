update omop_test_20220817.measurement_fhir set
measurement_concept_id = %(measurement_concept_id)s,
person_id = (case when split_part(%(person_id)s, '/', 2) like 'm%%' then '-' || substr(split_part(%(person_id)s, '/', 2), 2) else substr(split_part(%(person_id)s, '/', 2), 2) end)::int,
visit_occurrence_id = (case when split_part(%(visit_occurrence_id)s, '/', 2) like 'm%%' then '-' || substr(split_part(%(visit_occurrence_id)s, '/', 2), 2) else substr(split_part(%(visit_occurrence_id)s, '/', 2), 2) end)::int,
measurement_datetime = to_timestamp(split_part(%(measurement_datetime)s, 'T', 1) || ' ' || split_part(%(measurement_datetime)s, 'T', 2),'YYYY-MM-DD HH24:MI:SS'),
unit_concept_id = %(unit_concept_id)s,
value_as_number = %(value_as_number)s
where measurement_id = %(id)s
;

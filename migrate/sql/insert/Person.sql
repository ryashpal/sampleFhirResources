update omop_test_20220817.person set gender_concept_id = (
    select concept_id from omop_test_20220817.concept where vocabulary_id = 'Gender' and lower(concept_name) = %(gender)s
) where per.person_id = %(id)s
